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
        self.last_loaded_file = self.sender().filename
        logger.info('Round data file "{}" loaded.'.format(self.last_loaded_file))
        self.current_game.current_round_data = round.load_round_data_file(self.last_loaded_file)
        # create new question table and connect it to method of this class
        self.current_round_question_panel = game.QuestionTablePanel(self, self.current_game,
                                                                    self.WIDTH, self.HEIGHT, False)
        self.current_round_question_panel.question_button_pressed.connect(self.show_edit_dialog)
        self.setCentralWidget(self.current_round_question_panel)
        # TODO Add exit button to get back to menu!

    @QtCore.pyqtSlot(int, int)
    def show_edit_dialog(self, topic, question):
        """Opens up a new dialog to edit a question."""
        logger.info('Edit question: {} from topic {}.'.format(question, topic))
        dialog = EditQuestionDialog(self, self.current_game.current_round_data,
                                    topic, question)
        dialog.exec_()
        if dialog.data_has_changed:
            logger.info('Round data saved to file.')
            round.save_round_data_file(self.last_loaded_file,
                                       self.current_game.current_round_data)


class EditQuestionDialog(QtGui.QDialog):
    """Panel showing all available rounds.

    :param data: round data qith the question that should be edited
    :param topic: number of the topic that should be edited
    :param question: number of question of the given that should be edited
    """
    def __init__(self, parent, data, topic, question):
        """Initialize a new dialog box for editing a question."""
        super(EditQuestionDialog, self).__init__(parent)
        self.data = data
        self.topic = topic
        self.question = question
        self.data_has_changed = False
        self.create_fonts()
        self.setup_ui()
        self.set_signals_and_slots()

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
        self.setWindowTitle(config.APP_NAME + ' - Frage editieren...')
        self.setWindowIcon(QtGui.QIcon('icons/buzzer.png'))
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.layout = QtGui.QGridLayout()
        margin = 10
        self.layout.setSpacing(margin)
        # extract correct question data from round data        
        question_data = self.data['topics'][self.topic]['questions'][self.question]        
        topic_text = self.data['topics'][self.topic]['title']
        question_text = (self.question + 1) * config.QUESTION_POINTS
        # add title for dialog (and remove line breaks in topic names!)
        title_text = '{} - {}'.format(topic_text, question_text).replace('<br>', '')
        title_label = QtGui.QLabel(title_text)
        title_label.setFont(self.title_font)
        title_label.setWordWrap(False)
        self.layout.addWidget(title_label, 0, 0, 1, 2, QtCore.Qt.AlignHCenter)
        # add text fields for question and answer
        self.layout.addWidget(QtGui.QLabel('Frage: '), 1, 0, QtCore.Qt.AlignTop)
        self.question_text_field = QtGui.QTextEdit()
        self.question_text_field.setText(question_data['question'])
        self.question_text_field.setMaximumHeight(75)
        self.layout.addWidget(self.question_text_field, 1, 1)
        self.layout.addWidget(QtGui.QLabel('Antwort: '), 2, 0, QtCore.Qt.AlignTop)
        self.answer_text_field = QtGui.QTextEdit()
        self.answer_text_field.setText(question_data['answer'])
        self.answer_text_field.setMaximumHeight(75)
        self.layout.addWidget(self.answer_text_field, 2, 1)
        # add close button
        self.button_box = QtGui.QHBoxLayout()
        self.cancel_button = QtGui.QPushButton()
        self.cancel_button.setText('Abbrechen')
        self.button_box.addWidget(self.cancel_button)
        self.ok_button = QtGui.QPushButton()
        self.ok_button.setText('OK')
        self.button_box.addWidget(self.ok_button)
        self.layout.addLayout(self.button_box, 3, 1)
        self.setLayout(self.layout)

    def set_signals_and_slots(self):
        """Sets all signals and slots for edit dialog."""
        self.cancel_button.clicked.connect(lambda: self.on_close(False))
        self.ok_button.clicked.connect(lambda: self.on_close(True))

    @QtCore.pyqtSlot()
    def on_close(self, save_data):
        """Handles click on either the cancel or the ok button. Depending on
        the value of the parameter save_data the changed data will be saved."""
        # save data
        if save_data:
            self.data_has_changed = True
            question_data = self.data['topics'][self.topic]['questions'][self.question]
            # use method 'toHtml()' to get line breaks from text fields
            text = self.question_text_field.toPlainText().replace('\n', '<br>')
            question_data['question'] = text
            text = self.answer_text_field.toPlainText().replace('\n', '<br>')
            question_data['answer'] = text
        # close dialog
        self.close()

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
    # load and adjust config settings
    config.load_config_from_file()
    config.APP_NAME = 'pyPardyEdit'
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    main = AvailableRoundPanel(None, 1024, 768)
    main.show()
    app.exec_()
