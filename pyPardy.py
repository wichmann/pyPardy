#! /usr/bin/env python3

"""
pyPardy

Main starter for pyPardy.

Python dependencies:
 - PyQt4.phonon
 - libusb
 - python-libusb1
 - espeak

@author: Christian Wichmann
"""

import logging
import logging.handlers
import sys

from data import round
from data import config
from gui import gui


def create_logger():
    """Creates logger for this application."""
    LOG_FILENAME = 'pyPardy.log'
    logger = logging.getLogger('pyPardy')
    logger.setLevel(logging.DEBUG)
    log_to_file = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                                       maxBytes=262144,
                                                       backupCount=5)
    log_to_file.setLevel(logging.DEBUG)
    logger.addHandler(log_to_file)
    log_to_screen = logging.StreamHandler(sys.stdout)
    log_to_screen.setLevel(logging.INFO)
    logger.addHandler(log_to_screen)
    return logger


if __name__ == '__main__':
    logger = create_logger()
    logger.info('Starting pyPardy...')   
    config.load_config_from_file()
    if config.DEBUG:
        # print all available round data to stdout when in debug mode
        list_of_round_files = round.get_available_round_data()
        for title, filename in list_of_round_files:
            data = round.load_round_data_file(filename)
            round.pprint_round_data(data)
    gui.start_gui()
