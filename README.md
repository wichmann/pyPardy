pyPardy
=======

DESCRIPTION
-----------
pyPardy is a game similar to Jeopardy(tm). To be used with pardyBuzz game show buzzer [1].

[1] http://github.com/erebos42/pardyBuzz


KNOWN PROBLEMS AND BUGS
-----------------------


LICENSE
-------
pyPardy is released under the GNU General Public License v2 or newer.


REQUIREMENTS
------------
pyPardy requires at least Python 3.3. It requires also PyQt4 and PyQt4.phonon.

For the correct rendering the font "Linux Biolinum O" has to be installed.

To use the USB buzzer, libusb version 1.0 and the wrapper python-libusb1 have
to be installed. The file '10-buzzer.rules' contains a udev rule to access the
usb device without root access. Just copy it to /etc/udev/rules.d and change
the GROUP attribute to your needs.

Under Micorsoft Windows you have to install the generic USB driver first (see
https://github.com/libusb/libusb/wiki/Windows). The drivers INF file can be
found in this repositories windows/ directory. Just go to the Device Manager
and choose the INF file as new driver.

Next you have to copy the file libusb.dll into "C:\Windows\SysWOW64". This
version contains experimental support for USB-HotPlug under Windows and was
compiled from [2] as 32bit DLL with Visual Studio 2012 under Windows 7 64bit.

[2] http://github.com/dickens/libusbx-hp/commit/6cba5d96767b205fc653e3273fba81b59f1e1492


THIRD PARTY SOFTWARE
--------------------
pyPardy includes parts of or links with the following software packages and 
programs, so give the developers lots of thanks sometime! 

* PyQt, Phonon, Qt under GPL or LGPL license.
* libusb under LGPL license.
* python-libusb1 binding under GPL license.
* Some cliparts from opencliparts.org: 
   - http://openclipart.org/detail/190592/button-by-tobbi-190592
* Some free sound files:
   - https://www.freesound.org/people/hypocore/sounds/164089/
   - http://soundbible.com/1491-Zen-Buddhist-Temple-Bell.html
