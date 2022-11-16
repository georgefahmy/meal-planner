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
from recipe_interface import recipes
from recipe_viewer import recipe_viewer
from recipe_scrapers import scrape_me
from recipe_scrapers.settings import RecipeScraperSettings
from recipe_scrapers.settings import default
from string import capwords

if sys.version_info.minor >= 10:
    from itertools import pairwise
else:
    from itertools import tee

    def pairwise(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)


settings = RecipeScraperSettings()
settings._configure()

try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()

file_path = os.path.join(wd, "settings.json")

settings = json.load(open(file_path, "r"))
db_file = os.path.join(wd, "database.db")
meal_categories = list(dict.fromkeys(settings["meal_categories"]))
make_database(db_file)

today = datetime.date.today()
today_name = today.strftime("%A")

start = today - datetime.timedelta(days=(datetime.datetime.today().weekday()) % 7)
weeks_dates = [start + datetime.timedelta(days=x) for x in range(7)]
picked_date = str(start)

blank_plan_dict = {
    "date": str(start),
    "ingredients": [],
    "meals": {
        "Monday": [""],
        "Tuesday": [""],
        "Wednesday": [""],
        "Thursday": [""],
        "Friday": [""],
        "Saturday": [""],
        "Sunday": [""],
    },
}

blank_gui_table = [[day] + meals for day, meals in blank_plan_dict["meals"].items()]


# --------------------------------- Define Layout ---------------------------------

# --------------------------------MAIN LEFT COLUMN---------------------------------
# Top left quadrant - three columns, list of meals, selection checkboxes, submit or cancel

meal_selection_rightclick_menu_def = [
    "&Right",
    [
        "Change Meal Name",
        "Edit Category",
        "Edit Ingredients",
        ["Add Ingredient", "Edit Ingredients"],
        "Update Recipe",
        "Delete Meal",
    ],
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
input_text = [
    sg.Text("New Meal", font=("Arial", 18), size=(50, 2), justification="c"),
]
input_section = [
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
                    layout=[input_text, input_section],
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

gui_table = [[day] + meals for day, meals in current_plan_dict["meals"].items()]

table_right_click = [
    "&Right",
    ["Edit Selection::edit", "Delete::table"],
]

meal_plan_section = [
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
                    right_click_menu=table_right_click,
                    tooltip="Right click to remove items",
                    size=(40, 40),
                    hide_vertical_scroll=True,
                    key="-TABLE-",
                )
            ],
        ],
        element_justification="c",
    ),
]
plan_section_buttons = [
    sg.Column(
        [[sg.Button("Clear", visible=True, key="-PLAN-CLEAR-", enable_events=True),]],
        element_justification="c",
    )
]
# Get meal and ingredient information from the database
meals = {meal: info for meal, info in read_all_meals(db_file).items()}
plan_meals = [
    meal.lower() for meals in current_plan_dict["meals"].values() for meal in meals if meal
]
plan_ingredients = sorted(
    list(
        set(
            capwords(
                ", ".join([", ".join(meals[meal]["ingredients"]) for meal in plan_meals if meal])
            ).split(", ")
        )
    )
)
plan_ingredients = sorted(
    [plan_ingredient for plan_ingredient in plan_ingredients if plan_ingredient]
)
# Bottom Right Quadrant - Table of ingredients
ingredients_list_section = [
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
                sg.Listbox(
                    values=plan_ingredients,
                    font=("Arial", 14),
                    size=(60, 17),
                    key="-PLAN_INGREDIENTS_LIST-",
                    enable_events=False,
                    pad=(0, 0),
                )
            ],
        ],
        element_justification="c",
        pad=(0, 0),
    )
]

main_right_column = [
    sg.Column(
        [
            [
                sg.Frame(
                    "Weekly Plan",
                    layout=[meal_plan_section, plan_section_buttons],
                    element_justification="c",
                    size=(620, 230),
                    pad=(0, 0),
                )
            ],
            [
                sg.Frame(
                    "Shopping List",
                    layout=[ingredients_list_section],
                    element_justification="c",
                    size=(620, 350),
                    pad=(0, 0),
                )
            ],
        ],
        element_justification="c",
    )
]
menu_bar_layout = [
    ["&File", ["Load Database", "Export Database"]],
    ["Edit", ["!Edit Meal", "!Edit Ingredients"]],
    ["Recipes", ["New Recipe", "View Recipes", "!Edit recipe"]],
    ["Help", ["!About", "!How To", "!Feedback"]],
]

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


# --------------------------------- Create the Window ---------------------------------
# Use the full layout to create the window object
icon_file = wd + "/resources/burger-10956.png"
sg.set_options(icon=base64.b64encode(open(str(icon_file), "rb").read()))
themes = sg.theme_list()
chosen_theme = choice(themes)
sg.set_options(alpha_channel=0.99)
sg.theme("TanBlue")

window = sg.Window("Meal Planner PRO", full_layout, resizable=True, size=(1320, 660), finalize=True)
window.refresh()

# Get meal and ingredient information from the database
meals = {meal: info for meal, info in read_all_meals(db_file).items()}


window["-WEEK-"].update(value="Week of " + picked_date)
plan_ingredients = None

# Start the window loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    if event:
        # DEBUG to print out the events and values
        print(event, values)

    if event in ["View Recipes"]:
        recipe_viewer()
        meals = {meal: info for meal, info in read_all_meals(db_file).items()}
        window["-MEAL_LIST-"].update(
            sorted([capwords(meal) for meal in read_all_meals(db_file).keys()])
        )

    if event in ("Update Recipe", "Edit Recipe"):
        selected_meal = values["-MEAL_LIST-"][0].lower()
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
                update_meal_ingredients(db_file, selected_meal, edited_ingredients)
                meals = {meal: info for meal, info in read_all_meals(db_file).items()}
                window["-MEAL_INGREDIENTS_LIST-"].update(values=sorted(basic_ingredients))

            else:
                sg.popup_ok("Recipe not overwritten")

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
            window["-RECIPE_LINK-"].update(value="Paste Link Here (Optional)")
            recipe = ""
            window["-RECIPE_NOTE-"].update(visible=False)
            window["-CFILTER-"].update(set_to_index=[0], values=meal_categories)

        else:
            sg.Window(
                "ERROR",
                [
                    [sg.Text("No Meal Added", font=("Arial", 16), justification="c")],
                    [sg.Button("Okay")],
                ],
                disable_close=False,
            ).read(close=True)

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
            window["-CFILTER-"].update(set_to_index=[0], values=meal_categories)

        else:
            sg.Window(
                "ERROR",
                [
                    [sg.Text("No Meal Added", font=("Arial", 16), justification="c")],
                    [sg.Button("Okay")],
                ],
                disable_close=False,
            ).read(close=True)

    if event == "-PICK_DATE-":
        date = popup_get_date()
        if not date:
            continue
        month, day, year = date
        selected_day = datetime.date(year=year, month=month, day=day)
        week_start = selected_day - datetime.timedelta(days=selected_day.weekday() % 7)
        window["-WEEK-"].update(f"Week of {str(week_start)}")
        current_plan_dict["date"] = str(week_start)
        picked_date = str(week_start)

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

            plan = read_current_plans(db_file, plan_key)
            if plan:
                gui_table = [[day] + [", ".join(meals)] for day, meals in plan["meals"].items()]
                picked_date = str(plan["date"])
                plan_meals = [
                    meal.lower() for meals in plan["meals"].values() for meal in meals if meal
                ]

                plan_ingredients = []
                for meal in plan_meals:
                    meal_recipe = read_meal_recipe(db_file, meal)
                    if meal_recipe:
                        for ingredient in meal_recipe["ingredients"].values():
                            plan_ingredients.append(
                                re.sub(
                                    "\s+",
                                    " ",
                                    " ".join(
                                        [
                                            str(ingredient["quantity"])
                                            if ingredient["quantity"]
                                            else "1",
                                            ingredient["units"] if ingredient["units"] else "",
                                            capwords(ingredient["ingredient"])
                                            if ingredient["ingredient"]
                                            else "",
                                        ]
                                    ),
                                ).strip()
                            )
                    else:
                        plan_ingredients.extend(
                            list(set(capwords(", ".join(meals[meal]["ingredients"])).split(", ")))
                        )

                plan_ingredients = list(set(plan_ingredients))
                plan_ingredients = sorted(
                    [plan_ingredient for plan_ingredient in plan_ingredients if plan_ingredient]
                )

                # Update and clear the checkboxes once the plan is loaded
                current_plan_dict = plan
                window["-WEEK-"].update("Week of " + plan["date"])
                window["-TABLE-"].update(values=gui_table)
                window["-PLAN_INGREDIENTS_LIST-"].update(plan_ingredients)

            continue

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

        if confirm == "Export" and selected_plan[0]:
            export_plan_path = export_plan(selected_plan)
            sg.popup_ok(f"Saved to {export_plan_path}")
            continue

        if confirm == "Delete" and selected_plan[0]:
            plan_key = selected_plan[0][0]

            confirmation = sg.popup_ok_cancel(f"Permenantly delete plan for week of {plan_key}?")
            if confirmation == "Cancel":
                continue

            remove_plan(db_file, plan_key)
            confirmation = sg.popup_ok(f"Plan for week of {plan_key}\npermentantly deleted")
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

    if event == "Edit Selection::edit":
        if not values["-TABLE-"]:
            continue

        selected_row = values["-TABLE-"][0]
        available_foods = current_plan_dict["meals"][gui_table[selected_row][0]]
        confirm, chosen_food = sg.Window(
            "Edit Selected Day",
            [
                [sg.Text("Remove Specific Meals", font=("Arial", 14), justification="c")],
                [sg.Listbox(values=available_foods, font=("Arial", 14), size=(200, 6))],
                [sg.Button("Okay"), sg.Button("Cancel")],
            ],
            disable_close=False,
            size=(225, 200),
        ).read(close=True)

        if confirm == "Cancel":
            continue

        if not chosen_food[0]:
            continue

        chosen_food = chosen_food[0][0]
        current_plan_dict["meals"][gui_table[selected_row][0]].remove(chosen_food)
        gui_table = [
            [day] + [", ".join(meals)] for day, meals in current_plan_dict["meals"].items()
        ]
        plan_meals = [
            meal.lower() for meals in current_plan_dict["meals"].values() for meal in meals if meal
        ]

        plan_ingredients = []
        for meal in plan_meals:
            meal_recipe = read_meal_recipe(db_file, meal)
            if meal_recipe:
                for ingredient in meal_recipe["ingredients"].values():
                    plan_ingredients.append(
                        re.sub(
                            "\s+",
                            " ",
                            " ".join(
                                [
                                    str(ingredient["quantity"]) if ingredient["quantity"] else "1",
                                    ingredient["units"] if ingredient["units"] else "",
                                    capwords(ingredient["ingredient"])
                                    if ingredient["ingredient"]
                                    else "",
                                ]
                            ),
                        ).strip()
                    )
            else:
                plan_ingredients.extend(
                    list(set(capwords(", ".join(meals[meal]["ingredients"])).split(", ")))
                )

        plan_ingredients = list(set(plan_ingredients))
        plan_ingredients = sorted(
            [plan_ingredient for plan_ingredient in plan_ingredients if plan_ingredient]
        )

        window["-PLAN_INGREDIENTS_LIST-"].update(plan_ingredients)
        window["-TABLE-"].update(values=gui_table)

        plan_ingredients = ", ".join(plan_ingredients)
        current_plan_dict["ingredients"] = plan_ingredients

        add_plan(db_file, current_plan_dict, True)

    if event == "Delete::table":
        for row in values["-TABLE-"]:
            current_plan_dict["meals"][gui_table[row][0]] = [""]

            gui_table = [
                [day] + [", ".join(meals)] for day, meals in current_plan_dict["meals"].items()
            ]
            plan_meals = [
                meal.lower()
                for meals in current_plan_dict["meals"].values()
                for meal in meals
                if meal
            ]

            plan_ingredients = []
            for meal in plan_meals:
                meal_recipe = read_meal_recipe(db_file, meal)
                if meal_recipe:
                    for ingredient in meal_recipe["ingredients"].values():
                        plan_ingredients.append(
                            re.sub(
                                "\s+",
                                " ",
                                " ".join(
                                    [
                                        str(ingredient["quantity"])
                                        if ingredient["quantity"]
                                        else "1",
                                        ingredient["units"] if ingredient["units"] else "",
                                        capwords(ingredient["ingredient"])
                                        if ingredient["ingredient"]
                                        else "",
                                    ]
                                ),
                            ).strip()
                        )
                else:
                    plan_ingredients.extend(
                        list(set(capwords(", ".join(meals[meal]["ingredients"])).split(", ")))
                    )

            plan_ingredients = list(set(plan_ingredients))
            plan_ingredients = sorted(
                [plan_ingredient for plan_ingredient in plan_ingredients if plan_ingredient]
            )

            window["-PLAN_INGREDIENTS_LIST-"].update(plan_ingredients)
            window["-TABLE-"].update(values=gui_table)

            plan_ingredients = ", ".join(plan_ingredients)
            current_plan_dict["ingredients"] = plan_ingredients

            add_plan(db_file, current_plan_dict, True)

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

        gui_table = [
            [day] + [", ".join(meals)] for day, meals in current_plan_dict["meals"].items()
        ]

        plan_meals = [
            meal.lower() for meals in current_plan_dict["meals"].values() for meal in meals if meal
        ]

        plan_ingredients = []
        for meal in plan_meals:
            meal_recipe = read_meal_recipe(db_file, meal)
            if meal_recipe:
                for ingredient in meal_recipe["ingredients"].values():
                    plan_ingredients.append(
                        re.sub(
                            "\s+",
                            " ",
                            " ".join(
                                [
                                    str(ingredient["quantity"]) if ingredient["quantity"] else "1",
                                    ingredient["units"] if ingredient["units"] else "",
                                    capwords(ingredient["ingredient"])
                                    if ingredient["ingredient"]
                                    else "",
                                ]
                            ),
                        ).strip()
                    )
            else:
                plan_ingredients.extend(
                    list(set(capwords(", ".join(meals[meal]["ingredients"])).split(", ")))
                )

        plan_ingredients = list(set(plan_ingredients))
        plan_ingredients = sorted(
            [plan_ingredient for plan_ingredient in plan_ingredients if plan_ingredient]
        )

        # Update and clear the checkboxes once the database is loaded
        window["-TABLE-"].update(values=gui_table)
        window["-PLAN_INGREDIENTS_LIST-"].update(plan_ingredients)

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

    if event in ("Change Meal Name", "Edit Meal"):
        if values["-MEAL_LIST-"]:
            selected_meal = values["-MEAL_LIST-"][0].lower()
            _, new_meal_name = sg.Window(
                "Change Meal Name",
                [
                    [sg.Text("Change Name of Meal", font=("Arial", 14), justification="c")],
                    [
                        sg.Input(
                            default_text=capwords(selected_meal),
                            font=("Arial", 14),
                            key="-NEWMEALNAME-",
                            enable_events=False,
                        )
                    ],
                    [sg.Button("Okay")],
                ],
                disable_close=False,
                size=(225, 100),
            ).read(close=True)
            if not new_meal_name["-NEWMEALNAME-"]:
                continue
            new_meal_name = new_meal_name["-NEWMEALNAME-"].lower()
            recipe = read_meal_recipe(db_file, selected_meal)
            if recipe:
                recipe["title"] = capwords(new_meal_name)
                update_meal_recipe(db_file, json.dumps(recipe), new_meal_name)

            update_meal_name(db_file, new_meal_name, selected_meal)
            meals = {meal: info for meal, info in read_all_meals(db_file).items()}
            window["-MEAL_LIST-"].update(
                sorted([capwords(meal) for meal in read_all_meals(db_file).keys()])
            )

    if event == "Edit Category":
        if values["-MEAL_LIST-"]:
            selected_meal = values["-MEAL_LIST-"][0].lower()
            _, new_category = sg.Window(
                "Change Meal Category",
                [
                    [sg.Text("Change Meal Category", font=("Arial", 14), justification="c")],
                    [
                        sg.Combo(
                            values=meal_categories[1:],
                            font=("Arial", 14),
                            key="-NEWMEALCATEGORY-",
                            enable_events=False,
                        )
                    ],
                    [sg.Button("Okay")],
                ],
                disable_close=False,
                size=(225, 100),
            ).read(close=True)
            if not new_category["-NEWMEALCATEGORY-"]:
                continue
            new_category = new_category["-NEWMEALCATEGORY-"].lower()
            meal_categories = list(dict.fromkeys(settings["meal_categories"]))
            meal_categories.append(capwords(new_category))
            meal_categories = list(dict.fromkeys(meal_categories))
            settings["meal_categories"] = meal_categories
            with open(file_path, "w") as fp:
                json.dump(settings, fp, sort_keys=True, indent=4)
            update_meal_category(db_file, new_category, selected_meal)
            meals = {meal: info for meal, info in read_all_meals(db_file).items()}
            window["-MEAL_LIST-"].update(
                sorted([capwords(meal) for meal in read_all_meals(db_file).keys()])
            )
            window["-NEWCATEGORY-"].update(set_to_index=[0], values=meal_categories[1:])
            window["-CFILTER-"].update(set_to_index=[0], values=meal_categories)

    if event == "Add Ingredient":
        if values["-MEAL_LIST-"]:
            selected_meal = values["-MEAL_LIST-"][0].lower()
            ingredients = read_specific_meals(db_file, selected_meal)[selected_meal]
            _, new_ingredients = sg.Window(
                "Add Ingredients",
                [
                    [
                        sg.Text(
                            "Add Ingredient(s) - Separate w/ comma",
                            font=("Arial", 14),
                            justification="c",
                        )
                    ],
                    [sg.Input(key="-NEWINGREDIENTS-", font=("Arial", 14), enable_events=False)],
                    [sg.Button("Okay")],
                ],
                disable_close=False,
                size=(325, 100),
            ).read(close=True)
            if not new_ingredients["-NEWINGREDIENTS-"]:
                continue
            new_ingredients = new_ingredients["-NEWINGREDIENTS-"].lower().split(", ")
            ingredients.extend(
                [ingredient for ingredient in new_ingredients if ingredient not in ingredients]
            )
            updated_ingredients = ", ".join(ingredients)
            update_meal_ingredients(db_file, selected_meal, updated_ingredients)
            meals = {meal: info for meal, info in read_all_meals(db_file).items()}
            ingredients_list = meals[selected_meal]["ingredients"]
            window["-MEAL_INGREDIENTS_LIST-"].update(
                [capwords(ingredient) for ingredient in ingredients_list]
            )

    if event in "Edit Ingredients":
        if values["-MEAL_LIST-"]:
            selected_meal = values["-MEAL_LIST-"][0].lower()
            ingredients = read_specific_meals(db_file, selected_meal)[selected_meal]
            _, edited_ingredients = sg.Window(
                "Edit Ingredients",
                [
                    [sg.Text("Edit Ingredient(s)", font=("Arial", 14), justification="c",)],
                    [
                        sg.Multiline(
                            default_text=capwords(", ".join(sorted(ingredients))),
                            key="-EDITINGREDIENTS-",
                            enable_events=False,
                            font=("Arial", 14),
                            autoscroll=True,
                            rstrip=True,
                            size=(200, 5),
                        )
                    ],
                    [sg.Button("Okay")],
                ],
                disable_close=False,
                size=(400, 150),
            ).read(close=True)
            if not edited_ingredients["-EDITINGREDIENTS-"]:
                continue
            edited_ingredients = edited_ingredients["-EDITINGREDIENTS-"].lower().split(", ")
            edited_ingredients = ", ".join(sorted(list(set(edited_ingredients))))
            update_meal_ingredients(db_file, selected_meal, edited_ingredients)
            meals = {meal: info for meal, info in read_all_meals(db_file).items()}
            ingredients_list = meals[selected_meal]["ingredients"]
            window["-MEAL_INGREDIENTS_LIST-"].update(
                [capwords(ingredient) for ingredient in ingredients_list]
            )

    if event == "Delete Meal":
        if values["-MEAL_LIST-"]:
            selected_meal = values["-MEAL_LIST-"][0].lower()
            confirm_delete = sg.popup_yes_no(f"Confirm delete: {selected_meal}")
            if confirm_delete == "Yes":
                remove_meal(db_file, selected_meal)
                meals = {meal: info for meal, info in read_all_meals(db_file).items()}
                window["-MEAL_LIST-"].update(
                    sorted([capwords(meal) for meal in read_all_meals(db_file).keys()])
                )
                window["-MEAL_INGREDIENTS_LIST-"].update([])

            else:
                sg.Window(
                    "Canceled",
                    [
                        [
                            sg.Text(
                                f"Canceled\n{selected_meal} was not deleted",
                                font=("Arial", 14),
                                justification="c",
                                expand_x=True,
                            )
                        ],
                        [sg.Button("Okay")],
                    ],
                    disable_close=False,
                ).read(close=True)

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
        menu_bar_layout = [
            ["&File", ["Load Database", "Export Database"]],
            ["Edit", ["Edit Meal", "Edit Ingredients"]],
            ["Recipes", ["New Recipe", "View Recipes", "Edit recipe"]],
            ["Help", ["!About", "!How To", "!Feedback"]],
        ]
        window["-MENU-"].update(menu_definition=menu_bar_layout)

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
    if event == "-VIEW_RECIPE-":
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
        menu_bar_layout = [
            ["&File", ["Load Database", "Export Database"]],
            ["Edit", ["!Edit Meal", "!Edit Ingredients"]],
            ["Recipes", ["New Recipe", "View Recipes", "!Edit recipe"]],
            ["Help", ["!About", "!How To", "!Feedback"]],
        ]
        window["-MENU-"].update(menu_definition=menu_bar_layout)

    if event == "-PLAN-CLEAR-":
        # Empty out the table and return it to the default values
        current_plan_dict = blank_plan_dict
        plan_meals = [
            meal.lower() for meals in current_plan_dict["meals"].values() for meal in meals if meal
        ]

        plan_ingredients = []
        for meal in plan_meals:
            meal_recipe = read_meal_recipe(db_file, meal)
            if meal_recipe:
                for ingredient in meal_recipe["ingredients"].values():
                    plan_ingredients.append(
                        re.sub(
                            "\s+",
                            " ",
                            " ".join(
                                [
                                    str(ingredient["quantity"]) if ingredient["quantity"] else "1",
                                    ingredient["units"] if ingredient["units"] else "",
                                    capwords(ingredient["ingredient"])
                                    if ingredient["ingredient"]
                                    else "",
                                ]
                            ),
                        ).strip()
                    )
            else:
                plan_ingredients.extend(
                    list(set(capwords(", ".join(meals[meal]["ingredients"])).split(", ")))
                )

        plan_ingredients = list(set(plan_ingredients))
        plan_ingredients = sorted(
            [plan_ingredient for plan_ingredient in plan_ingredients if plan_ingredient]
        )
        window["-TABLE-"].update(blank_gui_table)
        window["-PLAN_INGREDIENTS_LIST-"].update([])

    if event == "-ADD_TO_PLAN-":
        # Add a selected meal to a day of the week in the plan table
        # selected_meal = ", ".join(values["-MEAL_LIST-"])
        selected_meal = values["-MEAL_LIST-"]

        # If no meal is selected when the 'add to plan' button is pressed
        # show popup warning and do nothing
        if not selected_meal:
            sg.Window(
                "ERROR",
                [
                    [sg.Text("No Meal Selected", font=("Arial", 16), justification="c")],
                    [sg.Button("Okay")],
                ],
                disable_close=False,
            ).read(close=True)
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
            sg.Window(
                "ERROR",
                [
                    [sg.Text("No Day Selected", font=("Arial", 16), justification="c")],
                    [sg.Button("Okay")],
                ],
                disable_close=False,
                size=(150, 80),
            ).read(close=True)
            continue

        # For each data selected when the 'add to plan' button is pressed, update the appropriate
        # row in the plan table to reflect the meal selection, check if there is already an
        # item in place, and if so, add to it (useful for adding salad + main meal)
        for day in selected_days:
            if not current_plan_dict["meals"][day][0]:
                current_plan_dict["meals"][day] = selected_meal

            elif current_plan_dict["meals"][day] == selected_meal:
                continue

            else:
                current_plan_dict["meals"][day] = current_plan_dict["meals"][day] + selected_meal

        gui_table = [
            [day] + [", ".join(meals)] for day, meals in current_plan_dict["meals"].items()
        ]

        # Update the table information with the plan meals and get the ingredients for those meals
        # then create a unique list that is sorted and put it into the ingredients listbox
        plan_meals = [
            meal.lower() for meals in current_plan_dict["meals"].values() for meal in meals if meal
        ]

        plan_ingredients = []
        for meal in plan_meals:
            meal_recipe = read_meal_recipe(db_file, meal)
            if meal_recipe:
                for ingredient in meal_recipe["ingredients"].values():
                    plan_ingredients.append(
                        re.sub(
                            "\s+",
                            " ",
                            " ".join(
                                [
                                    str(ingredient["quantity"]) if ingredient["quantity"] else "1",
                                    ingredient["units"] if ingredient["units"] else "",
                                    capwords(ingredient["ingredient"])
                                    if ingredient["ingredient"]
                                    else "",
                                ]
                            ),
                        ).strip()
                    )
            else:
                plan_ingredients.extend(
                    list(set(capwords(", ".join(meals[meal]["ingredients"])).split(", ")))
                )

        plan_ingredients = list(set(plan_ingredients))
        plan_ingredients = sorted(
            [plan_ingredient for plan_ingredient in plan_ingredients if plan_ingredient]
        )

        # Update and clear the checkboxes once the meal is submitted to the plan
        window["-TABLE-"].update(values=gui_table)
        window["-PLAN_INGREDIENTS_LIST-"].update(plan_ingredients)
        window["-MEAL_LIST-"].update(set_to_index=[])

        plan_ingredients = ", ".join(plan_ingredients)
        current_plan_dict["ingredients"] = plan_ingredients

        # Check if we're creating a new plan or updating an existing one
        all_plans = read_all_plans(db_file)
        overwrite = True if current_plan_dict["date"] in all_plans.keys() else False

        add_plan(db_file, current_plan_dict, overwrite)

        # Commenting this out so that I can make it optional later on with a user setting.
        # window["-MON-"].update(value=False)
        # window["-TUE-"].update(value=False)
        # window["-WED-"].update(value=False)
        # window["-THU-"].update(value=False)
        # window["-FRI-"].update(value=False)
        # window["-SAT-"].update(value=False)
        # window["-SUN-"].update(value=False)
