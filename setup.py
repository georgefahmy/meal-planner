from setuptools import find_packages, setup

VERSION = open("resources/VERSION", "r").read().strip()

APP = ["planner_app.py"]
DATA_FILES = [
    "database.db",
    "settings.json",
    "resources",
    "resources/burger.icns",
    "utils",
    "server_info.json",
]
OPTIONS = {
    "iconfile": "/Users/GFahmy/Documents/projects/meal-planner/resources/burger.icns",
    "arch": "x86_64",
}

setup(
    app=APP,
    version=VERSION,
    name="Meal Planner PRO",
    url="https://github.com/georgefahmy/meal-planner",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=[
        "py2app",
        "altgraph",
        "modulegraph",
        "macholib",
        "paramiko",
        "PySimpleGUI",
        "recipe-scrapers",
        "pillow",
    ],
    packages=find_packages(),
    license="GNU GENERAL PUBLIC LICENSE",
    author="George Fahmy",
    description="Meal Planner PRO",
    python_requires=">=3.6",
    long_description="""Meal Planner PRO is a one stop shop for all your meal planning. You can add
        all the meals and food you enjoy and lvoe into your database, including all the ingredients
        to make that food. From there, you can build out meal plans, and shopping lists, and even
        share the plans with friends and family!""",
)
