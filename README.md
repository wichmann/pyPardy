pyPardy
=======

DESCRIPTION
-----------
pyPardy is a game similar to Jeopardy(tm).


KNOWN PROBLEMS AND BUGS
-----------------------


LICENSE
-------
pyPardy is released under the GNU General Public License v2 or newer.


REQUIREMENTS
------------
pyPardy requires Python 3.

For the correct rendering the font "Linux Biolinum O" has to be installed.

To use the USB buzzer, libusb version 1.0 and the wrapper python-libusb1 have
to be installed. The file '10-buzzer.rules' contains a udev rule to access the
usb device without root access. Just copy it to /etc/udev/rules.d and change
the GROUP attribute to your needs.


THIRD PARTY SOFTWARE
--------------------
pyPardy includes parts of or links with the following software packages and 
programs, so give the developers lots of thanks sometime! 

* Some cliparts from opencliparts.org: 
   - http://openclipart.org/detail/190592/button-by-tobbi-190592
* Some free sound files from freesound.org
   - https://www.freesound.org/people/hypocore/sounds/164089/
* 
