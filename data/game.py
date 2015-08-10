
"""
pyPardy

Module for handling all game related data like teams and points.

@author: Christian Wichmann
"""


import logging

from data import config


logger = logging.getLogger('pyPardy.data')


# file name for storing information about points of all teams
POINTS_FILE = './points.log'


class Game():
    """Contains all necessary information about the current game.

    Included in this class are team number, buzzer ids for all teams, chosen
    round file, current question and its answer, etc.

    The team id and the buzzer id begins with 0. A value of -1 signals an
    error.
    """
    def __init__(self):
        self.reset_game(reset_points=True)
        # dictionary with the buzzer id for each team copied from configs
        # default
        self.buzzer_id_list = list(config.BUZZER_ID_FOR_TEAMS)
        self._current_round_data = None
        # open file for saving points information of all rounds
        self.points_file = open(POINTS_FILE, 'a')

    def __del__(self):
        # close file when destroying this object
        #self.points_file.close()
        pass

    @property
    def current_round_data(self):
        return self._current_round_data

    @current_round_data.setter
    def current_round_data(self, value):
        if value:
            self._current_round_data = value
            # write info to points file
            self.points_file.write('===== New round: {} =====\n'.format(self.get_round_title()))
            self.points_file.flush()
            # read question points from loaded data and set config option
            try:
                config.QUESTION_POINTS = int(self._current_round_data['question points'])
            except KeyError:
                logger.debug('Round does not include a setting for "question points"!')
        else:
            self._current_round_data = None

    ##### methods for generating information from raw data #####

    def get_number_of_topics(self):
        """Returns number of topics in current round.

        :returns: number of topics, or 0 if no round was chosen"""
        if self.current_round_data:
            return len(self.current_round_data['topics'])
        return 0

    def get_number_of_questions(self, topic):
        """Returns number of questions in chosen topic in current round.

        :returns: number of questions in chosen topic, or 0 if no round
                  was chosen"""
        if self.current_round_data:
            return len(self.current_round_data['topics'][topic]['questions'])
        return 0

    def get_topic_name(self):
        """Returns a string containing the name of the chosen topic."""
        if self.current_round_data:
            return self.current_round_data['topics'][self.current_topic]['title']

    def get_points_for_current_question(self):
        """Calculates and returns the points given for the current question as
        number.

        :returns: points for current question as number"""
        return (self.current_question + 1) * config.QUESTION_POINTS

    def get_current_question(self):
        """Returns a string containing the text of the current question."""
        questions = self.current_round_data['topics'][self.current_topic]['questions']
        return questions[self.current_question]['question']

    def get_current_answer(self):
        """Returns a string containing the answer of the current question."""
        questions = self.current_round_data['topics'][self.current_topic]['questions']
        return questions[self.current_question]['answer']

    def get_round_title(self):
        return self.current_round_data['title']

    ##### methods concerning status of questions #####

    def mark_question_as_complete(self, topic=None, question=None):
        """Marks current questions of current topic as completed."""
        if topic == None:
            topic = self.current_topic
        if question == None:
            question=self.current_question
        string = '{}-{}'.format(topic, question)
        self.played_questions_list.append(string)

    def was_question_completed(self, topic, question):
        """Marks current questions of current topic as completed."""
        string = '{}-{}'.format(topic, question)
        if string in self.played_questions_list:
            return True
        else:
            return False

    def is_round_complete(self):
        """Returns whether all questions of a given round were played.

        :returns: true, if all questions have been played"""
        for topic in range(self.get_number_of_topics()):
            for question in range(self.get_number_of_questions(topic)):
                if not self.was_question_completed(topic, question):
                    return False
        self.fix_ranking()
        return True

    def quit_round(self):
        for topic in range(self.get_number_of_topics()):
            for question in range(self.get_number_of_questions(topic)):
                if not self.was_question_completed(topic, question):
                    self.mark_question_as_complete(topic=topic, question=question)
        self.fix_ranking()

    ##### methods concerning points and team management #####

    def write_current_points_to_file(self):
        self.points_file.write('----- ')
        for team_id, team in self.team_points_dict.items():
            self.points_file.write(' * {}: {} * '.format(team_id, team))
        self.points_file.write(' -----\n')
        self.points_file.flush()

    def add_points_to_team(self, team_id):
        if team_id not in self.team_points_dict:
            raise ValueError('Invalid team id!')
        self.team_points_dict[team_id] += (self.current_question + 1) * config.QUESTION_POINTS
        self.write_current_points_to_file()

    def subtract_points_from_team(self, team_id):
        if team_id not in self.team_points_dict:
            raise ValueError('Invalid team id!')
        self.team_points_dict[team_id] -= (self.current_question + 1) * config.QUESTION_POINTS
        self.write_current_points_to_file() 

    def correct_points_by_100(self, team_id, add_points=True):
        """Corrects points for a given team by the number of points for a
        correct answer of the easiest question in a game round.

        :param team_id: id of the team for which points should be added or
                        subtracted
        :param add_points: whether to add points for given team or to subtract
                           them
        """
        if team_id not in self.team_points_dict:
            raise ValueError('Invalid team id!')
        if add_points:
            self.team_points_dict[team_id] += config.QUESTION_POINTS
        else:
            self.team_points_dict[team_id] -= config.QUESTION_POINTS

    def get_points_for_team(self, team_id):
        return self.team_points_dict[team_id]

    def fix_ranking(self):
        self.ranking = {}
        # create a set with all different points from the teams and sort them
        # in reverse order...
        list_of_points = sorted(set(self.team_points_dict.values()), reverse=True)
        place = 1
        # ...get for each and every points all teams that got the same amount
        # of points and count the places through to assign them to the teams.
        for place_points in list_of_points:
            for team in range(config.MAX_TEAM_NUMBER):
                if self.team_points_dict[team] == place_points:
                    self.ranking[place] = team
                    place += 1

    def get_placed_team(self, place):
        if self.is_round_complete() and (place in self.ranking):
            return (config.TEAM_NAMES[self.ranking[place]],
                    self.get_points_for_team(self.ranking[place]))
        else:
            return ()

    def set_buzzer_id_for_team(self, team_id, buzzer_id):
        """Sets buzzer id for a team.

        :param team_id: team id to be connected with the given buzzer id
        :param buzzer_id: buzzer id to be set for given team
        """
        logger.info('Setting buzzer id {} for team {}.'
                    .format(buzzer_id, team_id))
        # set buzzer id in config module
        config.BUZZER_ID_FOR_TEAMS[team_id] = buzzer_id
        # set internal state
        self.buzzer_id_list[team_id] = buzzer_id
        # TODO check if local dict is necessary or practical

    def get_team_by_buzzer_id(self, buzzer_id):
        """Returns the team id for a given buzzer id generated by the
        BuzzerReader object.

        :param buzzer_id: buzzer id for which to get team id
        """
        for team, buzzer in enumerate(self.buzzer_id_list):
            if buzzer == buzzer_id:
                return team
        return -1

    def reset_game(self, reset_points=False):
        """Reset all internal variables for the next game."""
        self.filename = ''
        self.current_round_data = None
        # number of the currently chosen topic, -1 if non was chosen
        self.current_topic = -1
        # number of the currently chosen question, -1 if non was chosen
        self.current_question = -1
        # list with all questions that have been played before
        self.played_questions_list = []
        # dictionary with points for all teams
        if not config.ADD_ROUND_POINTS or reset_points:
            self.team_points_dict = dict.fromkeys(range(config.MAX_TEAM_NUMBER), 0)


if __name__ == '__main__':
    pass
