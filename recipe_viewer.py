from random import choice
import PySimpleGUI as sg
import datetime
import json
import os
import sys
import base64
import shutil
import textwrap
import re

from utils.sql_functions import *
from utils.custom_date_picker import popup_get_date
from utils.make_database import make_database
from utils.recipe_units import units
from pprint import pprint
from recipe_interface import recipes
from recipe_scrapers import scrape_me
from itertools import pairwise

try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()

file_path = os.path.join(wd, "settings.json")

settings = json.load(open(file_path, "r"))
db_file = os.path.join(wd, "database.db")
meal_categories = list(dict.fromkeys(settings["meal_categories"]))

font = ("Arial", 16)

# ______RECIPE VIEWER_______


def clear_all_elements(window):
    window["title_frame"].update(visible=False)
    window["ingredients_frame"].update(visible=False)
    window["instructions_frame"].update(visible=False)
    return window


def open_recipes_window(meals):
    available_recipe_window = sg.Window(
        "Available Recipes",
        [
            [sg.Text("Available Recipes to View", font=("Arial Bold", 18), justification="c")],
            [
                sg.Listbox(
                    meals,
                    select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                    key="selected_meal",
                    font=font,
                    size=(30, 10),
                )
            ],
            [sg.Button("Okay"), sg.Button("Cancel")],
        ],
        disable_close=False,
    )
    while True:
        event, values = available_recipe_window.read()
        if event:
            print(event, values)
        if event in (sg.WIN_CLOSED, "Cancel"):
            available_recipe_window.close()
            return None
            break

        if event == "Okay":
            if not values["selected_meal"]:
                continue
            available_recipe_window.close()
            return values["selected_meal"][0].lower()
            break


def recipe_viewer(meals=None):
    if not meals:
        available_meals = read_all_recipes(db_file)
        meals = [meal.title() for meal, recipe in available_meals.items() if recipe]

    top_bar = [
        sg.Frame(
            "",
            layout=[
                [
                    sg.Button("New", key="new_recipe", enable_events=True),
                    sg.Text("", expand_x=True),
                    sg.Button("Clear", key="clear_recipe", enable_events=True),
                    sg.Button("Close", key="close_window", enable_events=True),
                ]
            ],
            element_justification="c",
            expand_x=True,
        )
    ]
    recipe_right_click_menu = [
        "&Right",
        ["Delete Recipe",],
    ]
    available_recipes = [
        [
            sg.Frame(
                "Available Recipes",
                [
                    [sg.Text("Available Recipes", font=("Arial Bold", 18), justification="c")],
                    [
                        sg.Listbox(
                            meals,
                            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                            key="available_meals",
                            enable_events=True,
                            right_click_menu=recipe_right_click_menu,
                            font=font,
                            expand_y=True,
                            expand_x=True,
                        )
                    ],
                ],
                expand_y=True,
                pad=2,
            ),
        ]
    ]

    title = [
        sg.Frame(
            "",
            [
                [sg.Text("", font=("Arial Bold", 18), justification="l", key="title")],
                [sg.Text("", font=("Arial Italic", 12), justification="l", key="subtitle",)],
            ],
            relief="flat",
            visible=False,
            key="title_frame",
        )
    ]

    ingredients = [
        sg.Frame(
            "",
            [
                [
                    sg.Text(
                        "Ingredients",
                        font=("Arial Bold", 14),
                        justification="c",
                        key="ingredient_header",
                    )
                ],
                [
                    sg.Column(
                        layout=[
                            [
                                sg.Text(
                                    "",
                                    font=("Arial Bold", 12),
                                    justification="l",
                                    key="left_ingredients",
                                )
                            ]
                        ],
                        element_justification="l",
                    ),
                    sg.Column(
                        layout=[[sg.Text("", font=("Arial Bold", 12), justification="l",)]],
                        expand_x=True,
                        element_justification="c",
                    ),
                    sg.Column(
                        layout=[
                            [
                                sg.Text(
                                    "",
                                    font=("Arial Bold", 12),
                                    justification="l",
                                    key="right_ingredients",
                                )
                            ]
                        ],
                        element_justification="l",
                    ),
                ],
                [sg.HorizontalSeparator()],
            ],
            relief="flat",
            expand_x=True,
            visible=False,
            key="ingredients_frame",
        )
    ]
    instructions = [
        sg.Frame(
            "",
            [
                [
                    sg.Text(
                        "Instructions",
                        font=("Arial Bold", 16),
                        justification="c",
                        key="instruction_header",
                    )
                ],
                [sg.Text("", font=("Arial", 12), justification="l", key="instructions",)],
            ],
            relief="flat",
            expand_x=True,
            visible=False,
            key="instructions_frame",
        )
    ]

    layout = [
        [
            top_bar,
            [
                sg.Column(available_recipes, expand_y=True),
                sg.Column([title, ingredients, instructions], vertical_alignment="top"),
            ],
        ],
    ]

    # Use the full layout to create the window object
    icon_file = wd + "/resources/burger-10956.png"
    sg.set_options(icon=base64.b64encode(open(str(icon_file), "rb").read()))
    recipe_window = sg.Window(
        "Recipe Interface", layout=layout, resizable=True, size=(700, 600), finalize=True,
    )

    while True:
        event, values = recipe_window.read()
        if event in (sg.WIN_CLOSED, "close_window"):
            recipe_window.close()
            break

        if event:
            # DEBUG to print out the events and values
            print(event, values)
            pass

        if event == "delete recipe":
            selected_meal = values["available_meals"][0].lower()
            remove_meal(db_file, selected_meal)
            available_meals = read_all_recipes(db_file)
            recipe_window["available_meals"].update(values=available_meals)

        if event == "new_recipe":
            recipe = recipes()
            if not recipe:
                continue
            basic_ingredients = [
                ingredient["ingredient"] for ingredient in recipe["ingredients"].values()
            ]
            new_meal = recipe["title"].lower()
            new_ingredients = ", ".join(basic_ingredients).lower()
            new_category = recipe["recipe_category"].lower()
            meal_categories = list(dict.fromkeys(settings["meal_categories"]))
            meal_categories.append(new_category.title())
            meal_categories = list(dict.fromkeys(meal_categories))
            settings["meal_categories"] = meal_categories
            with open(file_path, "w") as fp:
                json.dump(settings, fp, sort_keys=True, indent=4)

            if not new_ingredients:
                new_ingredients = new_meal

            if new_meal:
                add_meal(
                    db_file,
                    new_meal,
                    ingredients=new_ingredients,
                    recipe_link="",
                    recipe=json.dumps(recipe),
                    category=new_category,
                )
                meals = {meal: info for meal, info in read_all_meals(db_file).items()}
            available_meals = read_all_recipes(db_file)
            recipe_window["available_meals"].update(values=available_meals)

        if event in ("available_meals"):
            available_meals = read_all_recipes(db_file)
            meals = [meal.title() for meal, recipe in available_meals.items() if recipe]
            selected_meal = values["available_meals"][0].lower()
            if not selected_meal:
                continue
            recipe = json.loads(available_meals[selected_meal])
            if not recipe:
                continue

            ingredients = [
                re.sub(
                    "\s+",
                    " ",
                    " ".join(
                        [
                            ing["quantity"] if ing["quantity"] else "",
                            ing["units"] if ing["units"] else "",
                            "".join(
                                [
                                    ing["ingredient"] if ing["ingredient"] else "",
                                    (", " + ing["special_instruction"])
                                    if ing["special_instruction"]
                                    else "",
                                ]
                            ),
                        ]
                    ),
                ).strip()
                for ing in recipe["ingredients"].values()
            ]
            if len(ingredients) % 2 != 0:
                ingredients.append("")

            ingredients = list(pairwise(ingredients))[::2]
            left_ingredients = [i[0] for i in ingredients]
            right_ingredients = [i[1] for i in ingredients]

            recipe_window["title_frame"].update(visible=True)
            recipe_window["title"].update(value=recipe["title"])
            if recipe["subtitle"]:
                recipe_window["subtitle"].update(value=recipe["subtitle"])

            recipe_window["ingredients_frame"].update(visible=True)
            recipe_window["left_ingredients"].update(value="\n".join(left_ingredients))
            recipe_window["right_ingredients"].update(value="\n".join(right_ingredients))

            recipe_window["instructions_frame"].update(visible=True)
            recipe_window["instructions"].update(
                value="\n".join(textwrap.wrap(recipe["directions"], 80))
            )
            recipe_window.refresh()

        if event == "clear_recipe":
            clear_all_elements(recipe_window)
