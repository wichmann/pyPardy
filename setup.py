#! /usr/bin/env python3

import sys
from cx_Freeze import setup, Executable


# Dependencies are automatically detected, but it might need fine tuning.
includefiles = ['windows/libusb-1.0.dll',
                ('icons/buzzer.png', 'icons/buzzer.png'),
                'README.md',
                'LICENSE',
                'C:\\Windows\\SysWOW64\\msvcr110.dll']
excludes = []
packages = []
buildOptions = {'packages': packages,
                'excludes': excludes,
                'include_files':includefiles
                }

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable('pyPardy.py', base=base),
    Executable('pyPardyEdit.py', base=base)
]

setup(
    name='pyPardy',
    #long_description='',
    keywords='game jeopardy',
    version='0.2',
    author='Christian Wichmann',
    author_email='christian@freenono.org',
    packages=['data', 'gui'],
    url='',
    license='LICENSE',
    description='Jeopardy(tm) game system',
    platforms=['any'],
    classifiers=[
    'Intended Audience :: End Users/Desktop',
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
    'Operating System :: OS Independent',
    'Natural Language :: English',
    'Natural Language :: German',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Games/Entertainment',
    ],
    options=dict(build_exe=buildOptions),
    executables=executables, requires=['PyQt4', 'libusb1'],
    #data_files=[('libs', 'windows/libusb-1.0.dll'),
    #            ('icons', 'icons/buzzer.png')],
)
