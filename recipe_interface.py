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
from utils.recipe_units import units
from pprint import pprint

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


def new_ingredient(i):
    return [
        [
            sg.Input(font=font, key=("ingredient", i), expand_x=True, focus=True),
            sg.Button(
                "X", font=("Arial Bold", 14), key=("remove_ingredient", i), enable_events=True,
            ),
        ],
    ]


def clear_all_elements(window):
    for element in window.element_list():
        if type(element) in (sg.InputText, sg.Multiline) and window[element.Key].get():
            window[element.Key].update("")
    return window


def recipes():
    top_bar = [
        sg.Frame(
            "",
            layout=[
                [
                    sg.Button("Save", key="save_recipe", enable_events=True),
                    sg.Button("Clear", key="clear_recipe", enable_events=True),
                ]
            ],
            element_justification="r",
            expand_x=True,
        )
    ]
    main_recipe_info = [
        sg.Frame(
            "New Recipe",
            layout=[
                [
                    sg.Text("Title", font=font, size=(16, 1), pad=((5, 5), (5, 5))),
                    sg.Input(font=font, key="recipe_title", expand_x=True, pad=((5, 5), (5, 5))),
                ],
                [
                    sg.Text("Subtitle (optional)", font=font, size=(16, 1), pad=((5, 5), (5, 5)),),
                    sg.Input(
                        font=font, key="recipe_subtitle", expand_x=True, pad=((5, 5), (5, 5)),
                    ),
                ],
                [
                    sg.Text("Category", font=font, size=(16, 1), pad=((5, 5), (5, 5))),
                    sg.Combo(
                        values=meal_categories[1:],
                        font=font,
                        key="recipe_category",
                        readonly=True,
                        expand_x=True,
                        pad=((5, 5), (5, 10)),
                    ),
                ],
            ],
            element_justification="c",
            key="new_recipes_frame",
            expand_x=True,
            pad=((5, 5), (5, 5)),
            relief="raised",
        )
    ]

    recipe_section = [
        sg.Frame(
            "Recipe",
            layout=[
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
                                sg.Input(font=font, key=("ingredient", 0), expand_x=True),
                                sg.Button(
                                    "Submit",
                                    visible=False,
                                    enable_events=True,
                                    bind_return_key=True,
                                    key="submit",
                                ),
                            ],
                        ],
                        expand_x=True,
                        key=("ingredient_frame", 0),
                    ),
                ],
                [sg.Text("Directions", font=("Arial Bold", 14))],
                [sg.Multiline(font=font, key="directions", expand_x=True, size=(30, 5))],
            ],
            expand_x=True,
            key=("recipe_frame", 0),
            pad=((5, 5), (10, 10)),
            relief="raised",
        )
    ]

    layout = [
        [
            top_bar,
            sg.Column(
                layout=[main_recipe_info, recipe_section],
                scrollable=True,
                vertical_scroll_only=True,
                expand_y=True,
                element_justification="center",
                key="column",
                vertical_alignment="top",
            ),
        ],
    ]

    recipe_window = sg.Window(
        "Recipe Interface",
        layout=layout,
        resizable=True,
        size=(650, 600),
        element_justification="center",
        finalize=True,
    )

    available_units = "\n".join(
        ["\t".join(unit) for unit in [[unit[0], ", ".join(unit[1:])] for unit in units]]
    )
    tip_text = f"""
    Enter ingredient information as follows:
        quantity units ingredient, special instructions (units and special instructions optional)

        examples:
        2 c. onions, chopped
        1 oz. olive oil
        2 1/2 cups of flour, sifted
        (available units at the bottom)

    If an ingredient is not recognized or units are not recognized, the text as entered will
    be used in the recipe.

    Available units and abbreviations:
    {available_units}
    """

    fixed_units = []
    for unit in units:
        fixed_unit = []
        for character in unit:
            if character == ".":
                character = r"\{}".format(character)
            fixed_unit.append(character)
        fixed_units.append("".join(fixed_unit))

    unit_expression = "|".join(fixed_units)
    match_expression = f"([0-9\/\.]*)?\s?({unit_expression})?\s*?([a-zA-Z\s]*),?\s?([a-zA-Z\s]*)?"

    i = 1
    while True:
        event, values = recipe_window.read()
        if event == sg.WIN_CLOSED:
            break

        if event:
            # DEBUG to print out the events and values
            print(event, values)
            pass

        if event == "tips_button":
            sg.Window(
                "Recipe Tips",
                [
                    [sg.Text("Tips and Tricks", font=("Arial Bold", 14), justification="c")],
                    [
                        sg.Column(
                            [[sg.Text(tip_text, font=font, justification="l",)]],
                            scrollable=True,
                            vertical_scroll_only=True,
                            pad=((0, 0), (10, 50)),
                        )
                    ],
                    [sg.Button("Okay")],
                ],
                disable_close=False,
            ).read(close=True)

        if event == "submit":
            current_element_key = recipe_window.FindElementWithFocus().Key

            if "ingredient" in current_element_key:
                recipe_window.extend_layout(
                    recipe_window[("ingredient_frame", 0)], new_ingredient(i),
                )
                recipe_window.refresh()
                recipe_window["column"].contents_changed()
                new_row = recipe_window.FindElementWithFocus().Key
                i += 1

        if "remove_ingredient" in event:
            row = recipe_window.FindElementWithFocus().Key
            recipe_window[event].Widget.destroy()
            recipe_window[event].Widget.master.pack_forget()
            recipe_window[("ingredient", row[-1],)].update(value="")
            recipe_window[("ingredient", row[-1],)].Widget.destroy()
            recipe_window[("ingredient", row[-1],)].Widget.master.pack_forget()
            recipe_window.refresh()
            recipe_window["column"].contents_changed()

        if event == "save_recipe":
            raw_ingredients = []
            for element in recipe_window.element_list():
                if type(element) == sg.InputText:
                    if "ingredient" in element.Key:
                        if recipe_window[element.Key].get():
                            raw_ingredients.append(recipe_window[element.Key].get())
                if type(element) == sg.Multiline:
                    if "directions" in element.Key:

                        directions = (
                            recipe_window["directions"].get()
                            if recipe_window[element.Key].get()
                            else None
                        )

            recipe = {}
            j = 0
            for raw_ingredient in raw_ingredients:
                recipe["ingredients"] = {}
                recipe["ingredients"][f"ingredient_{j}"] = {}
                parsed_ingredient = re.match(match_expression, raw_ingredient).groups()
                (
                    recipe["ingredients"][f"ingredient_{j}"]["quantity"],
                    recipe["ingredients"][f"ingredient_{j}"]["units"],
                    recipe["ingredients"][f"ingredient_{j}"]["ingredient"],
                    recipe["ingredients"][f"ingredient_{j}"]["special_instruction"],
                ) = parsed_ingredient
                j += 1

            recipe["directions"] = directions
            return recipe

        if event == "clear_recipe":
            confirm = sg.popup_ok_cancel("Are you sure you want to clear?")
            if not confirm == "OK":
                continue
            clear_all_elements(recipe_window)
