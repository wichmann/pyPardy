
"""
pyPardy

Main window of pyPardy

@author: Christian Wichmann
"""

import logging

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.phonon import Phonon

from data import round
from data import game
from data import config

from gui import game as game_ui
from gui import admin
from gui import helper


__all__ = ['start_gui']


logger = logging.getLogger('pyPardy.gui')


class PyPardyGui(QtGui.QMainWindow):
    """Main window for pyPardy"""
    def __init__(self, parent=None):
        """Initialize main window for pyPardy."""
        logger.info('Building main window of pyPardy...')
        QtGui.QMainWindow.__init__(self, parent)
        self.set_window_size()
        # define all panels that are used inside the QStackedWidget
        self.available_rounds_panel = None
        self.current_round_question_panel = None
        self.current_question_panel = None
        self.current_game = None
        self.buzzer_config_panel = None
        # build and config all widgets
        self.setup_ui()
        helper.center_on_screen(self)
        self.set_signals_and_slots()
        # create instance of Game class for saving all necessary data
        self.current_game = game.Game()
        self.init_audio()

    # FIXME Handle game ending and release all resources from buzzer API!
    def __del__(self):
        pass

    def set_window_size(self):
        if config.FULLSCREEN:
            resolution = QtGui.QDesktopWidget().screenGeometry()
            self.WIDTH = resolution.width()
            self.HEIGHT = resolution.height()
            self.showFullScreen()
        else:
            self.WIDTH = 1024
            self.HEIGHT = 768

    def setup_ui(self):
        """Initializes the UI by displaying all available rounds."""
        # set size of window
        self.resize(self.WIDTH, self.HEIGHT)
        self.setWindowTitle(config.APP_NAME)
        self.setWindowIcon(QtGui.QIcon('icons/buzzer.png'))
        # build stacked widget for all current and coming panels
        self.stackedWidget = QtGui.QStackedWidget()
        self.stackedWidget.setFixedSize(self.WIDTH, self.HEIGHT)
        self.show_available_rounds_panel()
        # set central widget for main window
        self.setCentralWidget(self.stackedWidget)

    def set_signals_and_slots(self):
        """Sets all signals and slots for main window."""
        pass

    def init_audio(self):
        # create game end sound object
        self.audio_output = Phonon.AudioOutput(Phonon.MusicCategory)
        self.game_end_sound = Phonon.MediaObject()
        Phonon.createPath(self.game_end_sound, self.audio_output)
        self.game_end_sound.setCurrentSource(Phonon.MediaSource('./sounds/temple_bell.wav'))

    ##### slot methods #####

    @QtCore.pyqtSlot()
    def on_click_something(self):
        logger.info('Loading file...')

    ##### methods creating and selecting panels within QStackedWidget #####

    def show_round_table(self, filename):
        # save filename in Game class
        self.current_game.filename = filename
        # load round data from file
        self.current_game.current_round_data = round.load_round_data_file(filename)
        # remove old question table if it exists
        if self.current_round_question_panel:
            self.stackedWidget.removeWidget(self.current_round_question_panel)
        # create new question table and connect it to method of this class
        self.current_round_question_panel = game_ui.QuestionTablePanel(self, self.current_game,
                                                                       self.WIDTH, self.HEIGHT)
        self.current_round_question_panel.question_button_pressed.connect(self.show_question)
        self.stackedWidget.addWidget(self.current_round_question_panel)
        self.stackedWidget.setCurrentWidget(self.current_round_question_panel)

    def back_to_round_table(self):
        """Handles the transition from question view panel back to the table
        with all questions of the round."""
        # show the rounds question table
        self.stackedWidget.setCurrentWidget(self.current_round_question_panel)
        self.current_round_question_panel.update_widgets()
        # remove old question view widget
        if self.current_question_panel:
            self.current_question_panel = None
            #del self.current_question_panel
        # handle end of round
        if self.current_game.is_round_complete():
            logger.info('Round was completed.')
            self.round_complete()

    def quit_round(self):
        self.current_game.quit_round()
        if config.AUDIO_SFX:
            self.game_end_sound.play()
        dialog = game_ui.GameOverDialog(self, self.current_game)
        dialog.show()
        self.show_available_rounds_panel()

    def show_question(self, topic, question):
        # remove old question view if it exists
        if self.current_question_panel:
            self.stackedWidget.removeWidget(self.current_question_panel)
            self.current_question_panel.remove_signals_and_slots()
        # save chosen topic and question in Game class
        self.current_game.current_topic = topic
        self.current_game.current_question = question
        # create new question view
        self.current_question_panel = game_ui.QuestionViewPanel(self,
                                                                self.current_game,
                                                                self.WIDTH,
                                                                self.HEIGHT)
        self.stackedWidget.addWidget(self.current_question_panel)
        self.stackedWidget.setCurrentWidget(self.current_question_panel)

    def show_available_rounds_panel(self):
        # delete buzzer config panel if it exists already to unhook buzzer API
        if self.buzzer_config_panel:
            self.stackedWidget.removeWidget(self.buzzer_config_panel)
        # reset all internal state of game object
        if self.current_game:
            self.current_game.reset_game()
        # build and display available rounds
        if not self.available_rounds_panel:
            self.available_rounds_panel = admin.AvailableRoundPanel(self, self.WIDTH,
                                                                    self.HEIGHT)
            self.stackedWidget.addWidget(self.available_rounds_panel)
        self.stackedWidget.setCurrentWidget(self.available_rounds_panel)

    def show_buzzer_config_panel(self):
        # remove old buzzer config panel
        if self.buzzer_config_panel:
            self.stackedWidget.removeWidget(self.buzzer_config_panel)
        # create new buzzer config panel
        self.buzzer_config_panel = admin.BuzzerConfigPanel(self,
                                                           self.current_game,
                                                           self.WIDTH,
                                                           self.HEIGHT)
        self.stackedWidget.addWidget(self.buzzer_config_panel)
        self.stackedWidget.setCurrentWidget(self.buzzer_config_panel)

    def show_config_panel(self):
        config_panel = admin.ConfigurationPanel(self,
                                                self.current_game,
                                                self.WIDTH,
                                                self.HEIGHT)
        self.stackedWidget.addWidget(config_panel)
        self.stackedWidget.setCurrentWidget(config_panel)

    def show_information_panel(self):
        info_panel = admin.InformationPanel(self,
                                            self.current_game,
                                            self.WIDTH,
                                            self.HEIGHT)
        self.stackedWidget.addWidget(info_panel)
        self.stackedWidget.setCurrentWidget(info_panel)


def handle_exit():
    """Handles closing of the pyQt main window by destroying the python
    interpreter."""
    config.save_config_to_file()


def start_gui():
    import sys
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.aboutToQuit.connect(handle_exit)
    main = PyPardyGui()
    main.show()
    app.exec_()


if __name__ == "__main__":
    start_gui()
