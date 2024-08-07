import base64
import json
import os
import re
import sys
import textwrap
from string import capwords

import PySimpleGUI as sg

from recipe_interface import recipes
from utils.sql_functions import (
    add_meal,
    file_path,
    read_all_meals,
    read_all_recipes,
    remove_meal,
)

if sys.version_info.minor >= 10:
    from itertools import pairwise
else:
    from itertools import tee

    def pairwise(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)


try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()

settings = json.load(open(os.path.join(wd, "settings.json"), "r"))
db_file = os.path.join(wd, "database.db")
meals = dict(read_all_meals(db_file).items())
settings["meal_categories"].remove("All")
meal_categories = ["All"] + list(
    set(
        (
            settings["meal_categories"]
            + list({capwords(meal["category"]) for meal in meals.values()})
        )
    )
)
settings["meal_categories"] = sorted(meal_categories)
with open(file_path, "w") as fp:
    json.dump(settings, fp, sort_keys=True, indent=4)


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
            [
                sg.Text(
                    "Available Recipes to View",
                    font=("Arial Bold", 18),
                    justification="c",
                )
            ],
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
        # if event:
        # print(event, values)
        if event in (sg.WIN_CLOSED, "Cancel"):
            available_recipe_window.close()
            return None

        if event == "Okay":
            if not values["selected_meal"]:
                continue
            available_recipe_window.close()
            return values["selected_meal"][0].lower()


def matchingKeys(dictionary, searchString):
    return [
        key
        for key, val in dictionary.items()
        if searchString.lower() in key.lower()
        or any(
            searchString.lower() in s["ingredient"].lower()
            for s in val["ingredients"].values()
        )
        or searchString.lower() in val["recipe_category"]
    ]


def make_layout(meals):
    if not meals:
        available_meals = read_all_recipes(db_file)
        meals = [capwords(meal) for meal, recipe in available_meals.items() if recipe]
        meals = sorted(meals)

    top_bar = [
        sg.Frame(
            "",
            layout=[
                [
                    sg.Column(
                        [
                            [
                                sg.Button("New", key="new_recipe", enable_events=True),
                                sg.Button(
                                    "Import Recipe",
                                    key="import_recipe",
                                    enable_events=True,
                                ),
                                sg.Button(
                                    "Export Recipe",
                                    key="export_recipe",
                                    visible=False,
                                    enable_events=True,
                                ),
                            ]
                        ],
                        element_justification="l",
                        expand_x=True,
                    ),
                    sg.Text("Search: "),
                    sg.Input(
                        key="-RFILTER-",
                        font=("Arial", 14),
                        enable_events=True,
                        expand_x=True,
                    ),
                    sg.Column(
                        [
                            [
                                sg.Button(
                                    "Clear", key="clear_recipe", enable_events=True
                                ),
                                sg.Button(
                                    "Close", key="close_window", enable_events=True
                                ),
                            ]
                        ],
                        element_justification="r",
                        expand_x=True,
                    ),
                ]
            ],
            element_justification="c",
            expand_x=True,
        )
    ]
    recipe_right_click_menu = [
        "&Right",
        ["Delete Recipe"],
    ]
    available_recipes = [
        [
            sg.Frame(
                "Available Recipes",
                [
                    [
                        sg.Text(
                            "Available Recipes",
                            font=("Arial Bold", 18),
                            justification="c",
                        )
                    ],
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
                [
                    sg.Text(
                        "",
                        font=("Arial Italic", 12),
                        justification="l",
                        key="subtitle",
                    )
                ],
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
                        layout=[
                            [
                                sg.Text(
                                    "",
                                    font=("Arial Bold", 12),
                                    justification="l",
                                )
                            ]
                        ],
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
                [
                    sg.Text(
                        "",
                        font=("Arial", 12),
                        justification="l",
                        key="instructions",
                    )
                ],
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
    return layout


def recipe_viewer(meals=None, settings=settings, file_path=file_path):

    layout = make_layout(meals)

    icon_file = f"{wd}/resources/burger-10956.png"
    sg.set_options(icon=base64.b64encode(open(str(icon_file), "rb").read()))
    recipe_window = sg.Window(
        "Recipe Interface",
        layout=layout,
        resizable=True,
        size=(900, 600),
        finalize=True,
    )
    meals = dict(read_all_meals(db_file).items())
    available_meals = read_all_recipes(db_file)
    while True:
        event, values = recipe_window.read()
        if event in (sg.WIN_CLOSED, "close_window"):
            recipe_window.close()
            break

        # if event:
        # DEBUG to print out the events and values
        # print(event, values)
        if event == "-RFILTER-":
            # Typing in the search box will filter the main meal list based on the name of the meal
            # as well as ingredients in any meal
            meals = {
                json.loads(recipe)["title"]: json.loads(recipe)
                for recipe in available_meals.values()
                if recipe
            }
            filtered_meals = sorted(
                [capwords(meal) for meal in matchingKeys(meals, values["-RFILTER-"])]
            )
            recipe_window["available_meals"].update(values=sorted(filtered_meals))

        if event == "export_recipe":
            file_path = os.path.join(wd, "settings.json")
            settings = json.load(open(file_path, "r"))

            selected_meal = values["available_meals"][0].lower()
            available_meals = read_all_recipes(db_file)
            meals = [
                capwords(meal) for meal, recipe in available_meals.items() if recipe
            ]
            recipe = json.loads(available_meals[selected_meal])
            settings = json.load(open(file_path, "r"))
            export_plan_path = settings["export_plan_path"]

            if not export_plan_path:
                export_recipe_path = sg.popup_get_folder(
                    "Export Recipe", title="Export Recipe"
                )
                settings["export_recipe_path"] = export_recipe_path
                with open(file_path, "w") as fp:
                    json.dump(settings, fp, sort_keys=True, indent=4)

            if not export_recipe_path:
                continue

            if recipe["title"] not in export_recipe_path:
                export_recipe_path = f"{export_recipe_path}/" + f"{recipe['title']}.rcp"

            with open(export_recipe_path, "w") as fp:
                json.dump(recipe, fp, indent=4, sort_keys=True)
                sg.popup_ok(f"Saved to {export_recipe_path}")

        if event == "import_recipe":
            import_files_path = sg.popup_get_file(
                "Import Recipe",
                title="Import Recipe",
                default_extension="rcp",
                multiple_files=True,
                file_types=(".rcp"),
            )
            if not import_files_path:
                continue

            import_files_path = import_files_path.split(";")

            for file in import_files_path:
                if not file.endswith(".rcp"):
                    sg.popup_ok(
                        "Not a valid Recipe file", title="ERROR", font=("Arial", 14)
                    )
                    continue

                if not os.path.isfile(file):
                    sg.popup_ok(
                        "File does not exist!", title="ERROR", font=("Arial", 14)
                    )
                    continue

                with open(file, "r") as fp:
                    recipe = json.load(fp)

                if not recipe:
                    continue

                basic_ingredients = [
                    ingredient["ingredient"]
                    for ingredient in recipe["ingredients"].values()
                    if ingredient
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
                    meals = dict(read_all_meals(db_file).items())
                available_meals = [
                    capwords(meal_name) for meal_name in read_all_recipes(db_file)
                ]
                recipe_window["available_meals"].update(values=sorted(available_meals))

        if event == "Delete Recipe":
            selected_meal = values["available_meals"][0].lower()
            remove_meal(db_file, selected_meal)
            available_meals = read_all_recipes(db_file)
            recipe_window["available_meals"].update(values=available_meals)

        if event == "new_recipe":
            recipe = recipes()
            if not recipe:
                continue
            basic_ingredients = [
                ingredient["ingredient"]
                for ingredient in recipe["ingredients"].values()
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
                meals = dict(read_all_meals(db_file).items())
            available_meals = [
                capwords(meal_name) for meal_name in read_all_recipes(db_file)
            ]
            recipe_window["available_meals"].update(values=sorted(available_meals))

        if event in ("available_meals"):

            if not values["available_meals"]:
                continue

            selected_meal = values["available_meals"][0].lower()
            recipe_window["export_recipe"].update(visible=True)
            available_meals = read_all_recipes(db_file)
            meals = [
                capwords(meal) for meal, recipe in available_meals.items() if recipe
            ]
            recipe = json.loads(available_meals[selected_meal])
            if not recipe:
                continue

            ingredients = [
                re.sub(
                    "\s+",
                    " ",
                    " ".join(
                        [
                            ing["quantity"] or "",
                            ing["units"] or "",
                            "".join(
                                [
                                    ing["ingredient"] or "",
                                    (
                                        (", " + ing["special_instruction"])
                                        if ing["special_instruction"]
                                        else ""
                                    ),
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
            left_ingredients = [
                "- " + "\n".join(textwrap.wrap(i[0], 40)) for i in ingredients if i[0]
            ]
            right_ingredients = [
                "- " + "\n".join(textwrap.wrap(i[1], 40)) for i in ingredients if i[1]
            ]

            recipe_window["title_frame"].update(visible=True)
            recipe_window["title"].update(value=recipe["title"])
            recipe_window["subtitle"].update(value="")
            if recipe["subtitle"]:
                recipe_window["subtitle"].update(value=recipe["subtitle"])

            recipe_window["ingredients_frame"].update(visible=True)
            recipe_window["left_ingredients"].update(value="\n".join(left_ingredients))
            recipe_window["right_ingredients"].update(
                value="\n".join(right_ingredients)
            )

            recipe_window["instructions_frame"].update(visible=True)
            recipe_window["instructions"].update(
                value="\n".join(textwrap.wrap(recipe["directions"], 80))
            )
            recipe_window.refresh()

        if event == "clear_recipe":
            recipe_window["export_recipe"].update(visible=False)
            clear_all_elements(recipe_window)


if __name__ == "__main__":
    sg.theme("Reddit")
    recipe_viewer()
