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
    "resources",
    "resources/burger.icns",
    "utils",
]
OPTIONS = {"iconfile": "/Users/GFahmy/Documents/projects/meal-planner/resources/burger.icns"}

setup(
    app=APP,
    name="Meal Planner PRO",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app", "PySimpleGUI", "altgraph", "modulegraph", "macholib"],
    version="2.0.0",
    author="George Fahmy",
    description="Meal Planner PRO",
    long_description="""Meal Planner PRO is a one stop shop for all your meal planning. You can add
        all the meals and food you enjoy and lvoe into your database, including all the ingredients
        to make that food. From there, you can build out meal plans, and shopping lists, and even
        share the plans with friends and family!""",
)
