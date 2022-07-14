"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ["planner_app.py"]
DATA_FILES = [
    "database.db",
    "settings.json",
    "resources/",
]
OPTIONS = {"iconfile": "/Users/GFahmy/Documents/projects/meal-planner/resources/burger.icns"}

setup(
    app=APP,
    name="Meal Planner PRO",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app", "PySimpleGUI"],
    version="1.0.1",
    author="George Fahmy",
    description="Meal Planner PRO",
    long_description="""Meal Planner PRO""",
)