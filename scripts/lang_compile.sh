#!/bin/sh
cd ../myrobogals
django-admin.py compilemessages
cd ../rgtemplates
django-admin.py compilemessages
