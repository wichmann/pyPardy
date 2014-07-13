
"""
pyPardy

Configuration module for pyPardy.

@author: Christian Wichmann
"""


import logging


logger = logging.getLogger('pyPardy.data')


# name of the application that is shown in the GUI
APP_NAME = "pyPardy!"
# whether debug mode is activated
DEBUG = False


##### Game related settings #####

# maximum number of teams
MAX_TEAM_NUMBER = 3
# time for answering a questions in seconds
QUESTION_TIME = 60
# points that are added for every question in a given topic
QUESTION_POINTS = 100


##### Audio related settings #####

# whether to use text-to-speech to read question
AUDIO_SPEECH = False
# whether to play sound effects when buzzer was hit
AUDIO_SFX = True
# whether to play background music while showing the question
AUDIO_MUSIC = True


##### Graphics related settings #####

# font name for most of the GUI
BASE_FONT = 'Linux Biolinum O'
# whether to design graphical user interface for lower resolutions,
# e.g. 1024x768
LOW_RESOLUTION = True
# whether to show main GUI in fullscreen mode
FULLSCREEN = True


##### Buzzer related settings #####

# predefined buzzer ids for teams
BUZZER_ID_FOR_TEAMS = [1, 2, 3, 4]
# predefined team names
TEAM_NAMES = ['Team 1', 'Team A', 'Team α', 'Team あ']


def load_config_from_file():
    logger.info('Loading config from file...')
    raise NotImplementedError()


def save_config_to_file():
    logger.info('Saving config to file...')
    raise NotImplementedError()


if __name__ == '__main__':
    pass
