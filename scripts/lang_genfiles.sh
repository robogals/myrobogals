#!/bin/sh
cd ../myrobogals
django-admin.py makemessages -a
cd ../rgtemplates
django-admin.py makemessages -a
