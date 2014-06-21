#! /usr/bin/env python3

import sys
from cx_Freeze import setup, Executable


# Dependencies are automatically detected, but it might need fine tuning.
buildOptions = dict(packages=[], excludes=[])

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable('pyPardy.py', base=base)
]

setup(
    name='pyPardy',
    version='0.1',
    author='Christian Wichmann',
    author_email='christian@freenono.org',
    packages=['data', 'gui'],
    url='',
    license='LICENSE',
    description='Jeopardy(tm) game system',
    options=dict(build_exe=buildOptions),
    executables=executables
)
