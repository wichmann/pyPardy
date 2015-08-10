
pyPardy
=======

Building i18n files
-------------------

Extracting all messages from source files:

    pybabel extract gui/ > locale/pyPardy.pot

Initialize each locale that should be supported:

    pybabel init -l de_DE -d ./locale -i ./locale/messages.pot

Creating mo files from translated po files:

    pybabel compile -f -d ./locale

Updating messages on po files from source:

    pybabel update -l de_DE -d ./locale/ -i ./locale/messages.pot

Alternatively, you can use xgettext.
