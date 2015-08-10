
"""
pyPardy

Administrative widgets of pyPardy.

@author: Christian Wichmann
"""

import logging
from functools import partial
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtDeclarative
# QtQml

from data import round
from data import config
from gui import helper


logger = logging.getLogger('pyPardy.gui')


class BuzzerConfigPanel(QtGui.QWidget):
    """Shows a panel to config the buzzers for all teams."""
    def __init__(self, parent, game_data, width, height):
        super(BuzzerConfigPanel, self).__init__(parent)
        self.main_gui = parent
        self.game_data = game_data
        self.team_label_list = []
        self.currently_highlighted_team = 0
        self.STYLE_HIGHLIGHTED = 'border: none; background: none; color: red'
        self.STYLE_NONHIGHLIGHTED = 'border: none; background: none; color: black'

        self.setFixedSize(width, height)
        self.create_fonts()
        self.setup_ui()
        if config.HIGH_CONTRAST:
            helper.whitefy(self)
        self.set_signals_and_slots()

    def create_fonts(self):
        if config.LOW_RESOLUTION:
            self.label_font = QtGui.QFont(config.BASE_FONT)
            self.label_font.setPointSize(22)
        else:
            self.label_font = QtGui.QFont(config.BASE_FONT)
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
            new_button.setDown(True)
            vbox.addWidget(new_button)
            team_name = config.TEAM_NAMES[i]
            new_label_input = QtGui.QLineEdit(team_name)
            self.team_label_list.append(new_label_input)
            new_label_input.setAlignment(QtCore.Qt.AlignCenter |
                                   QtCore.Qt.AlignHCenter)
            new_label_input.setFont(self.label_font)
            new_label_input.setStyleSheet(self.STYLE_NONHIGHLIGHTED)
            new_label_input.returnPressed.connect(partial(self.on_change_team_name, i))
            vbox.addWidget(new_label_input)
            vbox.addStretch(1)
            # add vbox to hbox
            hbox.addLayout(vbox)
            hbox.addStretch(1)
        self.setLayout(hbox)
        self.team_label_list[0].setStyleSheet(self.STYLE_HIGHLIGHTED)

    def on_change_team_name(self, team_id):
        new_team_name = self.team_label_list[team_id].text()
        config.TEAM_NAMES[team_id] = new_team_name

    def set_signals_and_slots(self):
        """Sets all signals and slots for buzzer configuation window."""
        self.buzzer_connector = helper.get_buzzer_connector()
        self.buzzer_connector.flush_connection()
        self.buzzer_connector.buzzing.connect(self.on_buzzer_pressed)

    def close_connection_to_buzzer(self):
        self.buzzer_connector.buzzing.disconnect(self.on_buzzer_pressed)
        self.buzzer_connector = None

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            self.close_connection_to_buzzer()
            self.main_gui.show_available_rounds_panel()

    @QtCore.pyqtSlot(int)
    def on_buzzer_pressed(self, buzzer_id):
        """Handles a pressed buzzer and highlight the next team name.

        :param buzzer_id: buzzer id delivered by BuzzerReader()"""
        logger.info('Getting buzzer id ({}) from buzzer API.'.format(buzzer_id))
        # set buzzer id for current team in Game object
        self.game_data.set_buzzer_id_for_team(self.currently_highlighted_team,
                                              buzzer_id)
        if self.currently_highlighted_team < config.MAX_TEAM_NUMBER - 1:
            # unhighlight last team name
            self.team_label_list[self.currently_highlighted_team].setStyleSheet(self.STYLE_NONHIGHLIGHTED)
            # highlight next team name
            self.currently_highlighted_team += 1
            self.team_label_list[self.currently_highlighted_team].setStyleSheet(self.STYLE_HIGHLIGHTED)
        else:
            # unhighlight all team names and return
            self.team_label_list[self.currently_highlighted_team].setStyleSheet(self.STYLE_NONHIGHLIGHTED)
            self.close_connection_to_buzzer()
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
        helper.whitefy(self)

    def create_fonts(self):
        if config.LOW_RESOLUTION:
            self.title_font = QtGui.QFont(config.BASE_FONT)
            self.title_font.setPointSize(32)
            self.button_font = QtGui.QFont(config.BASE_FONT)
            self.button_font.setPointSize(24)
        else:
            self.title_font = QtGui.QFont(config.BASE_FONT)
            self.title_font.setPointSize(42)
            self.button_font = QtGui.QFont(config.BASE_FONT)
            self.button_font.setPointSize(36)

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
        # add button for assigning team buzzer
        buzzer_config_button = QtGui.QPushButton()
        buzzer_config_button.setText(_('Change buzzer assignment'))
        buzzer_config_button.setFont(self.button_font)
        buzzer_config_button.clicked.connect(self.on_buzzer_config_button)
        self.button_box.addStretch(5)
        self.button_box.addWidget(buzzer_config_button)
        # add button for configuration
        config_button = QtGui.QPushButton()
        config_button.setText(_('Configuration'))
        config_button.setFont(self.button_font)
        config_button.clicked.connect(self.on_config_button)
        self.button_box.addStretch(1)
        self.button_box.addWidget(config_button)
        # add button for information panel
        info_button = QtGui.QPushButton()
        info_button.setText(_('Information'))
        info_button.setFont(self.button_font)
        info_button.clicked.connect(self.on_information_button)
        self.button_box.addStretch(1)
        self.button_box.addWidget(info_button)
        # add button for quitting application
        quit_button = QtGui.QPushButton()
        quit_button.setText(_('Exit'))
        quit_button.setFont(self.button_font)
        quit_button.clicked.connect(self.main_gui.close)
        self.button_box.addStretch(1)
        self.button_box.addWidget(quit_button)
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
        filename_to_load = self.sender().filename
        logger.info('File "{}" should be loaded...'.format(filename_to_load))
        self.main_gui.show_round_table(filename_to_load)

    @QtCore.pyqtSlot()
    def on_buzzer_config_button(self):
        logger.info('Changing buzzer configuration...')
        self.main_gui.show_buzzer_config_panel()

    @QtCore.pyqtSlot()
    def on_information_button(self):
        logger.info('Showing information about game...')
        self.main_gui.show_information_panel()

    @QtCore.pyqtSlot()
    def on_config_button(self):
        logger.info('Showing configuration panel...')
        self.main_gui.show_config_panel()


class ConfigurationPanel(QtGui.QWidget):
    """Shows a panel to config all settings for pyPardy."""
    def __init__(self, parent, game_data, width, height):
        super(ConfigurationPanel, self).__init__(parent)
        self.main_gui = parent
        self.game_data = game_data
        self.setFixedSize(width, height)
        self.create_fonts()
        self.setup_data()
        self.setup_ui()
        self.fill_options()
        self.set_signals_and_slots()

    def create_fonts(self):
        if config.LOW_RESOLUTION:
            self.label_font = QtGui.QFont(config.BASE_FONT)
            self.label_font.setPointSize(22)
        else:
            self.label_font = QtGui.QFont(config.BASE_FONT)
            self.label_font.setPointSize(30)

    def setup_data(self):
        self.game_options = { 'ADD_ROUND_POINTS': None,
                              'ALLOW_ALL_TEAMS_TO_ANSWER': None,
                              'HIDE_QUESTION': None,
                              'PENALTY_WRONG_ANSWERS': None }
        self.audio_options = { 'AUDIO_MUSIC': None,
                               'AUDIO_SFX': None,
                               'AUDIO_SPEECH': None,
                               'LOOP_BACKGROUND_MUSIC': None }
        self.visual_options = { 'FULLSCREEN': None,
                                'HIGH_CONTRAST': None,
                                'LOW_RESOLUTION': None }
        self.game_options_labels = { 'ADD_ROUND_POINTS': _('Add points from different rounds'),
                                     'ALLOW_ALL_TEAMS_TO_ANSWER': _('Allow all teams to answer one after another'),
                                     'HIDE_QUESTION': _('Hide question after buzzing'),
                                     'PENALTY_WRONG_ANSWERS': _('Subtract penalty for wrong answers') }
        self.audio_options_labels = { 'AUDIO_MUSIC': _('Activate background music'),
                                      'AUDIO_SFX': _('Activate sound effects'),
                                      'AUDIO_SPEECH': _('Activate reading questions by TTS'),
                                      'LOOP_BACKGROUND_MUSIC': _('Loop background music') }
        self.visual_options_labels = { 'FULLSCREEN': _('Show in fullscreen'),
                                       'HIGH_CONTRAST': _('Show with high contrasts'),
                                       'LOW_RESOLUTION': _('Show version for low resolutions') }
    def setup_ui(self):
        vbox = QtGui.QVBoxLayout()
        # add game options
        game_options_group = QtGui.QGroupBox(_('Game options'))
        formLayout = QtGui.QFormLayout()
        game_options_group.setLayout(formLayout)
        for option in sorted(self.game_options):
            new_option = QtGui.QCheckBox()
            self.game_options[option] = new_option
            formLayout.addRow(self.game_options_labels[option], new_option)
        self.team_number_spin = QtGui.QSpinBox()
        self.team_number_spin.setMaximum(6)
        self.team_number_spin.setMinimum(2)
        formLayout.addRow(_('Number of teams'), self.team_number_spin)
        self.questions_points_spin = QtGui.QSpinBox()
        self.questions_points_spin.setMaximum(500)
        self.questions_points_spin.setMinimum(10)
        self.questions_points_spin.setSuffix(_(' points'))
        formLayout.addRow(_('Points per Question'), self.questions_points_spin)
        self.questions_time_spin = QtGui.QSpinBox()
        self.questions_time_spin.setMaximum(600)
        self.questions_time_spin.setMinimum(1)
        self.questions_time_spin.setSuffix(_(' seconds'))
        formLayout.addRow(_('Time per question (seconds)'), self.questions_time_spin)
        vbox.addWidget(game_options_group)
        # add audio options
        audio_options_group = QtGui.QGroupBox(_('Audio options'))
        formLayout = QtGui.QFormLayout()
        audio_options_group.setLayout(formLayout)
        for option in sorted(self.audio_options):
            new_option = QtGui.QCheckBox()
            self.audio_options[option] = new_option
            formLayout.addRow(self.audio_options_labels[option], new_option)
        vbox.addWidget(audio_options_group)
        # add visual options
        visual_options_group = QtGui.QGroupBox(_('Visual options'))
        formLayout = QtGui.QFormLayout()
        visual_options_group.setLayout(formLayout)
        for option in sorted(self.visual_options):
            new_option = QtGui.QCheckBox()
            self.visual_options[option] = new_option
            formLayout.addRow(self.visual_options_labels[option], new_option)
        vbox.addWidget(visual_options_group)
        # add button for returning to menu
        button_box = QtGui.QHBoxLayout()
        button_box.addStretch(100)
        self.back_button = QtGui.QPushButton(_('Back'))
        self.save_button = QtGui.QPushButton(_('Save'))
        button_box.addWidget(self.save_button)
        button_box.addWidget(self.back_button)
        vbox.addLayout(button_box)
        self.setLayout(vbox)

    def fill_options(self):
        # fill in game options
        for option_name, option_widget in self.game_options.items():
            option_widget.setChecked(getattr(config, option_name))
        self.team_number_spin.setValue(config.MAX_TEAM_NUMBER)
        self.questions_points_spin.setValue(config.QUESTION_POINTS)
        self.questions_time_spin.setValue(config.QUESTION_TIME)
        # fill in audio options
        for option_name, option_widget in self.audio_options.items():
            option_widget.setChecked(getattr(config, option_name))
        # fill in visual options
        for option_name, option_widget in self.visual_options.items():
            option_widget.setChecked(getattr(config, option_name))

    def store_options(self):
        # store game options
        for option_name, option_widget in self.game_options.items():
            setattr(config, option_name, option_widget.isChecked())
        try:
            value = int(self.team_number_spin.cleanText())
            config.MAX_TEAM_NUMBER = value
        except ValueError:
            value = 0
        try:
            value = int(self.questions_points_spin.cleanText())
            config.QUESTION_POINTS = value
        except ValueError:
            value = 0
        try:
            value = int(self.questions_time_spin.cleanText())
            config.QUESTION_TIME = value
        except ValueError:
            value = 0
        # store audio options
        for option_name, option_widget in self.audio_options.items():
            setattr(config, option_name, option_widget.isChecked())
        # store visual options
        for option_name, option_widget in self.visual_options.items():
            setattr(config, option_name, option_widget.isChecked())

    def set_signals_and_slots(self):
        """Sets all signals and slots."""
        self.back_button.clicked.connect(lambda: self.on_back_button(False))
        self.save_button.clicked.connect(lambda: self.on_back_button(True))

    @QtCore.pyqtSlot()
    def on_back_button(self, save_options=False):
        if save_options:
            self.store_options()
        self.main_gui.show_available_rounds_panel()


class InformationPanel(QtGui.QWidget):
    """Shows a panel with information about pyPardy."""
    def __init__(self, parent, game_data, width, height):
        super(InformationPanel, self).__init__(parent)
        self.main_gui = parent
        self.game_data = game_data
        self.setFixedSize(width, height)
        self.create_fonts()
        self.setup_ui()
        self.set_signals_and_slots()

    def create_fonts(self):
        if config.LOW_RESOLUTION:
            self.label_font = QtGui.QFont(config.BASE_FONT)
            self.label_font.setPointSize(22)
        else:
            self.label_font = QtGui.QFont(config.BASE_FONT)
            self.label_font.setPointSize(30)

    def setup_ui(self):
        vbox = QtGui.QVBoxLayout()
        vbox.setMargin(10)
        # add text labels
        label_6 = QtGui.QLabel()
        label_6.setFont(self.label_font)
        label_6.setText(_("pyPardy"))
        label_6.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(label_6)
        label_9 = QtGui.QLabel()
        label_9.setFont(self.label_font)
        label_9.setText(_("pyPardy is a game similar to Jeopardy(tm)."))
        label_9.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(label_9)
        line = QtGui.QFrame()
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)
        vbox.addWidget(line)
        label_7 = QtGui.QLabel()
        label_7.setText(_("Author: Christian Wichmann"))
        label_7.setFont(self.label_font)
        label_7.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(label_7)
        label_8 = QtGui.QLabel()
        label_8.setFont(self.label_font)
        label_8.setText(_("Licensed under GNU GPL v2 or newer."))
        label_8.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(label_8)
        # add button for returning to menu
        button_box = QtGui.QHBoxLayout()
        button_box.addStretch(100)
        self.back_button = QtGui.QPushButton(_('Back'))
        button_box.addWidget(self.back_button)
        vbox.addLayout(button_box)
        self.setLayout(vbox)

    def set_signals_and_slots(self):
        """Sets all signals and slots."""
        self.back_button.clicked.connect(self.on_back_button)

    @QtCore.pyqtSlot()
    def on_back_button(self):
        self.main_gui.show_available_rounds_panel()
