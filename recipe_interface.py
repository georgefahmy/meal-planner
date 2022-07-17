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


font = ("Arial", 16)

# ______RECIPE LAYOUT_______

main_recipe_info = [
    [
        sg.Frame("New Recipe",
            size=(600, 120),
            element_justification="c",
            layout=[
                [
                    sg.Text("Title", font=font, size=(16, 1)),
                    sg.Input(font=font, key="recipe_title", expand_x=True)
                ],
                [
                    sg.Text("Subtitle (optional)", font=font, size=(16, 1)),
                    sg.Input(font=font, key="recipe_subtitle", expand_x=True)
                ],
                [
                    sg.Text("Category", font=font, size=(16, 1)),
                    sg.Combo(
                        values=meal_categories[1:],
                        font=font,
                        key="recipe_category",
                        readonly=True,
                        expand_x=True,
                    )
                ],
            ]
        )
    ]
]

layout = main_recipe_info

recipe_window = sg.Window("Recipe Interface", layout=layout,
                   resizable=True, size=(800, 660), element_justification="c", finalize=True)

while True:
    event, values = recipe_window.read()
    if event == sg.WIN_CLOSED:
        break

    if event:
        # DEBUG to print out the events and values
        print(event, values)
