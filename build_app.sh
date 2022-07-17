#!/bin/bash

INVENV=$(python3 -c 'import sys; print( True if "virtual" in sys.prefix else False)')

if [ $INVENV == "True" ]; then
    echo "Please deactivate the virtual environment and run again"
    exit 0
else
    pip3.10 install -r requirements.txt
    python3.10 setup.py py2app
fi
