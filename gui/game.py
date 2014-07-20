
"""
pyPardy

Widgets for showing questions.

@author: Christian Wichmann
"""

import logging
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.phonon import Phonon

from data import config
from data import game
from gui import helper


logger = logging.getLogger('pyPardy.gui')


# time before a buzzer press has any effect
STARTUP_TIME = 0
# step that will be used to decrease game time
GAME_TIME_STEP = 100
# factor to divide given time in seconds into part of that
GAME_TIME_FACTOR = 10


class QuestionTablePanel(QtGui.QWidget):
    """Panel showing all questions of a chosen round.

    :param round_data_file_name: filename of data file containing all round
                                 data
    """
    # define signal to be used to update widgets inside this QuestionTablePanel
    table_shown = QtCore.pyqtSignal()

    def __init__(self, parent, game_data, width, height):
        """Initialize panel for displaying all questions."""
        super(QuestionTablePanel, self).__init__(parent)
        logger.info('Generating question table for round "{}"'
                    .format(game_data.current_round_data['title']))
        self.game_data = game_data
        self.main_gui = parent
        self.button_list = []
        self.setFixedSize(width, height)
        self.create_fonts()
        self.setup_ui()
        helper.whitefy(self)
        self.set_signals_and_slots()

    def create_fonts(self):
        if config.LOW_RESOLUTION:
            self.title_font = QtGui.QFont(config.BASE_FONT)
            self.title_font.setPointSize(32)
            self.topic_font = QtGui.QFont(config.BASE_FONT)
            self.topic_font.setPointSize(16)
            self.question_font = QtGui.QFont(config.BASE_FONT)
            self.question_font.setPointSize(36)
        else:
            self.title_font = QtGui.QFont(config.BASE_FONT)
            self.title_font.setPointSize(46)
            self.topic_font = QtGui.QFont(config.BASE_FONT)
            self.topic_font.setPointSize(24)
            self.question_font = QtGui.QFont(config.BASE_FONT)
            self.question_font.setPointSize(56)

    def setup_ui(self):
        self.box_layout = QtGui.QHBoxLayout()
        self.setLayout(self.box_layout)
        # build table
        self.box_layout.addLayout(self.build_table())
        # add team view widget
        self.team_view_panel = TeamViewPanel(self, self.game_data,
                                             150, self.height(),
                                             TeamViewPanel.VERTICAL_ORIENTATION)
        self.box_layout.addWidget(self.team_view_panel, QtCore.Qt.AlignCenter |
                                  QtCore.Qt.AlignRight)

    def build_table(self):
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.button_grid = QtGui.QGridLayout()
        margin = 40
        self.button_grid.setContentsMargins(margin, margin, margin, margin)
        # add title label
        title_label = QtGui.QLabel(self.game_data.current_round_data['title'])
        title_label.setFont(self.title_font)
        title_label.setAlignment(QtCore.Qt.AlignTop |
                                 QtCore.Qt.AlignHCenter)
        self.button_grid.addWidget(title_label, 0, 0, 1, 8)
        # add questions and labels  for all topics
        for topic_count, topic in enumerate(self.game_data.current_round_data['topics']):
            # add topic title label
            topic_label = QtGui.QLabel(topic['title'])
            topic_label.setAlignment(QtCore.Qt.AlignCenter |
                                     QtCore.Qt.AlignHCenter)
            topic_label.setFont(self.topic_font)
            self.button_grid.addWidget(topic_label, 1, topic_count)
            # add buttons for all questions
            points = 0
            for question_count, question in enumerate(topic['questions']):
                points += config.QUESTION_POINTS
                button_text = str(points)
                # create new button for question
                new_button = QtGui.QPushButton(button_text)
                new_button.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                         QtGui.QSizePolicy.Expanding)
                if config.HIGH_CONTRAST:
                    helper.whitefy(new_button)
                # set topic and question number inside each QButton
                new_button.topic_count = topic_count
                new_button.question_count = question_count
                new_button.setFont(self.question_font)
                new_button.clicked.connect(self.on_button_click)
                self.button_list.append(new_button)
                self.button_grid.addWidget(new_button, question_count+2,
                                           topic_count)
        return self.button_grid

    def set_signals_and_slots(self):
        """Sets all signals and slots for question table panel."""
        self.table_shown.connect(self.team_view_panel.on_update_points)

    def keyPressEvent(self, event):
        """Handle key events for cursor keys to navigate questions."""
        if event.isAutoRepeat():
            return
        # check which QButton is focused
        widget = QtGui.qApp.focusWidget()
        if isinstance(widget, QtGui.QPushButton):
            topic = widget.topic_count
            question = widget.question_count
        else:
            return
        # react to cursor keys
        list_of_keys = [QtCore.Qt.Key_1, QtCore.Qt.Key_2, QtCore.Qt.Key_3,
                        QtCore.Qt.Key_4, QtCore.Qt.Key_5, QtCore.Qt.Key_6]
        key = event.key()
        for i in range(config.MAX_TEAM_NUMBER):
            if key == list_of_keys[i]:
                self.game_data.correct_points_by_100(i)
                self.team_view_panel.on_update_points()
        if key == QtCore.Qt.Key_D:
            self.focus_specific_button(topic + 1, question)
        elif key == QtCore.Qt.Key_A:
            self.focus_specific_button(topic - 1, question)
        elif key == QtCore.Qt.Key_W:
            self.focus_specific_button(topic, question - 1)
        elif key == QtCore.Qt.Key_S:
            self.focus_specific_button(topic, question + 1)

    def focus_specific_button(self, topic, question):
        """Focuses a given button defined by its topic and the question number.

        This method checks if the given coordinates (topic, question) are valid
        within the bounds of the current round.

        :param topic: given topic number of which a button should be focused
        :param question: given question number of which a button should be
                         focused
        """
        for button in self.button_list:
            if button.topic_count == topic and button.question_count == question:
                button.setFocus()

    def update_widgets(self):
        # check which questions were played already
        for button in self.button_list:
            if self.game_data.was_question_completed(button.topic_count,
                                                     button.question_count):
                button.setEnabled(False)
                button.setText('')
        # update points for teams by emitting a signal 'table_shown'
        self.table_shown.emit()

    @QtCore.pyqtSlot()
    def on_button_click(self):
        """Handles a mouse click on one of the question buttons. After the
        click the question is loaded by the main gui (PyPardyGUI) and show in
        a new QuestionViewPanel.
        """
        topic = self.sender().topic_count
        question = self.sender().question_count
        logger.info('Question {} from topic {} should be shown...'
                    .format(question, topic))
        self.main_gui.show_question(topic, question)


class QuestionViewPanel(QtGui.QWidget):
    """Panel showing one question including a timer counting the time."""
    def __init__(self, parent, game_data, width, height):
        """Initialize panel for displaying one question including its timer.

        :param parent: parent widget
        :param game_data: instance of Game() containing all necessary
                          information
        :param width: width of this question view panel
        :param height: height of this question view panel
        """
        super(QuestionViewPanel, self).__init__(parent)
        # set data for this panel
        self.game_data = game_data
        self.main_gui = parent
        self.topic = game_data.get_topic_name()
        self.points = game_data.get_points_for_current_question()
        self.current_time = config.QUESTION_TIME * GAME_TIME_FACTOR
        self.last_buzzed_team = -1
        self.setFixedSize(width, height)
        # build gui and slots
        self.create_fonts()
        self.setup_ui()
        helper.whitefy(self)
        self.set_signals_and_slots()
        self.start_timer()
        # audio methods
        self.init_audio()
        self.play_background_music()
        self.read_question()

    def __del__(self):
        self.remove_signals_and_slots()
        self.close_connection_to_buzzer()

    def create_fonts(self):
        if config.LOW_RESOLUTION:
            self.question_font = QtGui.QFont(config.BASE_FONT)
            self.question_font.setPointSize(30)
            self.button_font = QtGui.QFont(config.BASE_FONT)
            self.button_font.setPointSize(18)
        else:
            self.question_font = QtGui.QFont(config.BASE_FONT)
            self.question_font.setPointSize(42)
            self.button_font = QtGui.QFont(config.BASE_FONT)
            self.button_font.setPointSize(24)

    def setup_ui(self):
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)
        # set margins for whole layout
        margin = 40
        self.grid.setContentsMargins(margin, margin, margin, margin)
        # build widgets
        self.build_info_button()
        self.build_control_buttons()
        self.build_labels()
        self.build_timer_widgets()

    def build_info_button(self):
        # add buttons for topic and points
        if config.HIGH_CONTRAST:        
            INFO_BUTTON_STYLE = 'color: black;'
        else:
            INFO_BUTTON_STYLE = 'background-color: yellow; color: black;'
        topic_button = QtGui.QPushButton(helper.replace_line_breaks(self.topic))
        topic_button.setEnabled(False)
        topic_button.setFont(self.button_font)
        topic_button.setStyleSheet(INFO_BUTTON_STYLE)
        self.grid.addWidget(topic_button, 0, 0, QtCore.Qt.AlignTop)
        points_button = QtGui.QPushButton(helper.replace_line_breaks(str(self.points)))
        points_button.setEnabled(False)
        points_button.setFont(self.button_font)
        points_button.setStyleSheet(INFO_BUTTON_STYLE)
        self.grid.addWidget(points_button, 0, 1, QtCore.Qt.AlignTop)

    def build_control_buttons(self):
        # add button for showing the answer of the question
        self.show_answer_button = QtGui.QPushButton('Antwort...')
        self.show_answer_button.setFont(self.button_font)
        self.show_answer_button.setEnabled(False)
        helper.hide_widget(self.show_answer_button)
        self.grid.addWidget(self.show_answer_button, 2, 0,
                            QtCore.Qt.AlignBottom)
        # add button for going back to question table
        self.answer_correct_button = QtGui.QPushButton('Richtig!')
        self.answer_correct_button.setFont(self.button_font)
        self.answer_correct_button.setEnabled(False)
        helper.hide_widget(self.answer_correct_button)
        self.grid.addWidget(self.answer_correct_button, 2, 1,
                            QtCore.Qt.AlignBottom)
        self.answer_incorrect_button = QtGui.QPushButton('Falsch!')
        self.answer_incorrect_button.setFont(self.button_font)
        self.answer_incorrect_button.setEnabled(False)
        helper.hide_widget(self.answer_incorrect_button)
        self.grid.addWidget(self.answer_incorrect_button, 2, 2,
                            QtCore.Qt.AlignBottom)

    def build_labels(self):
        # add question label
        self.question_label = QtGui.QLabel(self.game_data.get_current_question())
        self.question_label.setFont(self.question_font)
        self.question_label.setLineWidth(25)
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(QtCore.Qt.AlignTop |
                                         QtCore.Qt.AlignHCenter)
        self.grid.addWidget(self.question_label, 1, 0, 1, 4)
        # add team view panel for showing team that buzzered first
        self.team_view_panel = TeamViewPanel(self, self.game_data,
                                             450, 150,
                                             TeamViewPanel.HORIZONTAL_ORIENTATION)
        self.grid.addWidget(self.team_view_panel, 0, 2, 1, 2,
                            QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)

    def build_timer_widgets(self):
        # add timer
        self.timer_lcd = QtGui.QLCDNumber(self)
        self.timer_lcd.setFixedSize(250, 150)
        #self.timer_lcd.resize(300, 200)
        self.timer_lcd.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.timer_lcd.setFrameStyle(QtGui.QFrame.NoFrame)
        #self.set_lcd_colors()
        self.grid.addWidget(self.timer_lcd, 2, 3,
                            QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)

    def set_lcd_colors(self):
        # get the palette
        palette = self.timer_lcd.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(85, 85, 255))
        palette.setColor(palette.Background, QtGui.QColor(0, 170, 255))
        palette.setColor(palette.Light, QtGui.QColor(255, 0, 0))
        palette.setColor(palette.Dark, QtGui.QColor(0, 255, 0))
        # set the palette
        self.timer_lcd.setPalette(palette)

    def set_signals_and_slots(self):
        """Sets all signals and slots for question view."""
        self.show_answer_button.clicked.connect(self.on_show_answer_button)
        self.answer_incorrect_button.clicked.connect(lambda: self.on_back_button(False))
        self.answer_correct_button.clicked.connect(lambda: self.on_back_button(True))
        self.startup_timer = QtCore.QTimer()
        self.startup_timer.timeout.connect(self.on_startup_timer)
        self.startup_timer.start(STARTUP_TIME)

    def on_startup_timer(self):
        """Handles initialization of buzzer API and connects buzzer connector
        instance with slot in this class. After this the question view panel
        will react on all buzzer presses.
        """
        self.startup_timer.stop()
        self.buzzer_connector = helper.get_buzzer_connector()
        self.buzzer_connector.flush_connection()
        self.buzzer_connector.buzzing.connect(self.on_buzzer_pressed)

    def remove_signals_and_slots(self):
        """Sets all signals and slots for question view."""
        self.show_answer_button.clicked.disconnect()
        self.answer_incorrect_button.clicked.disconnect()
        self.answer_correct_button.clicked.disconnect()
        self.buzzer_connector.buzzing.disconnect()

    def keyPressEvent(self, event):
        """Handle key events for choosing teams instead of buzzering and
        control by keyboard."""
        if event.isAutoRepeat():
            return
        list_of_keys = [QtCore.Qt.Key_1, QtCore.Qt.Key_2, QtCore.Qt.Key_3,
                        QtCore.Qt.Key_4, QtCore.Qt.Key_5, QtCore.Qt.Key_6]
        key = event.key()
        for i in range(config.MAX_TEAM_NUMBER):
            if key == list_of_keys[i]:
                self.on_buzzer_pressed(self.game_data.buzzer_id_list[i])

    def close_connection_to_buzzer(self):
        """Closes the connection between the BuzzerConnector and the callable
        method 'on_buzzer_pressed' on this class.
        """
        self.buzzer_connector.buzzing.disconnect(self.on_buzzer_pressed)
        self.buzzer_connector = None

    ##### game timer methods #####

    def start_timer(self):
        """Builds timer that will update game time depending on the value of
        GAME_TIME_STEP. Each time the lcd widget will be updated and decreased
        by GAME_TIME_STEP. The maximum game time is defined as seconds in the
        config file and multiplied by GAME_TIME_FACTOR to show part of seconds.
        """
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_update_lcd)
        self.timer.start(GAME_TIME_STEP)
        self.on_update_lcd()

    def stop_timer(self):
        self.timer_lcd.display('{0:01}'.format(self.current_time / GAME_TIME_FACTOR))
        self.timer.stop()

    ##### slot methods #####

    @QtCore.pyqtSlot(int)
    def on_buzzer_pressed(self, buzzer_id):
        """Handles a pressed buzzer and registers the team.

        :param buzzer_id: buzzer id delivered by BuzzerReader()"""
        logger.info('Buzzer ({}) was pressed.'.format(buzzer_id))
        if self.last_buzzed_team == -1:
            # stop background music and play buzzer sound
            self.background_music.stop()
            self.play_buzzer_sound()
            # get team id from buzzer id
            team_id = self.game_data.get_team_by_buzzer_id(buzzer_id)
            self.last_buzzed_team = team_id
            # update gui widgets
            self.team_view_panel.highlight_team(team_id)
            if self.timer.isActive():
                self.on_question_time_end()

    @QtCore.pyqtSlot()
    def on_update_lcd(self):
        if self.current_time > 0:
            # decrement time when not yet expired
            self.current_time -= 1
            self.timer_lcd.display('{0:01}'.format(self.current_time / GAME_TIME_FACTOR))
        else:
            self.on_question_time_end()

    def on_question_time_end(self):
        # stop timer and fade question out only when buzzered before end of
        # timer
        self.stop_timer()
        if config.HIDE_QUESTION:
            # fade question label out
            logger.info('Question has been faded out.')
            helper.animate_widget(self.question_label, True,
                                  self.on_question_fadeout)
        else:
            # do not hide question label but do what would be done when
            # hiding the question label
            self.on_question_fadeout()

    @QtCore.pyqtSlot()
    def on_question_fadeout(self):
        self.background_music.stop()
        self.show_answer_button.setEnabled(True)
        self.show_answer_button.setFocus()
        helper.animate_widget(self.show_answer_button, False)

    @QtCore.pyqtSlot()
    def on_answer_fadein(self):
        logger.info('Question has been faded out.')
        if self.last_buzzed_team != -1:
            # if one of the buzzers was pressed, show buttons for
            # right and wrong
            self.answer_correct_button.setEnabled(True)
            self.answer_incorrect_button.setEnabled(True)
            self.answer_correct_button.setFocus()
            helper.animate_widget(self.answer_correct_button, False)
            helper.animate_widget(self.answer_incorrect_button, False)
        else:
            # otherwise just show one of the buttons to get back
            # to the question view table
            self.answer_correct_button.setText('Zurück')
            self.answer_correct_button.setFocus()
            self.answer_correct_button.setEnabled(True)
            helper.animate_widget(self.answer_correct_button, False)

    @QtCore.pyqtSlot()
    def on_show_answer_button(self):
        logger.info('Answer is shown.')
        # build string with question and answer
        string = self.game_data.get_current_question()
        string += '<br>–<br>'
        string += self.game_data.get_current_answer()
        # fade in label with question and answer
        self.question_label.setText(string)
        if config.HIDE_QUESTION:
            # fade question label in ONLY when it was not faded out before
            helper.animate_widget(self.question_label, False)
        else:
            # else do what would be done when question had to be faded in
            self.on_answer_fadein()
        self.game_data.mark_question_as_complete()

    @QtCore.pyqtSlot(bool)
    def on_back_button(self, answer_correct):
        """Handles a pressed back button. Either the given answer was correct
        or not. Depending on that the points in the game data object are
        adjusted.

        :param answer_correct: whether the given answer was correct
        """
        if self.last_buzzed_team != -1:
            if answer_correct:
                self.game_data.add_points_to_team(self.last_buzzed_team)
            else:
                if config.PENALTY_WRONG_ANSWERS:
                    self.game_data.subtract_points_from_team(self.last_buzzed_team)
        self.main_gui.back_to_round_table()

    ##### methods concerning sound/audio #####

    def init_audio(self):
        # create background music object
        self.audio_output = Phonon.AudioOutput(Phonon.MusicCategory)
        self.background_music = Phonon.MediaObject()
        Phonon.createPath(self.background_music, self.audio_output)
        if config.LOOP_BACKGROUND_MUSIC:
            self.background_music.finished.connect(self.background_music.play)
        self.background_music.setCurrentSource(Phonon.MediaSource('./sounds/jeopardy.wav'))
        # create buzzer sound object
        self.audio_output2 = Phonon.AudioOutput(Phonon.MusicCategory)
        self.buzzer_sound = Phonon.MediaObject()
        Phonon.createPath(self.buzzer_sound, self.audio_output2)
        self.buzzer_sound.setCurrentSource(Phonon.MediaSource('./sounds/buzzer.wav'))

    def read_question(self):
        if config.AUDIO_SPEECH:
            from espeak import espeak
            espeak.synth(self.game_data.get_current_question())

    def play_buzzer_sound(self):
        if config.AUDIO_SFX:
            self.buzzer_sound.play()

    def play_background_music(self):
        if config.AUDIO_MUSIC:
            self.background_music.play()


class TeamViewPanel(QtGui.QWidget):
    """Panel showing all teams including their current points.

    TODO: Handle size automatically without depending on width and height from
    parent widget!

    :param game_data: instance of Game class including all game information
    """
    # constants for orientation parameter
    HORIZONTAL_ORIENTATION = 1
    VERTICAL_ORIENTATION = 2

    def __init__(self, parent, game_data, width, height, orientation):
        """Initialize panel for displaying team data."""
        super(TeamViewPanel, self).__init__(parent)
        self.game_data = game_data
        self.main_gui = parent
        self.points_label_dict = {}
        self.team_label_dict = {}
        # set orientation for team view panel
        if orientation == self.HORIZONTAL_ORIENTATION or orientation == self.VERTICAL_ORIENTATION:
            self.orientation = orientation
        else:
            self.orientation = self.VERTICAL_ORIENTATION
        # build gui widgets
        self.setFixedSize(width, height)
        self.create_fonts()
        self.setup_ui()
        # set style sheet for all team labels
        self.highlight_team(-1)

    def create_fonts(self):
        # set point size depending on settings and orientation
        if self.orientation == self.VERTICAL_ORIENTATION:
            if config.LOW_RESOLUTION:
                point_size = 20
            else:
                point_size = 26
        elif self.orientation == self.HORIZONTAL_ORIENTATION:
            if config.LOW_RESOLUTION:
                point_size = 26
            else:
                point_size = 32
        else:
            raise NotImplementedError()
        # set font with specified name and size
        self.team_font = QtGui.QFont(config.BASE_FONT)
        self.team_font.setPointSize(point_size)

    def setup_ui(self):
        if self.orientation == self.VERTICAL_ORIENTATION:
            self.setup_vertically()
        elif self.orientation == self.HORIZONTAL_ORIENTATION:
            self.setup_horizontally()
        else:
            raise NotImplementedError()

    def setup_vertically(self):
        layout = QtGui.QVBoxLayout()
        layout.addSpacing(50)
        # add labels for each team
        for i in range(config.MAX_TEAM_NUMBER):
            # add team names
            string = config.TEAM_NAMES[i]
            team_label = QtGui.QLabel(string)
            team_label.setFont(self.team_font)
            team_label.setAlignment(QtCore.Qt.AlignCenter |
                                    QtCore.Qt.AlignLeft)
            self.team_label_dict[i] = team_label
            layout.addWidget(team_label)
            # add point for team
            points_label = QtGui.QLCDNumber(self)
            #points_label.resize(200, 200)
            points_label.setSegmentStyle(QtGui.QLCDNumber.Flat)
            points_label.setFrameStyle(QtGui.QFrame.NoFrame)
            points_for_team = str(self.game_data.get_points_for_team(i))
            points_label.display(points_for_team)
            self.points_label_dict[i] = points_label
            layout.addWidget(points_label)
            layout.addSpacing(20)
        layout.addSpacing(50)
        self.setLayout(layout)

    def setup_horizontally(self):
        layout = QtGui.QHBoxLayout()
        layout.addSpacing(10)
        # add labels for each team
        for i in range(config.MAX_TEAM_NUMBER):
            team_box = QtGui.QVBoxLayout()
            # add team names
            string = config.TEAM_NAMES[i]
            team_label = QtGui.QLabel(string)
            team_label.setFont(self.team_font)
            team_label.setAlignment(QtCore.Qt.AlignCenter |
                                    QtCore.Qt.AlignLeft)
            self.team_label_dict[i] = team_label
            team_box.addWidget(team_label)
            # add point for team
            points_label = QtGui.QLCDNumber(self)
            points_label.setSegmentStyle(QtGui.QLCDNumber.Flat)
            points_label.setFrameStyle(QtGui.QFrame.NoFrame)
            points_for_team = str(self.game_data.get_points_for_team(i))
            points_label.display(points_for_team)
            self.points_label_dict[i] = points_label
            team_box.addWidget(points_label)
            layout.addLayout(team_box)
        layout.addSpacing(10)
        self.setLayout(layout)

    def highlight_team(self, team_id):
        """Highlights a given team identified by its team id. All other teams
        will be unhighlighted!
        """
        SELECTED_STYLE = 'background: red; color: white; border-radius: 15px; border-width: 4px;'
        for id, team_label in self.team_label_dict.items():
            if team_id == id:
                team_label.setStyleSheet(SELECTED_STYLE)
            else:
                team_label.setStyleSheet('')

    @QtCore.pyqtSlot()
    def on_update_points(self):
        """Sets all signals and slots for question view."""
        logger.info('Updating points for all teams...')
        for key, value in self.points_label_dict.items():
            new_points = str(self.game_data.get_points_for_team(key))
            logger.info('Team {} has {} points.'.format(key, new_points))
            self.points_label_dict[key].display(new_points)


class GameOverDialog(QtGui.QDialog):
    """Dialog showing which team has won first place."""
    def __init__(self, parent, game_data, width, height):
        """Initialize dialog for showing final score of game.

        :param parent: parent widget
        :param game_data: instance of Game() containing all necessary
                          information
        :param width: width of this dialog box
        :param height: height of this dialog box
        """
        super(GameOverDialog, self).__init__(parent)
        # set data for this dialog
        self.game_data = game_data
        self.main_gui = parent
        self.setFixedSize(width, height)
        # build gui and slots
        self.create_fonts()
        self.setup_ui()
        #self.set_signals_and_slots()

    def create_fonts(self):
        if config.LOW_RESOLUTION:
            self.title_font = QtGui.QFont(config.BASE_FONT)
            self.title_font.setPointSize(30)
            self.team_font = QtGui.QFont(config.BASE_FONT)
            self.team_font.setPointSize(26)
            self.points_font = QtGui.QFont(config.BASE_FONT)
            self.points_font.setPointSize(20)
        else:
            self.title_font = QtGui.QFont(config.BASE_FONT)
            self.title_font.setPointSize(36)
            self.team_font = QtGui.QFont(config.BASE_FONT)
            self.team_font.setPointSize(26)
            self.points_font = QtGui.QFont(config.BASE_FONT)
            self.points_font.setPointSize(20)

    def setup_ui(self):
        self.place_style = 'border:2px solid black;'
        self.grid = QtGui.QGridLayout()
        center_box = QtGui.QVBoxLayout()
        title_label = QtGui.QLabel(self.game_data.get_round_title())
        title_label.setFont(self.title_font)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        center_box.addWidget(title_label, QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter)
        center_box.addSpacing(2)
        center_box.addLayout(self.grid, QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter)
        self.setLayout(center_box)
        # set margins for whole layout
        margin = 40
        self.grid.setContentsMargins(margin, margin, margin, margin)
        # build widgets
        self.build_first_place()
        self.build_second_place()
        self.build_third_place()

    def build_first_place(self):
        box = QtGui.QVBoxLayout()
        team_name, points = self.game_data.get_placed_team(1)
        place_label = QtGui.QLabel(team_name)
        place_label.setFont(self.team_font)
        place_label.setAlignment(QtCore.Qt.AlignCenter)
        place_label.setStyleSheet(self.place_style)
        box.addWidget(place_label, QtCore.Qt.AlignHCenter)
        points_label = QtGui.QLabel(str(points))
        points_label.setFont(self.points_font)
        points_label.setAlignment(QtCore.Qt.AlignCenter)
        box.addWidget(points_label, QtCore.Qt.AlignHCenter)
        self.grid.addLayout(box, 1, 1)

    def build_second_place(self):
        box = QtGui.QVBoxLayout()
        team_name, points = self.game_data.get_placed_team(2)
        place_label = QtGui.QLabel(team_name)
        place_label.setFont(self.team_font)
        place_label.setAlignment(QtCore.Qt.AlignCenter)
        place_label.setStyleSheet(self.place_style)
        box.addWidget(place_label, QtCore.Qt.AlignHCenter)
        points_label = QtGui.QLabel(str(points))
        points_label.setFont(self.points_font)
        points_label.setAlignment(QtCore.Qt.AlignCenter)
        box.addWidget(points_label, QtCore.Qt.AlignHCenter)
        self.grid.addLayout(box, 2, 2)

    def build_third_place(self):
        box = QtGui.QVBoxLayout()
        team_name, points = self.game_data.get_placed_team(3)
        place_label = QtGui.QLabel(team_name)
        place_label.setFont(self.team_font)
        place_label.setAlignment(QtCore.Qt.AlignCenter)
        place_label.setStyleSheet(self.place_style)
        box.addWidget(place_label, QtCore.Qt.AlignHCenter)
        points_label = QtGui.QLabel(str(points))
        points_label.setFont(self.points_font)
        points_label.setAlignment(QtCore.Qt.AlignCenter)
        box.addWidget(points_label, QtCore.Qt.AlignHCenter)
        self.grid.addLayout(box, 3, 0)
