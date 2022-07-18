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
    sg.Frame(
        "New Recipe",
        layout=[
            [
                sg.Text("Title", font=font, size=(16, 1)),
                sg.Input(font=font, key="recipe_title", expand_x=True),
            ],
            [
                sg.Text("Subtitle (optional)", font=font, size=(16, 1)),
                sg.Input(font=font, key="recipe_subtitle", expand_x=True),
            ],
            [
                sg.Text("Category", font=font, size=(16, 1)),
                sg.Combo(
                    values=meal_categories[1:],
                    font=font,
                    key="recipe_category",
                    readonly=True,
                    expand_x=True,
                ),
            ],
        ],
        element_justification="c",
        key="new_recipes_frame",
        expand_x=True,
        relief="raised",
    )
]


def new_ingredient(i, j):
    return [
        [
            sg.Input(font=font, key=f"section_{j}_ingredient_{i}", expand_x=True, focus=True),
            sg.Button(
                "X",
                font=("Arial Bold", 14),
                key=f"section_{j}_remove_ingredient_{i}",
                enable_events=True,
            ),
        ],
    ]


def new_recipe_section(j):
    return [
        [
            sg.Frame(
                "Recipe Section",
                layout=[
                    [
                        sg.Text("", expand_x=True),
                        sg.Button(
                            "- Remove Section", key=f"remove_recipe_section_{j}", enable_events=True
                        ),
                    ],
                    [
                        sg.Frame(
                            "Ingredients",
                            layout=[
                                [
                                    sg.Text("Ingredients: ", font=("Arial Bold", 14)),
                                    sg.Text(
                                        "Press 'Enter' to add another ingredient",
                                        font=("Arial Italic", 12),
                                    ),
                                    sg.Button("(i) Tips", key="tips_button", enable_events=True),
                                ],
                                [
                                    sg.Input(
                                        font=font, key=f"section_{j}_ingredient_{0}", expand_x=True
                                    ),
                                    sg.Button(
                                        "X",
                                        font=("Arial Bold", 14),
                                        key=f"section_{j}_remove_ingredient_{0}",
                                        enable_events=True,
                                    ),
                                    sg.Button(
                                        "Submit",
                                        visible=False,
                                        enable_events=True,
                                        bind_return_key=True,
                                        key="submit_ingredient",
                                    ),
                                ],
                            ],
                            expand_x=True,
                            key=f"ingredients_section_{j}",
                        )
                    ],
                ],
                expand_x=True,
                key=f"recipe_section_{j}",
                relief="raised",
            )
        ]
    ]


recipe_section = [
    sg.Frame(
        "Recipe Section",
        layout=[
            [sg.Button("+ Add Section", key=f"add_recipe_section_{0}", enable_events=True)],
            [
                sg.Frame(
                    "Ingredients",
                    layout=[
                        [
                            sg.Text("Ingredients: ", font=("Arial Bold", 14)),
                            sg.Text(
                                "Press 'Enter' to add another ingredient", font=("Arial Italic", 12)
                            ),
                            sg.Button("(i) Tips", key="tips_button", enable_events=True),
                        ],
                        [
                            sg.Input(font=font, key=f"section_{0}_ingredient_{0}", expand_x=True),
                            sg.Button(
                                "X",
                                font=("Arial Bold", 14),
                                key=f"section_{0}_remove_ingredient_{0}",
                                enable_events=True,
                            ),
                            sg.Button(
                                "Submit",
                                visible=False,
                                enable_events=True,
                                bind_return_key=True,
                                key="submit_ingredient",
                            ),
                        ],
                    ],
                    expand_x=True,
                    key=f"ingredients_section_{0}",
                )
            ],
        ],
        expand_x=True,
        key=f"recipe_section_{0}",
        relief="raised",
    )
]

layout = [
    [
        sg.Column(
            layout=[main_recipe_info, recipe_section],
            scrollable=True,
            expand_y=True,
            vertical_scroll_only=True,
            element_justification="center",
            key="column",
            vertical_alignment="top",
        ),
    ],
]


def recipes():
    recipe_window = sg.Window(
        "Recipe Interface",
        layout=layout,
        resizable=True,
        size=(650, 600),
        element_justification="center",
        finalize=True,
    )

    i = j = 1
    while True:
        event, values = recipe_window.read()
        if event == sg.WIN_CLOSED:
            break

        if event:
            # DEBUG to print out the events and values
            print(event, values)

        if event == "submit_ingredient":
            recipe_window.extend_layout(
                recipe_window[f"ingredients_section_{j-1}"], new_ingredient(i, j)
            )
            recipe_window.refresh()
            recipe_window["column"].contents_changed()
            i += 1

        if "remove_ingredient" in event:
            button = event
            row = "_".join(event.split("_remove_"))
            recipe_window[button].Widget.destroy()
            recipe_window[button].Widget.master.pack_forget()
            recipe_window[row].update(value="")
            recipe_window[row].Widget.destroy()
            recipe_window[row].Widget.master.pack_forget()

        if "add_recipe_section" in event:
            recipe_window.extend_layout(recipe_window["column"], new_recipe_section(j))
            recipe_window.refresh()
            recipe_window["column"].contents_changed()
            j += 1

        if "remove_recipe_section" in event:
            button = event
            row = event.split("remove_")[-1]
            recipe_window[button].Widget.destroy()
            recipe_window[button].Widget.master.pack_forget()
            recipe_window[row].Widget.destroy()
            recipe_window[row].Widget.master.pack_forget()
            recipe_window[row].Widget.destroy()
            recipe_window[row].Widget.master.pack_forget()


recipes()
