#! /usr/bin/env python3

"""
pyPardy

Module for reading and using round data, e.g. questions/answers.

@author: Christian Wichmann
"""

import glob
import os
import json


ROUND_DATA_EXTENSION = 'round'
ROUND_DATA_PATH = 'rounds/'


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


def load_round_data_file(filename):
    """Loads a given round data file and returns data from it.

    :param filename: filename to load round data from
    :returns: data from round data file
    """
    json_data_file = open(filename)
    data = json.load(json_data_file)
    json_data_file.close()
    return data


def verify_round_data():
    """Verifys the loaded round data from file."""
    pass


def pprint_round_data(data):
    print('=== {} ==='.format(data['title']))
    for topic in data['topics']:
        print('-- {} --'.format(topic['title']))
        for question in topic['questions']:
            print('Question: {}'.format(question['question']))
            print('Answer: {}'.format(question['answer']))


if __name__ == '__main__':
    pass
