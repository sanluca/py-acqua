#!/bin/sh
# compile il file po nel file acqua.mo
msgfmt $1 -o "locale/$2/en/LC_MESSAGES/acqua.mo"
