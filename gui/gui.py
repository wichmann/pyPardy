
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
from gui import helper


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
        self.current_game = None
        self.buzzer_config_panel = None
        # build and config all widgets
        self.setup_ui()
        #self.set_background()
        self.center_on_screen()
        self.set_signals_and_slots()
        # create instance of Game class for saving all necessary data
        self.current_game = game.Game()

    # FIXME Handle game ending and release all resources from buzzer API!
    def __del__(self):
        helper

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

    def set_background(self):
        """Paints a color gradient over the background.

        Sources:
         * http://developer.nokia.com/community/wiki/Archived:Creating_a_gradient_background_for_a_QPushButton_with_style_sheet
         * https://wiki.python.org/moin/PyQt/Windows%20with%20gradient%20backgrounds
        """
        #palette = QtGui.QPalette()
        #gradient = QtGui.QLinearGradient(QtCore.QRectF(self.rect()).topLeft(),
        #                                 QtCore.QRectF(self.rect()).topRight())
        #gradient.setColorAt(0.0, QtGui.QColor(33, 152, 192))
        #gradient.setColorAt(1.0, QtGui.QColor(13, 92, 166))
        #palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(gradient))
        #self.setPalette(palette)
        self.stackedWidget.setStyleSheet("""background-color: qlineargradient(
                              x1: 0, y1: 0, x2: 0, y2: 1,
                              stop: 0 #2198c0, stop: 1 #0d5ca6);""")

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
        """Handles the transition from question view panel back to the table
        with all questions of the round."""
        self.stackedWidget.setCurrentWidget(self.current_round_question_panel)
        self.current_round_question_panel.update_widgets()
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


def handle_exit():
    """Handles closing of the pyQt main window by destroying the python
    interpreter."""
    # TODO Close all threads for sub connections so that the application
    # end automatically!
    #helper.get_buzzer_connector().close_connection()
    import sys
    sys.exit()


def start_gui():
    import sys
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.aboutToQuit.connect(handle_exit)
    main = PyPardyGui()
    main.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    start_gui()
