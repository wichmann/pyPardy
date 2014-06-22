
"""
pyPardy

Main window of pyPardy

@author: Christian Wichmann
"""

import logging
from PyQt4 import QtGui
from PyQt4 import QtCore

from data import round
from data import game
from data import config
from gui import game as game_ui
from gui import admin


__all__ = ['start_gui']


logger = logging.getLogger('pyPardy.gui')


class PyPardyGui(QtGui.QMainWindow):
    """Main window for pyPardy"""
    def __init__(self, parent=None):
        """Initialize main window for pyPardy."""
        logger.info('Building main window of pyPardy...')
        QtGui.QMainWindow.__init__(self, parent)
        self.WIDTH = 1000
        self.HEIGHT = 750
        # define all panels that are used inside the QStackedWidget
        self.available_rounds_panel = None
        self.current_round_question_panel = None
        self.current_question_panel = None
        self.buzzer_config_panel = None
        # build and config all widgets
        self.setup_ui()
        self.center_on_screen()
        self.set_signals_and_slots()
        # create instance of Game class for saving all necessary data
        self.current_game = game.Game()

    def __del__(self):
        if self.buzzer_config_panel:
            self.buzzer_config_panel.__del__()

    def setup_ui(self):
        """Initializes the UI by displaying all available rounds."""
        # set size of window
        self.resize(self.WIDTH, self.HEIGHT)
        #self.showFullScreen()
        self.setWindowTitle(config.APP_NAME)
        self.setWindowIcon(QtGui.QIcon('icons/buzzer.png'))
        # build stacked widget for all current and coming panels
        self.stackedWidget = QtGui.QStackedWidget()
        self.stackedWidget.setFixedSize(self.WIDTH, self.HEIGHT)
        self.show_available_rounds_panel()
        # set central widget for main window
        self.setCentralWidget(self.stackedWidget)

    def center_on_screen(self):
        """Centers the window on the screen."""
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def set_signals_and_slots(self):
        """Sets all signals and slots for main window."""
        pass

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
        # create new question table
        self.current_round_question_panel = game_ui.QuestionTablePanel(self, self.current_game,
                                                                       self.WIDTH, self.HEIGHT)
        self.stackedWidget.addWidget(self.current_round_question_panel)
        self.stackedWidget.setCurrentWidget(self.current_round_question_panel)

    def back_to_round_table(self):
        self.stackedWidget.setCurrentWidget(self.current_round_question_panel)
        self.current_round_question_panel.update_question_buttons()
        if self.current_game.is_round_complete():
            logger.info('Round was completed.')
            QtGui.QMessageBox.information(self, 'Rund komplett!',
                                          "Die aktuelle Runde des Spiels ist komplett.",
                                          QtGui.QMessageBox.Ok)
            self.show_available_rounds_panel()

    def show_question(self, topic, question):
        # remove old question view if it exists
        if self.current_question_panel:
            self.stackedWidget.removeWidget(self.current_question_panel)
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
        self.current_game = game.Game()
        if not self.available_rounds_panel:
            self.available_rounds_panel = admin.AvailableRoundPanel(self, self.WIDTH,
                                                                    self.HEIGHT)
            self.stackedWidget.addWidget(self.available_rounds_panel)
        self.stackedWidget.setCurrentWidget(self.available_rounds_panel)

    def show_answer_for_questions(self):
        pass

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


def start_gui():
    import sys
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    main = PyPardyGui()
    main.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    start_gui()
