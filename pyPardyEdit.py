#! /usr/bin/env python3

"""
pyPardy Editor

Editor to edit round data files for pyPardy.

@author: Christian Wichmann
"""

import logging
import logging.handlers
import sys

from PyQt4 import QtGui
from PyQt4 import QtCore

from data import round
from data import config
import data.game
from gui import helper
from gui import game


class AvailableRoundPanel(QtGui.QMainWindow):
    """Panel showing all available rounds."""
    def __init__(self, parent, width, height):
        """Initialize panel for displaying all available rounds."""
        super(AvailableRoundPanel, self).__init__(parent)
        self.setFixedSize(width, height)
        self.WIDTH = width
        self.HEIGHT = height
        self.create_fonts()
        self.setup_ui()
        self.set_signals_and_slots()
        self.current_game = data.game.Game()

    def create_fonts(self):
        if config.LOW_RESOLUTION:
            self.title_font = QtGui.QFont(config.BASE_FONT)
            self.title_font.setPointSize(18)
            self.button_font = QtGui.QFont(config.BASE_FONT)
            self.button_font.setPointSize(14)
        else:
            self.title_font = QtGui.QFont(config.BASE_FONT)
            self.title_font.setPointSize(30)
            self.button_font = QtGui.QFont(config.BASE_FONT)
            self.button_font.setPointSize(20)
            
    def setup_ui(self):
        self.resize(self.WIDTH, self.HEIGHT)
        self.setWindowTitle(config.APP_NAME)
        self.setWindowIcon(QtGui.QIcon('icons/buzzer.png'))
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.main_widget = QtGui.QWidget()
        self.button_box = QtGui.QVBoxLayout()
        margin = 25
        self.button_box.setContentsMargins(margin, margin, margin, margin)
        # add title label
        title_label = QtGui.QLabel(config.APP_NAME)
        title_label.setFont(self.title_font)
        title_label.setAlignment(QtCore.Qt.AlignCenter |
                                 QtCore.Qt.AlignHCenter)
        self.button_box.addWidget(title_label)
        self.button_box.addStretch(2)
        # add buttons for all available rounds
        data = round.get_available_round_data()
        for title, filename in data:
            new_button = QtGui.QPushButton(title)
            new_button.title = title
            new_button.filename = filename
            new_button.resize(new_button.sizeHint())
            new_button.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                     QtGui.QSizePolicy.Expanding)
            if config.HIGH_CONTRAST:
                helper.whitefy(new_button)
            new_button.setFont(self.button_font)
            new_button.clicked.connect(self.on_button_click)
            self.button_box.addWidget(new_button)
            self.button_box.addStretch(1)
        # add button for quitting application
        quit_button = QtGui.QPushButton()
        quit_button.setText('Beenden')
        quit_button.setFont(self.button_font)
        quit_button.clicked.connect(self.close)
        self.button_box.addStretch(1)
        self.button_box.addWidget(quit_button)
        # add space after all buttons are inserted
        self.button_box.addStretch(10)
        # put vbox into hbox to center horizontally
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(self.button_box)
        hbox.addStretch(1)
        self.main_widget.setLayout(hbox)
        # set central widget for main window
        self.setCentralWidget(self.main_widget)

    def set_signals_and_slots(self):
        """Sets all signals and slots for main window."""
        pass

    @QtCore.pyqtSlot()
    def on_button_click(self):
        filename_to_load = self.sender().filename
        logger.info('File "{}" should be loaded...'.format(filename_to_load))
        self.current_game.current_round_data = round.load_round_data_file(filename_to_load)
        # create new question table and connect it to method of this class
        self.current_round_question_panel = game.QuestionTablePanel(self, self.current_game,
                                                                    self.WIDTH, self.HEIGHT, False)
        self.current_round_question_panel.question_button_pressed.connect(self.show_edit_dialog)
        self.setCentralWidget(self.current_round_question_panel)
        # TODO Add exit button to get back to menu!

    def show_edit_dialog(self, question, topic):
        logger.info('Edit question: ' + str(question) + '-' + str(topic))


def create_logger():
    """Creates logger for this application."""
    LOG_FILENAME = 'pyPardy.log'
    logger = logging.getLogger('pyPardyEdit')
    logger.setLevel(logging.DEBUG)
    log_to_file = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                                       maxBytes=262144,
                                                       backupCount=5)
    log_to_file.setLevel(logging.DEBUG)
    logger.addHandler(log_to_file)
    log_to_screen = logging.StreamHandler(sys.stdout)
    log_to_screen.setLevel(logging.INFO)
    logger.addHandler(log_to_screen)
    return logger


if __name__ == '__main__':
    logger = create_logger()
    logger.info('Starting pyPardyEdit...')   
    config.load_config_from_file()
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    main = AvailableRoundPanel(None, 1024, 768)
    main.show()
    app.exec_()
