
"""
pyPardy

Package for all gui components.

@author: Christian Wichmann
"""


import os
from PyQt4 import QtGui


def load_shipped_font():
    """Loads shipped fonts for same look on all plattforms."""
    FONT_DIRECTOY = './fonts'
    FONT_NAMES = ('LinuxBiolinum.ttf', )
    for font in FONT_NAMES:
        # create path string for each font file
        # INFO: It seems that QApplication must be initialized before a new
        # font can be loaded. Without the colon a memory error is thrown by
        # pyQt! With the colon it seems to be working.
        font_path = ':' + os.path.join(FONT_DIRECTOY, font)
        QtGui.QFontDatabase.addApplicationFont(font_path)


load_shipped_font()
