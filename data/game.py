
"""
pyPardy

Module for handling all game related data like teams and points.

@author: Christian Wichmann
"""


import logging

from data import config


logger = logging.getLogger('pyPardy.data')


class Game():
    """Contains all necessary information about the current game.

    Included in this class are team number, buzzer ids for all teams, chosen
    round file, current question and its answer, etc."""
    def __init__(self):
        self.filename = ''
        self.current_round_data = None
        # number of the currently chosen topic, -1 if non was chosen
        self.current_topic = -1
        # number of the currently chosen question, -1 if non was chosen
        self.current_question = -1
        # dictionary with the buzzer id for each team
        self.buzzer_id_list = {}
        # list with all questions that have been played before
        self.played_questions_list = []

    ##### methods for generating information from raw data #####

    def get_number_of_topics(self):
        """Returns number of topics in current round.

        :returns: number of topics, or 0 if no round was chosen"""
        if self.current_round_data:
            return len(self.current_round_data['topics'])
        return 0

    def get_number_of_questions(self, topic):
        """Returns number of questions in chosen topic in current round.

        :returns: number of questions in chosen topic, or 0 if no round was chosen"""
        if self.current_round_data:
            return len(self.current_round_data['topics'][topic]['questions'])
        return 0

    def get_topic_name(self):
        """Returns a string containing the name of the chosen topic."""
        if self.current_round_data:
            return self.current_round_data['topics'][self.current_topic]['title']

    def get_points_for_current_question(self):
        """Calculates and returns the points given for the current question as number.

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

    ##### methods concerning status of questions #####

    def mark_question_as_complete(self):
        """Marks current questions of current topic as completed."""
        string = '{}-{}'.format(self.current_topic, self.current_question)
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
        return True

    ##### methods concerning points and team management #####

    def add_points_to_team(self):
        pass

    def get_points_for_team(self, team_id):
        # FIXME save and use correct points
        import random
        return random.randint(0, 1000)


class Team():
    last_used_team_id = 0

    def __init__(self, team_name, buzzer_id):
        self.team_name = team_name
        self.buzzer_id = buzzer_id
        # increment team id and assign it
        Team.last_used_team_id += 1
        self.team_id = Team.last_used_team_id


class Teams():
    def __init__(self):
        self.team_list = []

    def add_team(self, team_name, buzzer_id=0):
        if buzzer_id == 0:
            logger.warning('No buzzer id assigned yet!')
        new_team = Team(team_name, buzzer_id)
        self.teamList.append(new_team)
        team_list_string = ', '.join(str(i) for i in self.getTeamList())
        logger.info("New team list: {}".format(team_list_string))

    def remove_team(self, team_name):
        for team in self.team_list:
            if team.get_team_list() == team_name:
                self.team_list.remove(team)

    def get_team_by_name(self, team_name):
        for team in self.team_list:
            if team.team_name == team_name:
                return team

    def load_teams_from_file(self):
        logger.error("Loading teams not yet implemented.")

    def save_teams_to_file(self):
        logger.error("Saving teams not yet implemented.")

    def get_team_list(self):
        team_names_list = []
        for team in self.teamList:
            team_names_list.append(team.team_name)
        return team_names_list


if __name__ == '__main__':
    pass
