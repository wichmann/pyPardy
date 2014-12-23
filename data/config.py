
"""
pyPardy

Configuration module for pyPardy.

@author: Christian Wichmann
"""


import logging
import json


logger = logging.getLogger('pyPardy.data')


# name of the application that is shown in the GUI
APP_NAME = 'pyPardy'
# whether debug mode is activated
DEBUG = False
# file name for configuration data
CONFIG_FILE_NAME = 'settings.json'


##### Game related settings #####

# maximum number of teams
MAX_TEAM_NUMBER = 3
# time for answering a questions in seconds
QUESTION_TIME = 60
# points that are added for every question in a given topic
QUESTION_POINTS = 100
# whether to decrease points when team answer wrongly
PENALTY_WRONG_ANSWERS = False
# whether to add points from all played round
ADD_ROUND_POINTS = False
# whether to hide question after buzzer was pressed
HIDE_QUESTION = False
# whether to allow multiple teams to answer a single question
ALLOW_ALL_TEAMS_TO_ANSWER = True


##### Audio related settings #####

# whether to use text-to-speech to read question
AUDIO_SPEECH = False
# whether to play sound effects when buzzer was hit
AUDIO_SFX = False
# whether to play background music while showing the question
AUDIO_MUSIC = False
# whether to loop background music
LOOP_BACKGROUND_MUSIC = False


##### Graphics related settings #####

# font name for most of the GUI
BASE_FONT = 'Linux Biolinum O'
# whether to design graphical user interface for lower resolutions,
# e.g. 1024x768
LOW_RESOLUTION = False
# whether to show main GUI in fullscreen mode
FULLSCREEN = False
# whether to use a high contrast theme
HIGH_CONTRAST = False


##### Buzzer related settings #####

# predefined buzzer ids for teams
BUZZER_ID_FOR_TEAMS = [1, 2, 3, 4]
# predefined team names
TEAM_NAMES = ['Rot', 'Grün', 'Gelb', 'Blau']


def load_config_from_file():
    """Loads configuration settings from file and stores the values in global
    variables.

    Alternative code:
    # globals().update(the_dict) or locals().update(the_dict).
    """
    logger.info('Loading config from file...')
    try:
        with open(CONFIG_FILE_NAME, 'r') as config_file:
            data = json.load(config_file)
            for element, value in data.items():
                # if element is variable in this module...
                if element in globals():
                    # set global variable in this module when type is correct
                    try:
                        setting = globals()[element]
                        if type(setting) == int:
                            globals()[element] = int(value)
                        elif type(setting) == bool:
                            globals()[element] = bool(value)
                        elif type(setting) == str:
                            globals()[element] = str(value)
                        elif type(setting) == list:
                            globals()[element] = list(value)
                        else:
                            raise ValueError()
                    except ValueError:
                        logger.error('Wrong data type in settings file, ignoring value for "{}" element!'.format(element))
    except FileNotFoundError as e:
        logger.error('Configuration file not found: ' + e)


def save_config_to_file():
    logger.info('Saving config to file...')
    with open(CONFIG_FILE_NAME, 'w') as config_file:
        # build dict with all info
        config_data = dict()
        for var in globals().keys():
            if not var.startswith("__") and all(char.isupper() or char == '_' for char in var):
                config_data[var] = eval(var)
        # dict( (name,eval(name)) for name in ['some','list','of','vars'] )
        # save dict to json file
        json.dump(config_data, config_file, indent=4, sort_keys=True)


if __name__ == '__main__':
    pass
