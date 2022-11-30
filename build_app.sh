#!/bin/bash

INVENV=$(python3 -c 'import sys; print( True if "virtual" in sys.prefix else False)')
VERSION=v$(python3 setup.py --version)

if [ $INVENV == "True" ]; then
    echo "Please deactivate the virtual environment and run again"
    exit 0
else
    rm -rf build dist
    pip3 install -r requirements.txt
    python3 setup.py py2app
    cd dist
    ln -s /Applications/
    echo "Creating Installation Image"
    hdiutil create -srcfolder . -volname "Meal Planner Pro" meal-planner-pro.dmg
    rm -rf "Meal Planner PRO.app"
    rm ./Applications
    cd ..
    echo "Creating release and uploading app to github"
    gh release create $VERSION dist/*.dmg -t "Meal Planner PRO $VERSION" -F resources/changelog.md
fi
