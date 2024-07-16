import base64
import json
import os
import re
import sys
from string import capwords

import PySimpleGUI as sg

from utils.recipe_units import units
from utils.sql_functions import file_path, read_all_meals

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
settings["meal_categories"] = meal_categories
with open(file_path, "w") as fp:
    json.dump(settings, fp, sort_keys=True, indent=4)


font = ("Arial", 16)

# ______RECIPE LAYOUT_______


def new_ingredient(i):
    return [
        [
            sg.Input(font=font, key=("ingredient", i), expand_x=True, focus=True),
            sg.Button(
                "X",
                font=("Arial Bold", 14),
                key=("remove_ingredient", i),
                enable_events=True,
            ),
        ],
    ]


def clear_all_elements(window):
    for element in window.element_list():
        if type(element) in (sg.InputText, sg.Multiline) and window[element.Key].get():
            window[element.Key].update("")
    return window


def recipes(meal_title=None, recipe_data=None):
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
                    sg.Input(
                        default_text=meal_title,
                        font=font,
                        key="recipe_title",
                        expand_x=True,
                        pad=((5, 5), (5, 5)),
                    ),
                ],
                [
                    sg.Text(
                        "Subtitle (optional)",
                        font=font,
                        size=(16, 1),
                        pad=((5, 5), (5, 5)),
                    ),
                    sg.Input(
                        font=font,
                        key="recipe_subtitle",
                        expand_x=True,
                        pad=((5, 5), (5, 5)),
                    ),
                ],
                [
                    sg.Text("Category", font=font, size=(16, 1), pad=((5, 5), (5, 5))),
                    sg.Combo(
                        values=meal_categories[1:],
                        font=font,
                        key="recipe_category",
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
                                sg.Button(
                                    "(i) Tips", key="tips_button", enable_events=True
                                ),
                            ],
                            [
                                sg.Input(
                                    font=font, key=("ingredient", 0), expand_x=True
                                ),
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
                [
                    sg.Multiline(
                        font=font, key="directions", expand_x=True, size=(30, 5)
                    )
                ],
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
    # Use the full layout to create the window object
    icon_file = f"{wd}/resources/burger-10956.png"
    sg.set_options(icon=base64.b64encode(open(str(icon_file), "rb").read()))
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
        for detailed_unit in unit:
            fixed_unit = []
            for character in detailed_unit:
                if character == ".":
                    character = f"\{character}"
                fixed_unit.append(character)
            fixed_units.append("".join(fixed_unit))

    fixed_units.reverse()
    unit_expression = "|".join(fixed_units)
    match_expression = (
        f"([0-9\/\.\-\s]*)?\s?({unit_expression})?\s*?([a-zA-Z0-9\s\-\.]*),?\s?(.*)?"
    )

    i = 1
    if recipe_data:
        if recipe_data["recipe_category"]:
            recipe_window["recipe_category"].update(
                value=recipe_data["recipe_category"]
            )

        if recipe_data["directions"]:
            recipe_window["directions"].update(value=recipe_data["directions"])

        if recipe_data["subtitle"]:
            recipe_window["recipe_subtitle"].update(value=recipe_data["subtitle"])

        if recipe_data["ingredients"]:
            for i, ingredient_dict in enumerate(recipe_data["ingredients"].values()):
                quantity = ingredient_dict["quantity"]
                ing_units = ingredient_dict["units"]
                ingredient_name = ingredient_dict["ingredient"]
                special_instruction = ingredient_dict["special_instruction"]
                ingredient = (
                    (f"{quantity} " if quantity else "")
                    + (f"{str(ing_units)} " if ing_units else "")
                    + capwords(ingredient_name)
                    + (f", {special_instruction}" if special_instruction else "")
                )
                recipe_window[("ingredient", i)].update(value=ingredient)
                recipe_window.extend_layout(
                    recipe_window[("ingredient_frame", 0)],
                    new_ingredient(i + 1),
                )
        recipe_window.refresh()
        recipe_window["column"].contents_changed()

    while True:
        event, values = recipe_window.read()
        if event == sg.WIN_CLOSED:
            break

        if event == "tips_button":
            sg.Window(
                "Recipe Tips",
                [
                    [
                        sg.Text(
                            "Tips and Tricks",
                            font=("Arial Bold", 14),
                            justification="c",
                        )
                    ],
                    [
                        sg.Column(
                            [
                                [
                                    sg.Text(
                                        tip_text,
                                        font=font,
                                        justification="l",
                                    )
                                ]
                            ],
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
                    recipe_window[("ingredient_frame", 0)],
                    new_ingredient(i),
                )
                recipe_window.refresh()
                recipe_window["column"].contents_changed()
                i += 1

        if "remove_ingredient" in event:
            icon_file = f"{wd}/resources/burger-10956.png"
            sg.set_options(icon=base64.b64encode(open(str(icon_file), "rb").read()))
            row = recipe_window.FindElementWithFocus().Key
            recipe_window[event].Widget.destroy()
            recipe_window[event].Widget.master.pack_forget()
            recipe_window[("ingredient", row[-1])].update(value="")
            recipe_window[("ingredient", row[-1])].Widget.destroy()
            recipe_window[("ingredient", row[-1])].Widget.master.pack_forget()
            recipe_window.refresh()
            recipe_window["column"].contents_changed()

        if event == "save_recipe":
            return return_window(recipe_window, match_expression)

        if event == "clear_recipe":
            icon_file = wd + "/resources/burger-10956.png"
            sg.set_options(icon=base64.b64encode(open(str(icon_file), "rb").read()))
            confirm = sg.popup_ok_cancel(
                "Are you sure you want to clear?",
                icon=base64.b64encode(open(str(icon_file), "rb").read()),
            )
            if confirm != "OK":
                continue
            clear_all_elements(recipe_window)


# TODO Rename this here and in `recipes`
def return_window(recipe_window, match_expression):
    icon_file = f"{wd}/resources/burger-10956.png"
    sg.set_options(icon=base64.b64encode(open(str(icon_file), "rb").read()))
    raw_ingredients = []
    recipe = {"ingredients": {}}
    for element in recipe_window.element_list():
        if element is sg.InputText:
            if "ingredient" in element.Key and recipe_window[element.Key].get():
                raw_ingredients.append(recipe_window[element.Key].get())

            if "recipe_title" in element.key:
                recipe["title"] = recipe_window[element.Key].get()

            if "recipe_subtitle" in element.key:
                recipe["subtitle"] = recipe_window[element.Key].get()

        if element is sg.Combo and "recipe_category" in element.key:
            recipe["recipe_category"] = recipe_window[element.Key].get()

        if element is sg.Multiline and "directions" in element.Key:
            directions = (
                recipe_window["directions"].get()
                if recipe_window[element.Key].get()
                else ""
            )
    if not raw_ingredients:
        raw_ingredients = [recipe["title"]]

    for j, raw_ingredient in enumerate(raw_ingredients):
        recipe["ingredients"][f"ingredient_{j}"] = {"raw_ingredient": raw_ingredient}
        parsed_ingredient = list(
            re.match(match_expression, raw_ingredient, flags=re.IGNORECASE).groups()
        )

        for i, val in enumerate(parsed_ingredient):
            if val:
                parsed_ingredient[i] = val.strip()

        parsed_ingredient = tuple(parsed_ingredient)
        (
            recipe["ingredients"][f"ingredient_{j}"]["quantity"],
            recipe["ingredients"][f"ingredient_{j}"]["units"],
            recipe["ingredients"][f"ingredient_{j}"]["ingredient"],
            recipe["ingredients"][f"ingredient_{j}"]["special_instruction"],
        ) = parsed_ingredient

    recipe["directions"] = directions
    recipe_window.close()
    return recipe
