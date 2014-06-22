
"""
pyPardy

Widgets for showing questions.

@author: Christian Wichmann
"""

import logging
from PyQt4 import QtGui
from PyQt4 import QtCore

from data import config
from gui import helper


ANIMATION_TIME = 1500


logger = logging.getLogger('pyPardy.gui')


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
        self.set_signals_and_slots()

    def create_fonts(self):
        base_font = 'Linux Biolinum O'
        #QtGui.QFontDatabase.addApplicationFont()
        self.title_font = QtGui.QFont(base_font)
        self.title_font.setPointSize(24)
        self.topic_font = QtGui.QFont(base_font)
        self.topic_font.setPointSize(18)
        self.question_font = QtGui.QFont(base_font)
        self.question_font.setPointSize(56)

    def setup_ui(self):
        self.box_layout = QtGui.QHBoxLayout()
        self.setLayout(self.box_layout)
        # build table
        self.box_layout.addLayout(self.build_table())
        # add team view widget
        self.team_view_panel = TeamViewPanel(self, self.game_data,
                                             200, self.height())
        self.box_layout.addWidget(self.team_view_panel)

    def build_table(self):
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.button_grid = QtGui.QGridLayout()
        margin = 25
        self.button_grid.setContentsMargins(margin, margin, margin, margin)
        # add title label
        title_label = QtGui.QLabel(self.game_data.current_round_data['title'])
        title_label.setFont(self.title_font)
        title_label.setAlignment(QtCore.Qt.AlignCenter |
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
        self.current_time = config.QUESTION_TIME
        self.last_buzzed_team = -1
        # create list of all animation objects
        self.animation_list = []
        self.setFixedSize(width, height)
        # build gui and slots
        self.create_fonts()
        self.setup_ui()
        self.set_signals_and_slots()
        self.start_timer()
        if config.AUDIO_SPEECH:
            self.read_question()

    def __del__(self):
        self.close_connection_to_buzzer()

    def create_fonts(self):
        base_font = 'Linux Biolinum O'
        self.question_font = QtGui.QFont(base_font)
        self.question_font.setPointSize(36)
        self.button_font = QtGui.QFont(base_font)
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
        topic_button = QtGui.QPushButton(self.topic)
        topic_button.setEnabled(False)
        topic_button.setFont(self.button_font)
        self.grid.addWidget(topic_button, 0, 0)
        points_button = QtGui.QPushButton(str(self.points))
        points_button.setEnabled(False)
        points_button.setFont(self.button_font)
        self.grid.addWidget(points_button, 0, 1)

    def build_control_buttons(self):
        # add button for showing the answer of the question
        self.show_answer_button = QtGui.QPushButton('Antwort...')
        self.show_answer_button.setFont(self.button_font)
        self.hide_widget(self.show_answer_button)
        self.grid.addWidget(self.show_answer_button, 2, 0)
        # add button for going back to question table
        self.answer_correct_button = QtGui.QPushButton('Richtig!')
        self.answer_correct_button.setFont(self.button_font)
        self.hide_widget(self.answer_correct_button)
        self.grid.addWidget(self.answer_correct_button, 2, 1)
        self.answer_incorrect_button = QtGui.QPushButton('Falsch!')
        self.answer_incorrect_button.setFont(self.button_font)
        self.hide_widget(self.answer_incorrect_button)
        self.grid.addWidget(self.answer_incorrect_button, 2, 2)

    def build_labels(self):
        # add question label
        self.question_label = QtGui.QLabel(self.game_data.get_current_question())
        self.question_label.setFont(self.question_font)
        self.question_label.setLineWidth(25)
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(QtCore.Qt.AlignCenter |
                                         QtCore.Qt.AlignHCenter)
        self.grid.addWidget(self.question_label, 1, 0, 1, 4)
        # add label for team that buzzered first
        self.team_to_answer_label = QtGui.QLabel('')
        self.team_to_answer_label.setFont(self.question_font)
        self.grid.addWidget(self.team_to_answer_label, 0, 3)

    def build_timer_widgets(self):
        # add timer
        self.timer_lcd = QtGui.QLCDNumber(self)
        self.timer_lcd.resize(200, 200)
        self.timer_lcd.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.timer_lcd.setFrameStyle(QtGui.QFrame.NoFrame)
        #self.timer_lcd.setStyleSheet("border: 0px")
        #self.set_lcd_colors()
        self.grid.addWidget(self.timer_lcd, 2, 3)

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
        self.buzzer_connector = helper.get_buzzer_connector()
        self.buzzer_connector.buzzing.connect(self.on_buzzer_pressed)

    def close_connection_to_buzzer(self):
        """Closes the connection between the BuzzerConnector and the callable
        method 'on_buzzer_pressed' on this class.
        """
        self.buzzer_connector.buzzing.disconnect(self.on_buzzer_pressed)
        self.buzzer_connector = None

    ##### timer methods #####

    def start_timer(self):
        """Builds timer that will update game time every 1000 ms."""
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_update_lcd)
        self.timer.start(1000)
        self.on_update_lcd()

    def stop_timer(self):
        self.timer_lcd.display(self.current_time)
        self.timer.stop()

    ##### helper methods #####

    def animate_widget(self, widget, fade_out, hook=None):
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
        self.animation_list.append(anim)
        anim.start()
        if hook:
            anim.finished.connect(hook)

    def hide_widget(self, widget):
        # generate effect class
        effect = QtGui.QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        # set opacity
        effect.setOpacity(0.0)

    ##### slot methods #####

    @QtCore.pyqtSlot(int)
    def on_buzzer_pressed(self, buzzer_id):
        """Handles a pressed buzzer and registers the team.

        :param buzzer_id: buzzer id delivered by BuzzerReader()"""
        logger.info('Getting buzzer id ({}) from buzzer API.'.format(buzzer_id))
        # play buzzer sound
        self.play_buzzer_sound()
        # get team id from buzzer id
        team_id = self.game_data.get_team_by_buzzer_id(buzzer_id)
        string = 'Team {}'.format(team_id + 1)
        self.last_buzzed_team = team_id
        # update gui widgets
        self.team_to_answer_label.setText(string)
        self.stop_timer()
        self.animate_widget(self.question_label, True,
                            self.on_question_fadeout)

    @QtCore.pyqtSlot()
    def on_update_lcd(self):
        if self.current_time > 0:
            # decrement time when not yet expired
            self.current_time -= 1
            self.timer_lcd.display(self.current_time)
        else:
            # stop timer and fade question out
            self.stop_timer()
            self.animate_widget(self.question_label, True,
                                self.on_question_fadeout)

    @QtCore.pyqtSlot()
    def on_question_fadeout(self):
        logger.info('Question has been faded out.')
        self.animate_widget(self.show_answer_button, False)

    @QtCore.pyqtSlot()
    def on_answer_fadein(self):
        logger.info('Question has been faded out.')
        self.animate_widget(self.answer_correct_button, False)
        self.animate_widget(self.answer_incorrect_button, False)

    @QtCore.pyqtSlot()
    def on_show_answer_button(self):
        logger.info('Answer is shown.')
        self.question_label.setText(self.game_data.get_current_answer())
        self.animate_widget(self.question_label, False, self.on_answer_fadein)
        self.game_data.mark_question_as_complete()

    @QtCore.pyqtSlot(bool)
    def on_back_button(self, answer_correct):
        """Handles a pressed back button. Either the given answer was correct
        or not. Depending on that the points in the game data object are
        adjusted.

        :param answer_correct: whether the given answer was correct
        """
        if answer_correct:
            if self.last_buzzed_team != -1:
                self.game_data.add_points_to_team(self.last_buzzed_team)
        self.main_gui.back_to_round_table()

    ##### methods concering sound/audio #####

    def read_question(self):
        from espeak import espeak
        espeak.synth(self.game_data.get_current_question())

    def play_buzzer_sound(self):
        if config.AUDIO_SFX:
            buzzer_sound = QtGui.QSound("./sounds/buzzer.wav")
            buzzer_sound.play()


class TeamViewPanel(QtGui.QWidget):
    """Panel showing all teams including their current points.

    :param game_data: instance of Game class including all game information
    """
    def __init__(self, parent, game_data, width, height):
        """Initialize panel for displaying team data."""
        super(TeamViewPanel, self).__init__(parent)
        self.game_data = game_data
        self.main_gui = parent
        self.points_label_dict = {}
        self.setFixedSize(width, height)
        self.create_fonts()
        self.setup_ui()

    def create_fonts(self):
        base_font = 'Linux Biolinum O'
        self.team_font = QtGui.QFont(base_font)
        self.team_font.setPointSize(24)
        self.points_font = QtGui.QFont(base_font)
        self.points_font.setPointSize(32)

    def setup_ui(self):
        layout = QtGui.QVBoxLayout()
        layout.addSpacing(10)
        # add labels for each team
        for i in range(config.MAX_TEAM_NUMBER):
            # add team names
            string = 'Team {}'.format(i + 1)
            team_label = QtGui.QLabel(string)
            team_label.setFont(self.team_font)
            team_label.setAlignment(QtCore.Qt.AlignCenter |
                                    QtCore.Qt.AlignLeft)
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
        layout.addSpacing(10)
        self.setLayout(layout)

    @QtCore.pyqtSlot()
    def on_update_points(self):
        """Sets all signals and slots for question view."""
        logger.info('Updating points for all teams...')
        for key, value in self.points_label_dict.items():
            new_points = str(self.game_data.get_points_for_team(key))
            logger.info('Team {} has {} points.'.format(key, new_points))
            self.points_label_dict[key].display(new_points)
