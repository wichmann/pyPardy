
"""
pyPardy

Administrative widgets of pyPardy.

@author: Christian Wichmann
"""

import logging
from PyQt4 import QtGui
from PyQt4 import QtCore

from data import round
from data import config


logger = logging.getLogger('pyPardy.gui')


class BuzzerConfigPanel(QtGui.QWidget):
    """Shows a panel to config the buzzers for all teams."""
    def __init__(self, parent, width, height):
        super(BuzzerConfigPanel, self).__init__(parent)
        self.main_gui = parent
        self.team_label_list = []
        self.currently_highlighted_team = 0
        self.setFixedSize(width, height)
        self.create_fonts()
        self.setup_ui()
        self.set_signals_and_slots()
        self.build_timer()

    def create_fonts(self):
        base_font = 'Linux Biolinum O'
        self.label_font = QtGui.QFont(base_font)
        self.label_font.setPointSize(30)

    def setup_ui(self):
        #self.setSizePolicy(QtGui.QSizePolicy.Expanding,
        #                   QtGui.QSizePolicy.Expanding)
        hbox = QtGui.QHBoxLayout()
        for i in range(config.MAX_TEAM_NUMBER):
            hbox.addStretch(1)
            # create new vbox for button and label
            vbox = QtGui.QVBoxLayout()
            vbox.addStretch(1)
            new_button = QtGui.QPushButton()
            new_button.setIcon(QtGui.QIcon('./icons/buzzer.png'))
            new_button.setIconSize(QtCore.QSize(128, 128))
            vbox.addWidget(new_button)
            team_name = 'Team {}'.format(i + 1)
            new_label = QtGui.QLabel(team_name)
            self.team_label_list.append(new_label)
            new_label.setAlignment(QtCore.Qt.AlignCenter |
                                   QtCore.Qt.AlignHCenter)
            new_label.setFont(self.label_font)
            vbox.addWidget(new_label)
            vbox.addStretch(1)
            # add vbox to hbox
            hbox.addLayout(vbox)
            hbox.addStretch(1)
        self.setLayout(hbox)
        self.team_label_list[0].setStyleSheet("color: red")

    def set_signals_and_slots(self):
        """Sets all signals and slots for main window."""
        pass

    def build_timer(self):
        """Builds timer that simulates buzzer pressed."""
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_buzzer_pressed)
        self.timer.start(2000)

    @QtCore.pyqtSlot()
    def on_buzzer_pressed(self):
        # FIXME Use buzzer connection to call method 'on_buzzer_pressed'
        # when buzzer was pressed and save buzzer id for teams in Game class
        if self.currently_highlighted_team < config.MAX_TEAM_NUMBER - 1:
            self.team_label_list[self.currently_highlighted_team].setStyleSheet("color: black")
            self.currently_highlighted_team += 1
            self.team_label_list[self.currently_highlighted_team].setStyleSheet("color: red")
        else:
            self.team_label_list[self.currently_highlighted_team].setStyleSheet("color: black")
            self.timer.stop()
            self.main_gui.show_available_rounds_panel()


class AvailableRoundPanel(QtGui.QWidget):
    """Panel showing all available rounds."""
    def __init__(self, parent, width, height):
        """Initialize panel for displaying all available rounds."""
        super(AvailableRoundPanel, self).__init__(parent)
        self.main_gui = parent
        self.setFixedSize(width, height)
        self.create_fonts()
        self.setup_ui()
        self.set_signals_and_slots()

    def create_fonts(self):
        base_font = 'Linux Biolinum O'
        self.title_font = QtGui.QFont(base_font)
        self.title_font.setPointSize(30)
        self.button_font = QtGui.QFont(base_font)
        self.button_font.setPointSize(20)

    def setup_ui(self):
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
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
        for filename in data:
            new_button = QtGui.QPushButton(filename)
            new_button.resize(new_button.sizeHint())
            new_button.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                     QtGui.QSizePolicy.Expanding)
            new_button.setFont(self.button_font)
            new_button.clicked.connect(self.on_button_click)
            self.button_box.addWidget(new_button)
            self.button_box.addStretch(1)
        # add button for assigning team buzzer
        buzzer_config_button = QtGui.QPushButton('Zuordnung der Buzzer ändern...')
        buzzer_config_button.setFont(self.button_font)
        buzzer_config_button.clicked.connect(self.on_buzzer_config_button)
        self.button_box.addWidget(buzzer_config_button)
        # add space after all buttons are inserted
        self.button_box.addStretch(10)
        # put vbox into hbox to center horizontally
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(self.button_box)
        hbox.addStretch(1)
        self.setLayout(hbox)

    def set_signals_and_slots(self):
        """Sets all signals and slots for main window."""
        pass

    @QtCore.pyqtSlot()
    def on_button_click(self):
        filename_to_load = self.sender().text()
        logger.info('File "{}" should be loaded...'.format(filename_to_load))
        self.main_gui.show_round_table(filename_to_load)

    @QtCore.pyqtSlot()
    def on_buzzer_config_button(self):
        logger.info('Changing buzzer configuration...')
        self.main_gui.show_buzzer_config_panel()
