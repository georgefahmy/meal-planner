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
import webbrowser

from utils.sql_functions import *
from utils.custom_date_picker import popup_get_date
from utils.make_database import make_database
from utils.recipe_units import units
from utils.remote_database_functions import (
    connect_to_remote_server,
    close_connection_to_remote_server,
    get_database_from_remote,
    send_database_to_remote,
    check_username_password,
    internet_on,
)
from check_for_updates import check_for_update
from recipe_interface import recipes
from recipe_viewer import recipe_viewer
from recipe_scrapers import scrape_me
from recipe_scrapers.settings import RecipeScraperSettings
from recipe_scrapers.settings import default
from string import capwords
from math import ceil
from time import sleep
from fractions import Fraction
from collections import Counter

if sys.version_info.minor >= 10:
    from itertools import pairwise
else:
    from itertools import tee

    def pairwise(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)


scraper_settings = RecipeScraperSettings()
scraper_settings._configure()

try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()

icon_file = wd + "/resources/burger-10956.png"
sg.set_options(icon=base64.b64encode(open(str(icon_file), "rb").read()))
themes = sg.theme_list()
chosen_theme = choice(themes)
sg.set_options(alpha_channel=0.99)
sg.theme("TanBlue")

restart = check_for_update()
if restart:
    exit()


def login(username="", password=""):
    submit, login_info = sg.Window(
        "Meal Planner Pro Login",
        [
            [
                sg.Text("Username: ", font=("Arial", 16), expand_x=True),
                sg.Input(username, font=("Arial", 16), key="-USER-", size=(10, 1)),
            ],
            [
                sg.Text("Password: ", font=("Arial", 16), expand_x=True),
                sg.Input(
                    password, font=("Arial", 16), key="-PASS-", size=(10, 1), password_char="*"
                ),
            ],
            [sg.Button("Okay", bind_return_key=True), sg.Button("Cancel (Offline Mode)")],
        ],
        disable_close=False,
        size=(300, 100),
    ).read(close=True)

    return submit, login_info


settings = json.load(open(os.path.join(wd, "settings.json"), "r"))
username, password, auth = settings["username"], settings["password"], settings["logged_in"]
sftp, ssh = connect_to_remote_server()

if username and sftp:
    get_database_from_remote(sftp, username, password)

db_file = os.path.join(wd, "database.db")
make_database(db_file)

# Get meal and ingredient information from the database
meals = {meal: info for meal, info in read_all_meals(db_file).items()}
settings["meal_categories"].remove("All")
meal_categories = ["All"] + list(
    set(
        settings["meal_categories"]
        + list(set([capwords(meal["category"]) for meal in meals.values()]))
    )
)

settings["meal_categories"] = sorted(meal_categories)
with open(file_path, "w") as fp:
    json.dump(settings, fp, sort_keys=True, indent=4)

today = datetime.date.today()
today_name = today.strftime("%A")

start = today - datetime.timedelta(days=(datetime.datetime.today().weekday()) % 7)
weeks_dates = [start + datetime.timedelta(days=x) for x in range(7)]
picked_date = str(start)

blank_plan_dict = {
    "date": str(start),
    "ingredients": [],
    "meals": {
        "Monday": "",
        "Tuesday": "",
        "Wednesday": "",
        "Thursday": "",
        "Friday": "",
        "Saturday": "",
        "Sunday": "",
    },
}

blank_gui_table = [[day] + [", ".join(meals)] for day, meals in blank_plan_dict["meals"].items()]


def update_menu_bar_definition(auth, sftp):
    if auth:
        menu_bar_layout = [
            ["&File", ["Load Database", "Export Database", "!Login", "Logout"]],
            ["Recipes", ["New Recipe", "View Recipes", "Edit Recipe"]],
            ["User Settings", ["View Settings"]],
            ["Help", ["!About", "!How To", "!Feedback", "Debug Window"]],
        ]
    else:

        menu_bar_layout = [
            ["&File", ["Load Database", "Export Database", "Login", "!Logout"]],
            ["Recipes", ["New Recipe", "View Recipes", "Edit Recipe"]],
            ["User Settings", ["View Settings"]],
            ["Help", ["!About", "!How To", "!Feedback", "Debug Window"]],
        ]
    return menu_bar_layout


# --------------------------------- Define Layout ---------------------------------

# --------------------------------MAIN LEFT COLUMN---------------------------------
# Top left quadrant - three columns, list of meals, selection checkboxes, submit or cancel

meal_selection_rightclick_menu_def = [
    "&Right",
    ["!View Recipe::meal", "!Edit Recipe::meal", sg.MENU_SEPARATOR_LINE, "!Delete::meal",],
]


left_column = [
    [
        sg.Frame(
            title="Filters",
            element_justification="l",
            size=(260, 65),
            pad=(0, 0),
            layout=[
                [
                    sg.Text("Category", font=("Arial", 12), size=(7, 1)),
                    sg.Combo(
                        default_value="All",
                        values=meal_categories,
                        font=("Arial", 12),
                        size=(10, 1),
                        key="-CFILTER-",
                        enable_events=True,
                        expand_x=True,
                        readonly=True,
                    ),
                ],
                [
                    sg.Text("Keyword", key="-MFILTER_TEXT-", font=("Arial", 12), size=(7, 1)),
                    sg.Input(
                        font=("Arial", 12),
                        size=(10, 1),
                        key="-MFILTER-",
                        enable_events=True,
                        expand_x=True,
                        tooltip="Search meals and ingredients for a keyword",
                    ),
                ],
            ],
        )
    ],
    [
        sg.Frame(
            "Available Meals",
            element_justification="c",
            size=(260, 350),
            layout=[
                [
                    sg.Text(
                        "Meal Selection",
                        font=("Arial", 16),
                        size=(20, 1),
                        justification="center",
                        expand_x=True,
                    )
                ],
                [
                    sg.Listbox(
                        values=sorted([capwords(meal) for meal in read_all_meals(db_file).keys()]),
                        size=(18, 15),
                        expand_x=True,
                        pad=((5, 5), (5, 5)),
                        font=("Arial", 14),
                        key="-MEAL_LIST-",
                        enable_events=True,
                        auto_size_text=True,
                        select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
                        right_click_menu=meal_selection_rightclick_menu_def,
                        tooltip="Select one or more meals.\nRight click meals for more options.",
                    )
                ],
                [
                    sg.Column(
                        [
                            [
                                sg.Button(
                                    "Add to Plan",
                                    visible=True,
                                    key="-ADD_TO_PLAN-",
                                    enable_events=True,
                                ),
                                sg.Button(
                                    "Cancel", visible=True, key="-CANCEL-", enable_events=True
                                ),
                            ]
                        ]
                    )
                ],
            ],
        )
    ],
]

middle_column = [
    sg.Column(
        [
            [
                sg.Frame(
                    "Week Days",
                    element_justification="l",
                    vertical_alignment="top",
                    size=(70, 220),
                    pad=(0, 0),
                    layout=[
                        [
                            sg.Checkbox(
                                day,
                                font=("Arial", 14),
                                default=False,
                                key=f"-{day.upper()}-",
                                enable_events=True,
                                auto_size_text=True,
                                size=(6, 10),
                            )
                        ]
                        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                    ],
                ),
            ],
        ]
    )
]

right_column = [
    [
        sg.Frame(
            title="",
            element_justification="c",
            size=(260, 65),
            pad=(0, 0),
            relief="flat",
            layout=[
                [
                    sg.Text(
                        "Category:",
                        font=("Arial", 14),
                        justification="l",
                        visible=True,
                        expand_x=True,
                        size=(12, 2),
                    ),
                    sg.Text(
                        "category",
                        key="-CATEGORY_TEXT-",
                        font=("Arial", 14),
                        justification="l",
                        size=(260, 1),
                        visible=False,
                        expand_x=True,
                    ),
                ],
            ],
        )
    ],
    [
        sg.Frame(
            "Ingredients",
            size=(260, 350),
            expand_x=True,
            expand_y=True,
            element_justification="c",
            vertical_alignment="bottom",
            layout=[
                [
                    sg.Text(
                        "Ingredients",
                        font=("Arial", 16),
                        size=(20, 1),
                        justification="c",
                        expand_x=True,
                    )
                ],
                [
                    sg.Listbox(
                        values=[],
                        size=(18, 15),
                        expand_x=True,
                        pad=((5, 5), (5, 5)),
                        font=("Arial", 14),
                        key="-MEAL_INGREDIENTS_LIST-",
                        auto_size_text=True,
                        enable_events=False,
                        select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                    )
                ],
                [
                    sg.Button(
                        "View Recipe",
                        key="-VIEW_RECIPE-",
                        disabled=True,
                        disabled_button_color=("Black", "Gray"),
                    )
                ],
            ],
        ),
    ],
]

item_selection_section = [
    [
        sg.Column(left_column, element_justification="c", pad=((0, 0), (0, 0))),
        sg.Column([middle_column], element_justification="c", pad=((0, 0), (0, 0))),
        sg.Column(right_column, element_justification="c", pad=((0, 0), (0, 0))),
    ]
]

# Bottom left quadrant - New meal submission - meal, ingredients, links, submit, clear
input_section = [
    [sg.Text("New Meal", font=("Arial", 18), size=(50, 2), justification="c"),],
    [
        sg.Column(
            [
                [
                    sg.Button(
                        "New Recipe",
                        font=("Arial", 12),
                        size=(20, 1),
                        expand_x=True,
                        key="-RECIPE-",
                        tooltip="Full detailed recipe information",
                    )
                ],
                [
                    sg.Text(
                        "Recipe saved",
                        font=("Arial", 10),
                        size=(16, 1),
                        expand_x=True,
                        key="-RECIPE_NOTE-",
                        visible=False,
                    )
                ],
            ],
            element_justification="c",
        ),
        sg.Column(
            [
                [
                    sg.In(
                        default_text="Paste Link Here (Optional)",
                        size=(24, 2),
                        font=("Arial Italic", 14),
                        key="-RECIPE_LINK-",
                        enable_events=False,
                        tooltip="Paste a URL from your favorite recipe here",
                    ),
                    sg.Button(
                        "Submit",
                        size=(8, 1),
                        font=("Arial", 12),
                        key="-SUBMIT_RECIPE_URL-",
                        enable_events=False,
                        tooltip="Paste a URL from your favorite recipe here",
                    ),
                ],
            ],
            element_justification="c",
        ),
    ],
]

main_left_column = [
    sg.Column(
        [
            [
                sg.Frame(
                    "Item Selection",
                    element_justification="c",
                    layout=item_selection_section,
                    pad=(0, 0),
                    size=(620, 440),
                )
            ],
            [
                sg.Frame(
                    "New Meals",
                    element_justification="c",
                    layout=input_section,
                    pad=(0, 0),
                    size=(620, 140),
                )
            ],
        ]
    )
]

# ---------------------------MAIN RIGHT COLUMN---------------------------
# Top right quadrant - Meal Plan - Date, Meal Name, Link (if any)

current_plan_dict = blank_plan_dict

gui_table = [[day] + [", ".join(meals)] for day, meals in current_plan_dict["meals"].items()]

default_table_right_click = [
    "&Right",
    ["Clear Row::table", sg.MENU_SEPARATOR_LINE,],
]

meal_plan_section = [
    [
        sg.Column(
            [
                [
                    sg.Button("Pick Date", key="-PICK_DATE-"),
                    sg.Text(
                        "Week's Plan",
                        size=(22, 1),
                        font=("Arial", 18),
                        justification="l",
                        key="-WEEK-",
                        expand_x=True,
                    ),
                    sg.Button("Available Plans", key="-AVAILABLE_PLANS-",),
                ],
                [
                    sg.Table(
                        values=gui_table,
                        display_row_numbers=False,
                        justification="l",
                        num_rows=7,
                        headings=["Day", "Meal"],
                        font=("Arial", 14),
                        text_color="black",
                        background_color="lightgray",
                        alternating_row_color="white",
                        auto_size_columns=False,
                        col_widths=(10, 30),
                        selected_row_colors="lightblue on blue",
                        enable_events=True,
                        enable_click_events=False,
                        right_click_menu=default_table_right_click,
                        tooltip="Right click to edit or remove items",
                        size=(40, 40),
                        hide_vertical_scroll=True,
                        key="-TABLE-",
                    )
                ],
            ],
            element_justification="c",
        ),
    ],
    [
        sg.Column(
            [[sg.Button("Clear", visible=True, key="-PLAN-CLEAR-", enable_events=True),]],
            element_justification="c",
        )
    ],
]

# Bottom Right Quadrant - Table of ingredients
ingredients_list_section = [
    [
        sg.Column(
            [
                [
                    sg.Text(
                        "Plan Ingredients List",
                        size=(40, 1),
                        font=("Arial", 16),
                        justification="c",
                        expand_x=True,
                    )
                ],
                [
                    sg.Multiline(
                        "",
                        font=("Arial", 14),
                        size=(60, 17),
                        key="-PLAN_INGREDIENTS_LIST-",
                        enable_events=False,
                        disabled=True,
                        pad=(0, 0),
                    )
                ],
            ],
            element_justification="c",
            pad=(0, 0),
        )
    ]
]

main_right_column = [
    sg.Column(
        [
            [
                sg.Frame(
                    "Weekly Plan",
                    layout=meal_plan_section,
                    element_justification="c",
                    size=(620, 230),
                    pad=(0, 0),
                )
            ],
            [
                sg.Frame(
                    "Shopping List",
                    layout=ingredients_list_section,
                    element_justification="c",
                    size=(620, 350),
                    pad=(0, 0),
                )
            ],
        ],
        element_justification="c",
    )
]

menu_bar_layout = update_menu_bar_definition(auth, sftp)

# ----- Full layout -----
full_layout = [
    [
        [sg.Menu(menu_bar_layout, font=("Arial", "12"), key="-MENU-")],
        [sg.Text("Meal Planner PRO", font=("Arial", 20), justification="center", expand_x=True)],
        [sg.HorizontalSeparator()],
        sg.Column([main_left_column], size=(400, 600), element_justification="c", expand_x=True,),
        sg.VSeperator(),
        sg.Column([main_right_column], size=(400, 600), element_justification="c", expand_x=True,),
    ]
]


def matchingKeys(dictionary, searchString):
    return [
        key
        for key, val in dictionary.items()
        if searchString.lower() in key.lower()
        or any(searchString.lower() in s.lower() for s in val["ingredients"])
        or searchString.lower() in val["category"]
    ]


def display_recipe(recipe):
    if not recipe:
        return

    if type(recipe) == str:
        # print("recipe not converted to dict, converting now")
        recipe = json.loads(recipe)

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
    subtitle_flag = True if recipe["subtitle"] else False

    if len(ingredients) % 2 != 0:
        ingredients.append("")

    ingredients = list(pairwise(ingredients))[::2]
    left_ingredients = ["- " + "\n".join(textwrap.wrap(i[0], 40)) for i in ingredients if i[0]]
    right_ingredients = ["- " + "\n".join(textwrap.wrap(i[1], 40)) for i in ingredients if i[1]]
    layout = [
        [sg.Text(capwords(recipe["title"]), font=("Arial Bold", 18), justification="l")],
        [
            sg.Text(
                recipe["subtitle"],
                font=("Arial Italic", 12),
                visible=subtitle_flag,
                justification="l",
            )
        ],
        [
            sg.Text(
                "",
                key="recipe_link_view",
                font=("Arial Italic", 12),
                expand_x=True,
                enable_events=True,
                tooltip="Click to Open in browser",
                justification="l",
                visible=False,
            )
        ],
        [sg.Text("", font=("Arial Italic", 12), expand_x=True, justification="c")],
        [sg.HorizontalSeparator()],
        [sg.Text("Ingredients", font=("Arial Bold", 14), justification="c")],
        [
            sg.Column(
                [
                    [sg.Text(ingredient, font=("Arial Bold", 12), justification="l")]
                    for ingredient in left_ingredients
                ],
                element_justification="l",
            ),
            sg.Column(
                [
                    [sg.Text(ingredient, font=("Arial Bold", 12), justification="l")]
                    for ingredient in right_ingredients
                ],
                element_justification="l",
            ),
        ],
        [sg.HorizontalSeparator()],
        [sg.Text("Instructions", font=("Arial Bold", 16), justification="c")],
        [
            sg.Text(
                "\n".join(textwrap.wrap(recipe["directions"], 80)),
                font=("Arial Bold", 12),
                justification="l",
            )
        ],
        [sg.Text("", font=("Arial Bold", 12), expand_x=True, justification="c")],
    ]
    display_window = sg.Window("Recipe", layout, resizable=True, finalize=True)
    if meals[recipe["title"].lower()]["recipe_link"]:
        display_window["recipe_link_view"].update(
            value=meals[recipe["title"].lower()]["recipe_link"], visible=True
        )
    display_window.refresh()
    while True:
        event, values = display_window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == "recipe_link_view":
            webbrowser.open(display_window[event].get())
            display_window.close()
            return None
    return display_window


fixed_units = []
for unit in units:
    for detailed_unit in unit:
        fixed_unit = []
        for character in detailed_unit:
            if character == ".":
                character = r"\{}".format(character)
            fixed_unit.append(character)
        fixed_units.append("".join(fixed_unit))

fixed_units.reverse()
unit_expression = "|".join(fixed_units)
match_expression = f"([0-9\/\.\-\s]*)?\s?({unit_expression})?\s*?([a-zA-Z0-9\s\-\.]*),?\s?(.*)?"


def process_recipe_link(recipe_link):
    recipe = {}
    try:
        scraped_recipe = scrape_me(recipe_link, wild_mode=True)
    except:
        return recipe

    recipe["title"] = scraped_recipe.schema.title() if scraped_recipe.schema.title() else ""
    recipe["directions"] = (
        re.sub("\n", " ", scraped_recipe.schema.instructions())
        if scraped_recipe.schema.instructions()
        else ""
    )
    recipe["recipe_category"] = (
        scraped_recipe.schema.category() if scraped_recipe.schema.category() else "Dinner"
    )
    raw_ingredients = (
        scraped_recipe.schema.ingredients() if scraped_recipe.schema.ingredients() else []
    )

    ingredients = {}
    for i, raw_ingredient in enumerate(raw_ingredients):
        raw_ingredient = re.sub(" \(,", ",", raw_ingredient)
        raw_ingredient = re.sub(" \)", "", raw_ingredient)
        raw_ingredient = re.sub(",", "", raw_ingredient)

        ingredients[f"ingredient_{i}"] = {}
        ingredients[f"ingredient_{i}"]["raw_ingredient"] = raw_ingredient
        parsed_ingredient = list(
            re.match(match_expression, raw_ingredient, flags=re.IGNORECASE).groups()
        )
        for j, val in enumerate(parsed_ingredient):
            if val:
                parsed_ingredient[j] = val.strip()

        parsed_ingredient = tuple(parsed_ingredient)
        (
            ingredients[f"ingredient_{i}"]["quantity"],
            ingredients[f"ingredient_{i}"]["units"],
            ingredients[f"ingredient_{i}"]["ingredient"],
            ingredients[f"ingredient_{i}"]["special_instruction"],
        ) = parsed_ingredient

    recipe["ingredients"] = ingredients
    recipe["subtitle"] = ""
    return recipe


def generate_plan_shopping_list(current_plan_dict):

    plan_meals = [
        meal.lower() for meals in current_plan_dict["meals"].values() for meal in meals if meal
    ]

    full_plan_shopping_list = []
    for meal in plan_meals:
        meal_shopping_list = []
        meal_recipe = read_meal_recipe(db_file, meal)
        meal_title = meal_recipe["title"]
        for ingredient in meal_recipe["ingredients"].values():
            if ingredient["quantity"]:
                if "-" in ingredient["quantity"]:
                    ingredient["quantity"] = ingredient["quantity"].split("-")[-1]

                full_plan_shopping_list.extend(
                    [
                        (
                            (ingredient["units"].lower() + " " + ingredient["ingredient"].lower())
                            if ingredient["units"]
                            else ingredient["ingredient"].lower()
                        )
                    ]
                    * ceil(float(sum(Fraction(s) for s in ingredient["quantity"].split())))
                )
            else:
                # just add the ingredient to the full list for counting.
                full_plan_shopping_list.extend(
                    [
                        (
                            (ingredient["units"].lower() + " " + ingredient["ingredient"].lower())
                            if ingredient["units"]
                            else ingredient["ingredient"].lower()
                        )
                    ]
                )

    counter = Counter(full_plan_shopping_list)
    plan_ingredients = []
    for ingredient, count in counter.items():
        plan_ingredients.append(f"{count} {capwords(ingredient)}")

    current_plan_dict["ingredients"] = ", ".join(plan_ingredients)
    plan_ingredients = "\n".join(sorted(plan_ingredients, reverse=True))

    gui_table = [[day] + [", ".join(meals)] for day, meals in current_plan_dict["meals"].items()]

    window["-WEEK-"].update("Week of " + current_plan_dict["date"])
    window["-TABLE-"].update(values=gui_table)
    window["-PLAN_INGREDIENTS_LIST-"].update(plan_ingredients)
    window["-TABLE-"].set_right_click_menu(default_table_right_click)

    return current_plan_dict


def error_window(text):
    sg.Window(
        "ERROR",
        [[sg.Text(text, font=("Arial", 16), justification="c")], [sg.Button("Okay")],],
        disable_close=False,
    ).read(close=True)


def export_plan(selected_plan):
    plan_key = selected_plan[0][0]
    current_plan_dict = read_current_plans(db_file, plan_key)

    settings = json.load(open(file_path, "r"))
    export_plan_path = settings["export_plan_path"]

    if not export_plan_path:
        export_plan_path = sg.popup_get_folder("Choose Export Location")
        settings["export_plan_path"] = export_plan_path
        with open(file_path, "w") as fp:
            json.dump(settings, fp, sort_keys=True, indent=4)

    if not export_plan_path:
        return

    if current_plan_dict["date"] not in export_plan_path:
        export_plan_path = export_plan_path + "/" + f"plan_{current_plan_dict['date']}.txt"

    day_plan = []
    day_plan.append(f"Plan for the week of {current_plan_dict['date']}\n")
    for day, meal in current_plan_dict["meals"].items():
        if not meal:
            day_plan.append(f"{day}:")
            day_plan.append("No Planned Meal\n\n"),
            continue
        day_plan.append(f"{day}:")
        for meal in meal:
            if meal:
                day_plan.append(f"-{meal}-")
                day_plan.append("Ingredients:")
                wrapped_ingredients = textwrap.wrap(
                    capwords(", ".join(meals[meal.lower()]["ingredients"])), 50
                )
                day_plan.append("\n".join(wrapped_ingredients))
                day_plan.append("\n")
    day_plan.append("All Ingredients:")
    day_plan.append(current_plan_dict["ingredients"])
    plan_text = "\n".join(day_plan)
    with open(export_plan_path, "w") as fp:
        fp.write(plan_text)
        fp.close()
    return export_plan_path


def add_meal_to_right_click_menu(meal_right_click_menu, meal, day):
    meal_sub_menu = [
        "View Recipe::" + meal,
        "Edit Recipe::" + meal,
        sg.MENU_SEPARATOR_LINE,
        "&Change Day",
        [
            "Monday::" + meal,
            "Tuesday::" + meal,
            "Wednesday::" + meal,
            "Thursday::" + meal,
            "Friday::" + meal,
            "Saturday::" + meal,
            "Sunday::" + meal,
        ],
        sg.MENU_SEPARATOR_LINE,
        "Delete Item::" + meal,
    ]
    meal_sub_menu[4].pop(day)
    menu_extension = [meal, meal_sub_menu]

    if meal in [meal[0] for meal in meal_right_click_menu[1][3:]]:
        return meal_right_click_menu

    meal_right_click_menu[1].extend(menu_extension)

    return meal_right_click_menu


def check_if_plan_exists(picked_date):
    current_plan_dict = read_current_plans(db_file, picked_date)
    if current_plan_dict:
        picked_date = str(current_plan_dict["date"])
        current_plan_dict = generate_plan_shopping_list(current_plan_dict)
    return current_plan_dict


def settings_viewer():
    settings = json.load(open(os.path.join(wd, "settings.json"), "r"))
    plan_path = settings["export_plan_path"] if settings["export_plan_path"] else "None"
    recipe_path = settings["export_recipe_path"] if settings["export_recipe_path"] else "None"
    meal_categories = settings["meal_categories"]
    meal_categories.remove("All")
    username = settings["username"] if settings["username"] else "None"
    password = settings["password"] if settings["password"] else "None"
    settings_window = sg.Window(
        "User Settings",
        [
            [sg.Text(f"Username: {username}; Password: {password}", font=("Arial", 16)),],
            [sg.Text(f"Plan Export Path: {plan_path}", font=("Arial", 16)),],
            [sg.Text(f"Recipe Export Path: {recipe_path}", font=("Arial", 16)),],
            [
                [sg.Text("Meal Categories", font=("Arial", 16), justification="c")],
                [
                    sg.Listbox(
                        meal_categories,
                        size=(20, 10),
                        tooltip="Right click to edit",
                        key="Category_settings",
                        right_click_menu=["&Right", ["Edit::settings", "Delete::settings"]],
                    )
                ],
                [sg.Button("Add Category", enable_events=True)],
            ],
        ],
        disable_close=False,
    )

    while True:
        settings_event, settings_values = settings_window.read()
        if settings_event == sg.WIN_CLOSED:
            break

        if settings_event:
            print(settings_event, settings_values)

        if settings_event == "Edit::settings":
            updated_category = sg.popup_get_text(
                "Edit Category", default_text=settings_values["Category_settings"][0]
            )
            updated_category = updated_category.replace("('", "").replace("',", "").replace(")", "")
            if updated_category:
                meal_categories.remove(settings_values["Category_settings"][0])
                meal_categories.append(updated_category)

            settings["meal_categories"] = ["All"] + sorted(meal_categories)
            with open(os.path.join(wd, "settings.json"), "w") as fp:
                json.dump(settings, fp, sort_keys=True, indent=4)

            meal_categories = settings["meal_categories"]
            meal_categories.remove("All")
            settings_window["Category_settings"].update(values=meal_categories)

        if settings_event == "Delete::settings":
            confirm = sg.popup_ok_cancel("Confirm Delete Category?")
            if confirm == "OK":
                meal_categories.remove(settings_values["Category_settings"][0])

            settings["meal_categories"] = ["All"] + sorted(meal_categories)
            with open(os.path.join(wd, "settings.json"), "w") as fp:
                json.dump(settings, fp, sort_keys=True, indent=4)

            meal_categories = settings["meal_categories"]
            meal_categories.remove("All")
            settings_window["Category_settings"].update(values=meal_categories)

        if settings_event == "Add Category":
            new_category = sg.popup_get_text("New Category")
            new_category = new_category.replace("('", "").replace("',", "").replace(")", "")
            if new_category:
                meal_categories.append(new_category)

            settings["meal_categories"] = ["All"] + sorted(meal_categories)
            with open(os.path.join(wd, "settings.json"), "w") as fp:
                json.dump(settings, fp, sort_keys=True, indent=4)

            meal_categories = settings["meal_categories"]
            meal_categories.remove("All")
            settings_window["Category_settings"].update(values=meal_categories)


# --------------------------------- Create the Window ---------------------------------
# Use the full layout to create the window object
window = sg.Window("Meal Planner PRO", full_layout, resizable=True, size=(1320, 660), finalize=True)
window.refresh()

window["-WEEK-"].update(value="Week of " + picked_date)
current_plan_dict = check_if_plan_exists(picked_date)
if not current_plan_dict:
    current_plan_dict = blank_plan_dict
debug = False

# Start the window loop
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        if sftp:
            send_database_to_remote(sftp, username, password)
        close_connection_to_remote_server(sftp, ssh)
        break

    if event == "Debug Window":
        if debug:
            debug = False

        if not debug:
            sg.show_debugger_window()
            debug = True

    if event == "View Settings":
        settings_viewer()

    if debug == True:
        sg.Print(event, values)

    if event == "Login":
        with open(os.path.join(wd, "settings.json"), "r") as fp:
            settings = json.load(fp)
        username, password, auth = (
            settings["username"],
            settings["password"],
            settings["logged_in"],
        )
        if not sftp:
            sftp, ssh = connect_to_remote_server()

        while not auth:
            sleep(1)
            if not auth:
                submit, login_info = login(username, password)
                if submit == "Okay":
                    username, password = login_info["-USER-"], login_info["-PASS-"]
                    auth, new = check_username_password(sftp, username, password)
                if submit == "Cancel (Offline Mode)":
                    break

            if auth:
                settings["username"], settings["password"], settings["logged_in"] = (
                    username,
                    password,
                    auth,
                )
                with open(os.path.join(wd, "settings.json"), "w") as fp:
                    json.dump(settings, fp, sort_keys=True, indent=4)

                if new:
                    os.remove(db_file)
                    make_database(db_file)
                    window.perform_long_operation(
                        lambda: send_database_to_remote(sftp, username, password), "Done"
                    )
                else:
                    get_database_from_remote(sftp, username, password)

                window["-MEAL_LIST-"].update(
                    values=sorted([capwords(meal) for meal in read_all_meals(db_file).keys()])
                )
                meals = {meal: info for meal, info in read_all_meals(db_file).items()}
                current_plan_dict = read_current_plans(db_file, str(start))
                window["-CFILTER-"].update(
                    set_to_index=[0],
                    values=["All"]
                    + list(set([capwords(meal["category"]) for meal in meals.values()])),
                )
                if not current_plan_dict:
                    current_plan_dict = blank_plan_dict

                current_plan_dict = generate_plan_shopping_list(current_plan_dict)
                menu_bar_layout = update_menu_bar_definition(auth, sftp)
                window["-MENU-"].update(menu_definition=menu_bar_layout)

    if event == "Logout":
        save_before_logging_out = sg.popup_yes_no("Save Database before logging out?")
        if save_before_logging_out == "Yes":
            window.perform_long_operation(
                lambda: send_database_to_remote(sftp, username, password), "Done"
            )
        auth = False
        # settings["password"] = settings["username"] = ""
        settings["logged_in"] = False
        with open(os.path.join(wd, "settings.json"), "w") as fp:
            json.dump(settings, fp, sort_keys=True, indent=4)
        # os.rename(db_file, db_file.split(".")[0] + "_loggedout.db")
        # make_database(db_file)
        window["-MEAL_LIST-"].update(
            values=sorted([capwords(meal) for meal in read_all_meals(db_file).keys()])
        )
        meals = {meal: info for meal, info in read_all_meals(db_file).items()}
        current_plan_dict = read_current_plans(db_file, str(start))

        if not current_plan_dict:
            current_plan_dict = blank_plan_dict

        current_plan_dict = generate_plan_shopping_list(current_plan_dict)

        menu_bar_layout = update_menu_bar_definition(auth, sftp)
        window["-MENU-"].update(menu_definition=menu_bar_layout)
        window["-MEAL_INGREDIENTS_LIST-"].update([])

    if event == "View Recipes":
        recipe_viewer()
        meals = {meal: info for meal, info in read_all_meals(db_file).items()}
        window["-MEAL_LIST-"].update(
            sorted([capwords(meal) for meal in read_all_meals(db_file).keys()])
        )

    if event == "-SUBMIT_RECIPE_URL-" and ".com" in values["-RECIPE_LINK-"]:
        new_recipe = values["-RECIPE_LINK-"].lower()

        recipe = process_recipe_link(new_recipe)
        recipe["recipe_category"] = (
            recipe["recipe_category"] if recipe["recipe_category"] else "Dinner"
        )
        recipe = recipes(capwords(recipe["title"]), recipe_data=recipe)

        if not recipe:
            continue

        basic_ingredients = [
            ingredient["ingredient"] for ingredient in recipe["ingredients"].values()
        ]
        new_meal = recipe["title"].lower()
        new_ingredients = ", ".join(basic_ingredients).lower()
        new_category = recipe["recipe_category"].lower()

        meal_categories = list(dict.fromkeys(settings["meal_categories"]))
        meal_categories.append(capwords(new_category))
        meal_categories = list(dict.fromkeys(meal_categories))

        settings["meal_categories"] = meal_categories
        with open(file_path, "w") as fp:
            json.dump(settings, fp, sort_keys=True, indent=4)

        if new_meal:
            add_meal(
                db_file,
                new_meal,
                ingredients=new_ingredients,
                recipe_link=new_recipe,
                recipe=json.dumps(recipe),
                category=new_category,
            )
            meals = {meal: info for meal, info in read_all_meals(db_file).items()}
            window["-MEAL_LIST-"].update(sorted([capwords(meal) for meal in meals.keys()]))
            window["-MEAL_INGREDIENTS_LIST-"].update([])
            window["-RECIPE_LINK-"].update(value="Paste Link Here (Optional)")
            recipe = ""
            window["-RECIPE_NOTE-"].update(visible=False)
            window["-CFILTER-"].update(
                set_to_index=[0],
                values=["All"] + list(set([capwords(meal["category"]) for meal in meals.values()])),
            )
            window.perform_long_operation(
                lambda: send_database_to_remote(sftp, username, password), "Done"
            )

        else:
            error_window("No Meal Added")

    if event in ["New Recipe", "-RECIPE-"]:
        basic_recipe = {}
        basic_recipe["ingredients"] = {}
        basic_recipe["directions"] = ""
        basic_recipe["title"] = ""
        basic_recipe["subtitle"] = ""
        basic_recipe["recipe_category"] = "Dinner"
        new_recipe_name = ""

        recipe = recipes(capwords(new_recipe_name), recipe_data=basic_recipe)

        if not recipe:
            continue

        if not recipe["directions"]:
            recipe["directions"] = ""

        basic_ingredients = [
            ingredient["ingredient"] for ingredient in recipe["ingredients"].values()
        ]
        new_meal = recipe["title"].lower()
        new_ingredients = ", ".join(basic_ingredients).lower() if basic_ingredients else new_meal

        new_category = recipe["recipe_category"].lower() if recipe["recipe_category"] else "Dinner"

        meal_categories = list(dict.fromkeys(settings["meal_categories"]))
        meal_categories.append(capwords(new_category))
        meal_categories = list(dict.fromkeys(meal_categories))

        settings["meal_categories"] = meal_categories
        with open(file_path, "w") as fp:
            json.dump(settings, fp, sort_keys=True, indent=4)

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
            window["-MEAL_LIST-"].update(sorted([capwords(meal) for meal in meals.keys()]))
            window["-RECIPE_LINK-"].update(value="Paste Link Here (Optional)")
            recipe = ""
            window["-RECIPE_NOTE-"].update(visible=False)
            window["-CFILTER-"].update(
                set_to_index=[0],
                values=["All"] + list(set([capwords(meal["category"]) for meal in meals.values()])),
            )
            window.perform_long_operation(
                lambda: send_database_to_remote(sftp, username, password), "Done"
            )

        else:
            error_window("No Meal Added")

    if event == "-PICK_DATE-":
        date = popup_get_date()
        if not date:
            continue
        month, day, year = date
        selected_day = datetime.date(year=year, month=month, day=day)
        week_start = selected_day - datetime.timedelta(days=selected_day.weekday() % 7)

        picked_date = str(week_start)

        current_plan_dict = read_current_plans(db_file, picked_date)
        if current_plan_dict:
            picked_date = str(current_plan_dict["date"])
        else:
            current_plan_dict = blank_plan_dict
        current_plan_dict = generate_plan_shopping_list(current_plan_dict)
        window["-WEEK-"].update(f"Week of {picked_date}")

    if event == "-AVAILABLE_PLANS-":
        all_plans = read_all_plans(db_file)
        available_plans = list(all_plans.keys())
        confirm, selected_plan = sg.Window(
            "Available Meal Plans",
            [
                [sg.Text("Available Meal Plans", font=("Arial", 16), justification="c")],
                [sg.Listbox(available_plans, font=("Arial", 12), size=(40, 20))],
                [
                    sg.Button("View Plan"),
                    sg.Button("Load Plan"),
                    sg.Button("Delete"),
                    sg.Button("Export"),
                    sg.Text("", expand_x=True),
                    sg.Button("Cancel"),
                ],
            ],
            disable_close=False,
        ).read(close=True)

        if not selected_plan[0]:
            continue

        if confirm in (None, "Cancel"):
            continue

        if confirm == "Load Plan":
            plan_key = selected_plan[0][0]

            current_plan_dict = read_current_plans(db_file, plan_key)
            if current_plan_dict:
                picked_date = str(current_plan_dict["date"])

                current_plan_dict = generate_plan_shopping_list(current_plan_dict)

            continue

        if confirm == "Export" and selected_plan[0]:
            export_plan_path = export_plan(selected_plan)
            if not export_plan_path:
                continue
            sg.popup_ok(f"Saved to {export_plan_path}")
            continue

        if confirm == "Delete" and selected_plan[0]:
            plan_key = selected_plan[0][0]

            confirmation = sg.popup_ok_cancel(f"Permenantly delete plan for week of {plan_key}?")
            if confirmation == "Cancel":
                continue

            remove_plan(db_file, plan_key)
            confirmation = sg.popup_ok(f"Plan for week of {plan_key}\npermentantly deleted")
            window.perform_long_operation(
                lambda: send_database_to_remote(sftp, username, password), "Done"
            )
            continue

        if confirm == "View Plan":

            plan_key = selected_plan[0][0]
            plan = all_plans[plan_key]

            plan_text = []
            days_text = []
            i = 0

            weeks_dates = [
                datetime.datetime.strptime(plan["date"], "%Y-%m-%d").date()
                + datetime.timedelta(days=x)
                for x in range(7)
            ]

            for day, meal in plan["meals"].items():
                meal = ", ".join(meal) if meal else ""
                days_text.append(
                    f"{day} {str(weeks_dates[i].month)}/{str(weeks_dates[i].day)}: {meal}"
                )
                i += 1

            days_text = "\n".join(days_text)
            plan_ingredients = "\n".join(textwrap.wrap(plan["ingredients"], 60))

            plan_text.append(f"{days_text}\n\nPlan Ingredients:\n{plan_ingredients}\n")
            plan_text = "\n\n".join(plan_text)

            confirm_export, _ = sg.Window(
                "Available Meal Plans",
                [
                    [sg.Text(f"Plan for {plan['date']}", font=("Arial", 16), justification="c")],
                    [sg.Multiline(plan_text, font=("Arial", 12), size=(60, 20), disabled=True)],
                    [sg.Button("Okay"), sg.Button("Export")],
                ],
                disable_close=False,
            ).read(close=True)

            if confirm_export == "Export":
                export_plan_path = export_plan(selected_plan)
                sg.popup_ok(f"Saved to {export_plan_path}")
                continue

    if event == "-TABLE-":

        table_right_click = default_table_right_click = [
            "&Right",
            ["Clear Row::table", sg.MENU_SEPARATOR_LINE,],
        ]

        if not values["-TABLE-"]:
            window["-TABLE-"].set_right_click_menu(default_table_right_click)
            continue

        selected_row = values["-TABLE-"][0]

        available_foods = current_plan_dict["meals"][gui_table[selected_row][0]]

        if not available_foods:
            window["-TABLE-"].set_right_click_menu(default_table_right_click)

        if available_foods:
            for meal in available_foods:
                add_meal_to_right_click_menu(table_right_click, meal, selected_row)

        window["-TABLE-"].set_right_click_menu(table_right_click)

    if (
        event.split("::")[0]
        in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",]
        and values["-TABLE-"]
    ):
        selected_row = values["-TABLE-"][0]

        chosen_day = event.split("::")[0]
        chosen_food = event.split("::")[1]

        current_plan_dict["meals"][gui_table[selected_row][0]].remove(chosen_food)

        if not len(current_plan_dict["meals"][chosen_day]):
            current_plan_dict["meals"][chosen_day] = [chosen_food]

        elif current_plan_dict["meals"][chosen_day] == [chosen_food]:
            continue

        else:
            current_plan_dict["meals"][chosen_day] = current_plan_dict["meals"][chosen_day] + [
                chosen_food
            ]

        gui_table = [
            [day] + [", ".join(meals)] for day, meals in current_plan_dict["meals"].items()
        ]

        plan_meals = [
            meal.lower() for meals in current_plan_dict["meals"].values() for meal in meals if meal
        ]

        window["-TABLE-"].update(values=gui_table)
        window["-MEAL_LIST-"].update(set_to_index=[])
        window["-TABLE-"].set_right_click_menu(default_table_right_click)

        add_plan(db_file, current_plan_dict, True)
        window.perform_long_operation(
            lambda: send_database_to_remote(sftp, username, password), "Done"
        )
    if "View Recipe::" in event and values["-TABLE-"]:
        chosen_food = event.split("::")[-1]

        if not chosen_food:
            continue

        recipe = read_meal_recipe(db_file, chosen_food)
        w = display_recipe(recipe)

    if "Delete Item::" in event and values["-TABLE-"]:
        chosen_food = event.split("::")[-1]

        selected_row = values["-TABLE-"][0]

        if not chosen_food:
            continue

        current_plan_dict["meals"][gui_table[selected_row][0]].remove(chosen_food)

        current_plan_dict = generate_plan_shopping_list(current_plan_dict)

        add_plan(db_file, current_plan_dict, True)
        window.perform_long_operation(
            lambda: send_database_to_remote(sftp, username, password), "Done"
        )
        window["-MEAL_LIST-"].update(set_to_index=[])
        window["-TABLE-"].set_right_click_menu(default_table_right_click)

    if event == "Clear Row::table":
        for row in values["-TABLE-"]:
            current_plan_dict["meals"][gui_table[row][0]] = ""

            current_plan_dict = generate_plan_shopping_list(current_plan_dict)

            add_plan(db_file, current_plan_dict, True)
            window.perform_long_operation(
                lambda: send_database_to_remote(sftp, username, password), "Done"
            )

            window["-MEAL_LIST-"].update(set_to_index=[])
            window["-TABLE-"].set_right_click_menu(default_table_right_click)

    if event == "Load Database":

        new_file_path = sg.popup_get_file(
            "Load new Database", title="Load Database", file_types=((".db"),), font=("Arial", 12),
        )
        if not new_file_path:
            continue
        os.remove(db_file)
        shutil.copyfile(new_file_path, db_file)
        window["-MEAL_LIST-"].update(
            values=sorted([capwords(meal) for meal in read_all_meals(db_file).keys()])
        )
        meals = {meal: info for meal, info in read_all_meals(db_file).items()}
        current_plan_dict = read_current_plans(db_file, str(start))

        if not current_plan_dict:
            current_plan_dict = blank_plan_dict

        current_plan_dict = generate_plan_shopping_list(current_plan_dict)
        window.perform_long_operation(
            lambda: send_database_to_remote(sftp, username, password), "Done"
        )
        window["-CFILTER-"].update(
            set_to_index=[0],
            values=["All"] + list(set([capwords(meal["category"]) for meal in meals.values()])),
        )

    if event == "Export Database":
        export_database_path = sg.popup_get_file(
            "Export Database",
            title="Export Database",
            save_as=True,
            default_extension=".db",
            file_types=((".db"),),
            font=("Arial", 12),
        )
        if not export_database_path:
            continue
        shutil.copyfile(db_file, export_database_path)

        # Future to expand for more options - will need to update the databse for additional columns

    if (event in ("Edit Recipe", "Edit Recipe::meal") and values["-MEAL_LIST-"]) or (
        "Edit Recipe::" in event and values["-TABLE-"]
    ):

        if "::meal" in event:
            selected_meal = values["-MEAL_LIST-"][0].lower()
        else:
            selected_meal = event.split("::")[-1]

        existing_recipe = read_meal_recipe(db_file, selected_meal)

        recipe = recipes(capwords(selected_meal), recipe_data=existing_recipe)
        if recipe:
            confirm = sg.popup_ok_cancel(
                "Overwrite existing recipe?",
                icon=base64.b64encode(open(str(icon_file), "rb").read()),
            )
            if confirm == "OK":
                update_meal_recipe(db_file, json.dumps(recipe), selected_meal)
                basic_ingredients = [
                    capwords(ingredient["ingredient"])
                    for ingredient in recipe["ingredients"].values()
                ]
                edited_ingredients = ", ".join(sorted(list(set(basic_ingredients))))
                update_meal_name(db_file, recipe["title"].lower(), selected_meal)
                update_meal_ingredients(db_file, recipe["title"].lower(), edited_ingredients)
                update_meal_category(db_file, recipe["recipe_category"], recipe["title"].lower())
                meals = {meal: info for meal, info in read_all_meals(db_file).items()}
                window["-MEAL_LIST-"].update(
                    values=sorted([capwords(meal) for meal in read_all_meals(db_file).keys()])
                )
                meal_categories = ["All"] + list(
                    set(
                        settings["meal_categories"]
                        + list(set([capwords(meal["category"]) for meal in meals.values()]))
                    )
                )

                settings["meal_categories"] = meal_categories
                with open(file_path, "w") as fp:
                    json.dump(settings, fp, sort_keys=True, indent=4)

                window["-MEAL_INGREDIENTS_LIST-"].update([])
                window["-CFILTER-"].update(
                    set_to_index=[0], values=meal_categories,
                )
                current_plan_dict = generate_plan_shopping_list(current_plan_dict)
                window.perform_long_operation(
                    lambda: send_database_to_remote(sftp, username, password), "Done"
                )

            else:
                sg.popup_ok("Recipe not overwritten")

    if event == "Delete::meal" and values["-MEAL_LIST-"]:
        selected_meal = values["-MEAL_LIST-"][0].lower()
        confirm_delete = sg.popup_yes_no(f"Confirm delete: {selected_meal}")
        if confirm_delete == "Yes":
            remove_meal(db_file, selected_meal)
            meals = {meal: info for meal, info in read_all_meals(db_file).items()}
            window["-MEAL_LIST-"].update(
                sorted([capwords(meal) for meal in read_all_meals(db_file).keys()])
            )
            window["-CFILTER-"].update(
                set_to_index=[0],
                values=["All"] + list(set([capwords(meal["category"]) for meal in meals.values()])),
            )
            window["-MEAL_INGREDIENTS_LIST-"].update([])
            window.perform_long_operation(
                lambda: send_database_to_remote(sftp, username, password), "Done"
            )

        else:
            error_window(f"Canceled\n{selected_meal} was not deleted")

    if event == "-CFILTER-":
        if values["-CFILTER-"] == "All":
            values["-CFILTER-"] = ""
        filtered_meals = sorted(
            [capwords(meal) for meal in matchingKeys(meals, values["-CFILTER-"])]
        )
        window["-MEAL_LIST-"].update(filtered_meals)

    if event == "-MFILTER-":
        # Typing in the search box will filter the main meal list based on the name of the meal
        # as well as ingredients in any meal
        filtered_meals = sorted(
            [capwords(meal) for meal in matchingKeys(meals, values["-MFILTER-"])]
        )
        window["-MEAL_LIST-"].update(filtered_meals)

    if event == "-MEAL_LIST-":
        # Choosing an item from the list of meals will update the ingredients list for that meal
        menu_bar_layout = update_menu_bar_definition(auth, sftp)
        window["-MENU-"].update(menu_definition=menu_bar_layout)

        meal_selection_rightclick_menu_def = (
            ["&Right", ["View Recipe::meal", "Edit Recipe::meal", "Delete::meal"]]
            if values["-MEAL_LIST-"]
            else ["&Right", ["!View Recipe::meal", "!Edit Recipe::meal", "!Delete::meal"]]
        )

        window["-MEAL_LIST-"].set_right_click_menu(meal_selection_rightclick_menu_def)

        if not values["-MEAL_LIST-"]:
            continue

        selected_meal = values["-MEAL_LIST-"][0].lower()
        recipe = read_meal_recipe(db_file, selected_meal)

        if recipe:
            window["-VIEW_RECIPE-"].update(disabled=False)
        else:
            window["-VIEW_RECIPE-"].update(disabled=True)

        ingredients_list = meals[selected_meal]["ingredients"]
        window["-MEAL_INGREDIENTS_LIST-"].update(
            sorted([capwords(ingredient) for ingredient in ingredients_list])
        )
        window["-CATEGORY_TEXT-"].update(
            visible=True, value=capwords(meals[selected_meal]["category"])
        )

    if event == "-VIEW_RECIPE-" or event == "View Recipe::meal":
        w = display_recipe(recipe)

    if event in ("-MON-", "-TUE-", "-WED-", "-THU-", "-FRI-", "-SAT-", "-SUN-"):
        all_days = [f"-{day.upper()}-" for day in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]]
        for day in [day for day in all_days if day != event]:
            window[day].update(value=False)

    if event == "-CANCEL-":
        # Meal selection Cancel, clear out all the values for the checkboxes and meal list and
        # ingredients for that selected meal
        window["-MON-"].update(value=False)
        window["-TUE-"].update(value=False)
        window["-WED-"].update(value=False)
        window["-THU-"].update(value=False)
        window["-FRI-"].update(value=False)
        window["-SAT-"].update(value=False)
        window["-SUN-"].update(value=False)
        window["-MEAL_LIST-"].update(sorted([capwords(meal) for meal in meals.keys()]))
        window["-MEAL_INGREDIENTS_LIST-"].update([])
        window["-CFILTER-"].update(set_to_index=[0])
        window["-MFILTER-"].update(value="")
        window["-VIEW_RECIPE-"].update(disabled=True)
        window["-CATEGORY_TEXT-"].update(visible=False, value="category")
        menu_bar_layout = update_menu_bar_definition(auth, sftp)
        window["-MENU-"].update(menu_definition=menu_bar_layout)
        window["-MEAL_LIST-"].set_right_click_menu(
            ["&Right", ["!View Recipe::meal", "!Edit Recipe::meal", "!Delete::meal"]]
        )

    if event == "-PLAN-CLEAR-":
        # Empty out the table and return it to the default values
        current_plan_dict = blank_plan_dict

        current_plan_dict = generate_plan_shopping_list(current_plan_dict)

    if event == "-ADD_TO_PLAN-":
        # Add a selected meal to a day of the week in the plan table
        # selected_meal = ", ".join(values["-MEAL_LIST-"])
        selected_meal = values["-MEAL_LIST-"]

        # If no meal is selected when the 'add to plan' button is pressed
        # show popup warning and do nothing
        if not selected_meal:
            error_window("No Meal Selected")
            continue

        days_of_week = {
            "Sunday": values["-SUN-"],
            "Monday": values["-MON-"],
            "Tuesday": values["-TUE-"],
            "Wednesday": values["-WED-"],
            "Thursday": values["-THU-"],
            "Friday": values["-FRI-"],
            "Saturday": values["-SAT-"],
        }
        day_index = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6,
        }
        selected_days = [day for day, val in days_of_week.items() if val == True]

        # If no day is selected when the 'add to plan' button is pressed
        # show popup warning and do nothing
        if not selected_days:
            error_window("No Day Selected")
            continue

        # For each data selected when the 'add to plan' button is pressed, update the appropriate
        # row in the plan table to reflect the meal selection, check if there is already an
        # item in place, and if so, add to it (useful for adding salad + main meal)
        for day in selected_days:
            if not len(current_plan_dict["meals"][day]):
                current_plan_dict["meals"][day] = selected_meal

            elif all(item in current_plan_dict["meals"][day] for item in selected_meal):
                continue

            elif any(item in current_plan_dict["meals"][day] for item in selected_meal):
                selected_meal = [
                    item for item in selected_meal if item not in current_plan_dict["meals"][day]
                ]

            else:
                current_plan_dict["meals"][day] = current_plan_dict["meals"][day] + selected_meal

        current_plan_dict = generate_plan_shopping_list(current_plan_dict)

        # Check if we're creating a new plan or updating an existing one
        all_plans = read_all_plans(db_file)
        overwrite = True if current_plan_dict["date"] in all_plans.keys() else False

        add_plan(db_file, current_plan_dict, overwrite)
        window.perform_long_operation(
            lambda: send_database_to_remote(sftp, username, password), "Done"
        )
