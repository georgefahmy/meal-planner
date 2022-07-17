from random import choice
import PySimpleGUI as sg
import datetime
import json
import os
import sys
import base64
import shutil
import textwrap

from utils.sql_functions import (
    add_meal,
    read_all_meals,
    read_specific_meals,
    update_meal_name,
    update_meal_category,
    update_meal_ingredients,
    remove_meal,
    add_plan,
    read_all_plans,
    read_current_plans,
    create_connection,
)
from utils.custom_date_picker import popup_get_date
from utils.make_database import make_database

try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()

file_path = os.path.join(wd, "settings.json")

settings = json.load(open(file_path, "r"))
db_file = os.path.join(wd, "database.db")
meal_categories = list(dict.fromkeys(settings["meal_categories"]))


font = ("Arial", 14)

# ______RECIPE LAYOUT_______

main_recipe_info = [
    [sg.Text("Title", font=font), sg.Input(font=font, key="recipe_title")],
    [sg.Text("Subtitle (optional)", font=font), sg.Input(font=font, key="recipe_subtitle")],
    [
        sg.Text("Category", font=font),
        sg.Combo(values=meal_categories, font=font, key="recipe_category", readonly=True),
    ],
]
layout = main_recipe_info

sg.Window("Recipe Interface", layout=layout, finalize=True)
