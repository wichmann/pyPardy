#!/usr/bin/env python3

"""
This module handles all low level USB access. To use this just create an
instance of BuzzerReader with a callback as an argument.
"""

import threading
import platform
import time
import usb1
import libusb1
import logging


logger = logging.getLogger('pyPardy.buzzer')


# setting or getting device_id:
#
#    def search_device(context):
#        for device in context.getDeviceList():
#            if (device.getVendorID() == USBDEV_VENDOR and
#                device.getProductID() == USBDEV_PRODUCT):
#                return device
#        return None
#
#    dev = search_device(context)
#    bd = BuzzerDevice(dev)
#    bd.set_device_id(0x01)
#    del bd


# Shared VID/PID for buzzers (see also V-USB)
USBDEV_VENDOR       = 0x16C0
USBDEV_PRODUCT      = 0x05DC
# Magic byte, that is send by the buzzer
BUZZER_MAGIC_MARKER = 0xa5
# Interface to claim
INTERFACE = 0
# timeout for USB connection
USB_TIMEOUT = 250


class BuzzerDevice(threading.Thread):
    """Represents one Buzzer. Is a thread, that calls 'callback', everytime
       the Buzzer gets pressed.
    """
    def __init__(self, dev, callback):
        super().__init__()
        self.__device = dev
        self.__handle = self.open_device(dev)
        self.__device_id = 0x00
        self.__device_id_dirty = True
        self.__keep_running = True
        self.__callback = callback

    def __del__(self):
        """Make sure the thread is stopped and the device is closed."""
        self.__keep_running = False
        try:
            # close device only if still available
            self.__device.getDeviceAddress()
            self.close_device()
        except libusb1.USBError:
            pass

    def run(self):
        while(self.__keep_running):
            if self.read_interrupt():
                try:
                    self.__callback(self.get_device_id())
                except libusb1.USBError:
                    logger.error('Could not get device id!')

    def stop(self):
        self.__keep_running = False

    def open_device(self, dev):
        handle = dev.open()
        if platform.system() == 'Linux' and handle.kernelDriverActive(INTERFACE):
            handle.detachKernelDriver(INTERFACE)
        handle.claimInterface(INTERFACE)
        return handle

    def close_device(self):
        self.__handle.releaseInterface(INTERFACE)
        self.__handle.close()

    def set_device_id(self, device_id):
        self.__device_id_dirty = True
        self.__device_id = device_id
        self.__handle.controlRead(libusb1.LIBUSB_TYPE_VENDOR |
                                  libusb1.LIBUSB_RECIPIENT_DEVICE |
                                  libusb1.LIBUSB_ENDPOINT_IN,
                                  0, int(device_id), 0, 1, timeout=USB_TIMEOUT)

    def get_device_id(self):
        """Returns Buzzer ID. uses a dirty flag, to prevent unnecessary USB
        reads.
        """
        if self.__device_id_dirty:
            ret = self.__handle.controlRead(libusb1.LIBUSB_TYPE_VENDOR |
                                            libusb1.LIBUSB_RECIPIENT_DEVICE |
                                            libusb1.LIBUSB_ENDPOINT_IN,
                                            0, 0x00, 0, 1, timeout=USB_TIMEOUT)
            self.__device_id = int(ret[0])
            self.__device_id_dirty = False
        return self.__device_id

    def get_device(self):
        return self.__device

    def read_interrupt(self, timeout=USB_TIMEOUT):
        """Read the USB Interrupt Endpoint. Blocks until byte is read or
        timeout.
        """
        try:
            temp = int(self.__handle.interruptRead(endpoint=1, length=1,
                                                   timeout=timeout)[0])
            if temp == BUZZER_MAGIC_MARKER:
                return True
            else:
                raise libusb1.USBError('Wrong buzzer marker!')
        except libusb1.USBError:
            return False
        return False

    def flush_interrupt_data(self):
        """A pressed button is 'stored' in the device and may need to get
        flushed, before a real value can be read.
        """
        self.read_interrupt()


class BuzzerReader(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.__callback = callback
        self.__device_list = []
        self.__context = self.init_context()
        self.__context.hotplugRegisterCallback(self.callback_device_left,
                                               events=libusb1.LIBUSB_HOTPLUG_EVENT_DEVICE_LEFT,
                                               vendor_id=USBDEV_VENDOR, product_id=USBDEV_PRODUCT)
        self.__context.hotplugRegisterCallback(self.callback_device_arrived,
                                               events=libusb1.LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED,
                                               vendor_id=USBDEV_VENDOR, product_id=USBDEV_PRODUCT)
        self.__keep_running = True
        self.daemon = True
        self.start()

    def stop(self):
        self.__keep_running = False

    def run(self):
        try:
            while True:
                self.__context.handleEvents()
        except (KeyboardInterrupt, SystemExit):
            pass
        self.__context.exit()

    def init_context(self):
        context = usb1.USBContext()
        if not context.hasCapability(libusb1.LIBUSB_CAP_HAS_HOTPLUG):
            print('Hotplug support is missing. Please update your libusb version.')
        return context

    def callback_device_arrived(self, context, device, event):
        """Hotplug callback for device arrival. Gets called for every existing
        device at the start.
        """
        bd = BuzzerDevice(device, self.__callback)
        self.__device_list.append(bd)
        bd.daemon = True
        bd.start()
        # return False, to *not* cancel the callback
        return False

    def callback_device_left(self, context, device, event):
        """Hotplug callback for device removal."""
        for d in self.__device_list:
            # check which device was removed - the device address is assigned
            # by the os and should be pretty unique. I think...
            if device.getDeviceAddress() == d.get_device().getDeviceAddress():
                d.stop()
                self.__device_list.remove(d)
        # return False, to *not* cancel the callback
        return False

    def flush_all_devices(self):
        for d in self.__device_list:
            d.flush_interrupt_data()


class BuzzerReaderPoller(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.__callback = callback
        self.__devices_already_registered = {}
        self.__context = self.init_context()
        self.__keep_running = True
        self.daemon = True
        self.start()

    def stop(self):
        self.__keep_running = False

    def run(self):
        try:
            while True:
                self.check_for_new_devices()
                # stop for half a second before checking again
                time.sleep(0.5)
        except (KeyboardInterrupt, SystemExit):
            pass
        self.__context.exit()

    def check_for_new_devices(self):
        # check for new devices
        newly_found_devices = {}
        found_devices = []
        for device in self.__context.getDeviceList():
            if (device.getVendorID() == USBDEV_VENDOR and
                device.getProductID() == USBDEV_PRODUCT):
                bus_id = device.getBusNumber()
                device_address = device.getDeviceAddress()
                x = (bus_id, device_address)
                if x not in self.__devices_already_registered:
                    print('New buzzer: {}'.format(x))
                    bd = BuzzerDevice(device, self.__callback)
                    bd.daemon = True
                    bd.start()
                    newly_found_devices[x] = bd
                found_devices.append(x)
        # delete old devices that are not there anymore
        list_of_old_devices = []
        for key, device in self.__devices_already_registered.items():
            if key not in found_devices:
                self.__devices_already_registered[key].stop()
                list_of_old_devices.append(key)
        for device in list_of_old_devices:
            print('Deleting old device {}.'.format(device))
            del self.__devices_already_registered[device]
        self.__devices_already_registered.update(newly_found_devices)

    def init_context(self):
        context = usb1.USBContext()
        #if not context.hasCapability(libusb1.LIBUSB_CAP_HAS_HOTPLUG):
        #    print('Hotplug support is missing. Please update your libusb version.')
        return context

    def flush_all_devices(self):
        for k, d in self.__devices_already_registered.items():
            d.flush_interrupt_data()


if __name__ == '__main__':
    def callback(buzzer_id):
        print(buzzer_id)
    BuzzerReaderPoller(callback)
