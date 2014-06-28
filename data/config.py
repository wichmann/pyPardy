
"""
pyPardy

Configuration module for pyPardy.

@author: Christian Wichmann
"""


import logging


logger = logging.getLogger('pyPardy.data')


APP_NAME = "pyPardy!"
# maximum number of teams
MAX_TEAM_NUMBER = 3
# time for answering a questions in seconds
QUESTION_TIME = 10
# points that are added for every question in a given topic
QUESTION_POINTS = 100
# whether to use text-to-speech to read question
AUDIO_SPEECH = False
# whether to play sound effects when buzzer was hit
AUDIO_SFX = False
# whether to play background music while showing the question
AUDIO_MUSIC = True

# predefined buzzer ids for teams
BUZZER_ID_FOR_TEAMS = {1: 1, 2: 2, 3: 3, 4: 4}


def load_config_from_file():
    logger.info('Loading config from file...')
    raise NotImplementedError()


def save_config_to_file():
    logger.info('Saving config to file...')
    raise NotImplementedError()


if __name__ == '__main__':
    pass
