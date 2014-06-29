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


def get_available_round_data():
    """Checks for all round data files in current directory and returns list
    of all available data file names.

    Only files with '.round' extension are recognized!

    :returns: all available files with round data
    """
    search_directory = '.'
    round_data = []
    os.chdir(search_directory)
    for filename in glob.glob('rounds/*.{}'.format(ROUND_DATA_EXTENSION)):
        data_ok = check_round_file(filename)
        if data_ok:
            round_data.append(filename)
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
