
"""
pyPardy

Helper classes for the gui of pyPardy.

@author: Christian Wichmann
"""

import logging
from PyQt4 import QtCore

from buzzer import buzzer


logger = logging.getLogger('pyPardy.gui')


class BuzzerConnector(QtCore.QObject):
    """Connects the buzzer API throught a callback with the QT gui over a new
    signal that is emitted when a buzzer is pressed.
    """
    # define a QT signal to react on buzzer presses
    buzzing = QtCore.pyqtSignal(int)

    def __init__(self):
        super(BuzzerConnector, self).__init__()
        # install callback for buzzer API
        self.buzzer_reader = buzzer.BuzzerReader(self.on_buzzer_pressed)

    #def __del__(self):
    #    self.buzzer_reader.stop()

    def on_buzzer_pressed(self, buzzer_id):
        self.buzzing.emit(buzzer_id)
