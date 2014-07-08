
"""
pyPardy

Module for reading and using round data, e.g. questions/answers.

TODO:
 - Add support for image or audio instead of or additional to questions.
 - Improve verify process.

@author: Christian Wichmann
"""

import glob
import os
import json
import logging

from data.helper import memoized

logger = logging.getLogger('pyPardy.data')


ROUND_DATA_EXTENSION = 'round'
ROUND_DATA_PATH = 'rounds/'

MAXIMUM_TOPIC_COUNT = 6
MAXIMUM_QUESTION_COUNT = 7


def get_available_round_data():
    """Checks for all round data files in current directory and returns list
    of all available data file names.

    Only files with '.round' extension are recognized!

    :returns: all available rounds including their name and the filename with
              the round data
    """
    search_directory = '.'
    round_data = []
    os.chdir(search_directory)
    extension = '*.{}'.format(ROUND_DATA_EXTENSION)
    for filename in glob.glob(os.path.join(ROUND_DATA_PATH, extension)):
        data_ok = check_round_file(filename)
        title = load_round_data_file(filename)['title']
        if data_ok:
            round_data.append((title, filename))
    return round_data


def check_round_file(filename):
    """Checks whether a given file contains valid JSON data."""
    return True


@memoized
def load_round_data_file(filename):
    """Loads a given round data file and returns data from it.

    :param filename: filename to load round data from
    :returns: data from round data file
    """
    json_data_file = open(filename)
    data = json.load(json_data_file)
    if not verify_round_data(data):
        logger.error('Error in round data file: {}.'.format(filename))
    json_data_file.close()
    return data


def verify_round_data(data):
    """Verifys the loaded round data from file.

    :returns: True, if data is valid round data
    """
    try:
        # check if title exists and if number of topics is valid
        data['title']
        if len(data['topics']) > MAXIMUM_TOPIC_COUNT:
            raise ValueError('To much topics in round data file.')
        questions_per_topic = len(data['topics'][0]['questions'])
        for topic in data['topics']:
            # check if topic title exists and if number of questions in topic
            # is valid
            topic['title']
            if len(topic['questions']) > MAXIMUM_QUESTION_COUNT:
                raise ValueError('Too much questions in round "{}" in round data file.'.format(topic['title']))
            # check if all topics have same number of questions
            if questions_per_topic != len(topic['questions']):
                raise ValueError('Not all topics have the same number of questions.')
            # check if all questions have answers :-)
            for question in topic['questions']:
                question['question']
                question['answer']
    except Exception as e:
        logger.error(e)
        return False
    return True


def pprint_round_data(data):
    print('=== {} ==='.format(data['title']))
    for topic in data['topics']:
        print('-- {} --'.format(topic['title']))
        for question in topic['questions']:
            print('Question: {}'.format(question['question']))
            print('Answer: {}'.format(question['answer']))


if __name__ == '__main__':
    pass
