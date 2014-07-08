
"""
pyPardy

Helper classes for the gui of pyPardy.

@author: Christian Wichmann
"""

import logging
import time

from PyQt4 import QtCore
from PyQt4 import QtGui

from buzzer import buzzer


logger = logging.getLogger('pyPardy.gui')


# duration for the animation of widgets
ANIMATION_TIME = 750
# singleton instance that is returned by get_buzzer_connector() function
STATIC_INSTANCE_OF_BUZZER_CONNECTOR = None
# whether to debounce buzzers
DEBOUNCE_BUZZER = True
# debounce interval in s
DEBOUNCE_INTERVAL = 0.500


# list of all animation objects
animation_list = []


class BuzzerConnector(QtCore.QObject):
    """Connects the buzzer API throught a callback with the QT gui over a new
    signal that is emitted when a buzzer is pressed.

    This class should NEVER be manually instanciated! For getting a new
    BuzzerConnector the module-level function get_buzzer_connector() should
    be used.

    By using the constants DEBOUNCE_BUZZER and DEBOUNCE_INTERVAL it is possible
    to define the behaviour of the connected buzzers. If DEBOUNCE_BUZZER is
    True a signal from the buzzer will only emitted when the current buzzer id
    is different than the last buzzed id or the given interval is elapsed!

    NOTE: Debouncing uses time.monotonic() which is only part of Python since
    version 3.3!
    """
    # define a QT signal to react on buzzer presses
    buzzing = QtCore.pyqtSignal(int)

    def __init__(self):
        super(BuzzerConnector, self).__init__()
        # install callback for buzzer API
        self.buzzer_reader = buzzer.BuzzerReader(self.on_buzzer_pressed)
        self.last_buzzer_id = -1
        self.last_buzzer_time = 0

    def __del__(self):
        self.buzzer_reader.stop()

    def close_connection(self):
        self.buzzer_reader.stop()
        self.buzzer_reader.join()
        del self.buzzer_reader

    def flush_connection(self):
        self.last_buzzer_id = -1
        self.buzzer_reader.flush_all_devices()

    def on_buzzer_pressed(self, buzzer_id):
        if DEBOUNCE_BUZZER:
            # get current time and check if DEBOUNCE_INTERVAL has elapsed
            current_time = time.monotonic()
            time_difference = current_time - self.last_buzzer_time
            print('{}, {}'.format(current_time, time_difference))
            if buzzer_id != self.last_buzzer_id or time_difference > DEBOUNCE_INTERVAL:
                self.last_buzzer_time = current_time
                self.last_buzzer_id = buzzer_id
                self.buzzing.emit(buzzer_id)
        else:
            self.buzzing.emit(buzzer_id)


def get_buzzer_connector():
    global STATIC_INSTANCE_OF_BUZZER_CONNECTOR
    if not STATIC_INSTANCE_OF_BUZZER_CONNECTOR:
        STATIC_INSTANCE_OF_BUZZER_CONNECTOR = BuzzerConnector()
    return STATIC_INSTANCE_OF_BUZZER_CONNECTOR


##### Miscellaneous functions for GUI

def center_on_screen(window):
    """Centers the window on the screen."""
    screen = QtGui.QDesktopWidget().screenGeometry()
    size = window.geometry()
    window.move((screen.width() - size.width()) / 2,
                (screen.height() - size.height()) / 2)


##### Functions for animating, hiding and showing widgets with opaycity effects

def animate_widget(widget, fade_out, hook=None):
    """Creates an opacity effect for the question label and fades it in or
    out.

    Per default JLabel has no property 'opacity' so that QPropertyAnimation
    can not be used without adding a graphics effect from the QT library
    (QGraphicsOpacityEffect).

    :param widget: widget that should be faded out or in
    :param fade_out: whether to fade out or in
    :param hook: method that should be called when animation is over
    """
    # set start and stop opacity
    if fade_out:
        start_value = 1.0
        stop_value = 0.0
    else:
        start_value = 0.0
        stop_value = 1.0
    # generate effect class
    effect = QtGui.QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    # fade question in/out
    anim = QtCore.QPropertyAnimation(effect, "opacity")
    anim.setDuration(ANIMATION_TIME)
    anim.setStartValue(start_value)
    anim.setEndValue(stop_value)
    anim.setEasingCurve(QtCore.QEasingCurve.InOutBack)
    ###
    # Add currently constructed animation object to list of all animations
    # so that they are not destroyed when this method is through. After the
    # animation has run the objects can live happily ever after in the
    # list!
    ###
    global animation_list
    animation_list.append(anim)
    anim.start()
    if hook:
        anim.finished.connect(hook)


def hide_widget(widget):
    # generate effect class
    effect = QtGui.QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    # set opacity
    effect.setOpacity(0.0)


def show_widget(widget):
    # generate effect class
    effect = QtGui.QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    # set opacity
    effect.setOpacity(1.0)
