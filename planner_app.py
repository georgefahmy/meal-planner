from random import choice
import PySimpleGUI as sg
import datetime
import json
import textwrap
import base64

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
from utils.make_database import make_database

settings = json.load(open("settings.json", "r"))
db_file = settings["database_file"]
meal_categories = settings["meal_categories"]
make_database(db_file)
db_file_name = db_file.split("/")[-1]

today = datetime.date.today()
start = today - datetime.timedelta(days=today.weekday())
week_date = f"Week of {str(start)}"

blank_table_data = table_data = [
    ["Monday", ""],
    ["Tuesday", ""],
    ["Wednesday", ""],
    ["Thursday", ""],
    ["Friday", ""],
    ["Saturday", ""],
    ["Sunday", ""],
]

# --------------------------------- Define Layout ---------------------------------

# --------------------------------MAIN LEFT COLUMN---------------------------------
# Top left quadrant - three columns, list of meals, selection checkboxes, submit or cancel

meal_selection_rightclick_menu_def = [
    [],
    [
        "&Edit Meal",
        [
            "Change Meal Name",
            "Edit Category",
            "Edit Ingredients",
            ["Add Ingredient", "Edit Ingredients"],
            "Delete Meal",
        ],
    ],
]


left_column = [
    sg.Frame(
        "Meals",
        element_justification="c",
        layout=[
            [
                sg.Text(
                    "Meal Selection",
                    font=("Arial", 18),
                    size=(20, 1),
                    justification="center",
                    expand_x=True,
                )
            ],
            [
                sg.Listbox(
                    values=sorted([meal.title() for meal in read_all_meals(db_file).keys()]),
                    size=(20, 10),
                    font=("Arial"),
                    key="-MEAL_LIST-",
                    enable_events=True,
                    auto_size_text=True,
                    right_click_menu=meal_selection_rightclick_menu_def,
                )
            ],
            [
                sg.Column(
                    [
                        [
                            sg.Button(
                                "Add to Plan", visible=True, key="-ADD_TO_PLAN-", enable_events=True
                            ),
                            sg.Button("Cancel", visible=True, key="-CANCEL-", enable_events=True),
                        ]
                    ]
                )
            ],
        ],
    )
]

middle_column = [
    sg.Column(
        [
            [
                sg.Frame(
                    title="Filters",
                    element_justification="c",
                    layout=[
                        [
                            sg.Text("Meal Category", font=("Arial", 12),),
                            sg.Combo(
                                default_value="All",
                                values=meal_categories,
                                font=("Arial", 12),
                                size=(10, 1),
                                key="-CFILTER-",
                                enable_events=True,
                                readonly=True,
                                expand_x=True,
                            ),
                        ],
                        [
                            sg.Text("Meal Filter", key="-MFILTER_TEXT-", font=("Arial", 12),),
                            sg.Input(
                                font=("Arial", 12),
                                size=(10, 1),
                                key="-MFILTER-",
                                enable_events=True,
                                expand_x=True,
                            ),
                        ],
                    ],
                    size=(180, 100),
                    pad=(0, 0),
                )
            ],
            [sg.HorizontalSeparator(pad=22)],
            [
                sg.Frame(
                    "Day Selection",
                    element_justification="c",
                    layout=[
                        [
                            sg.Checkbox(
                                "Mon",
                                font=("Arial", 12),
                                default=False,
                                key="-MON-",
                                enable_events=False,
                                size=(6, 10),
                            ),
                            sg.Checkbox(
                                "Tue",
                                font=("Arial", 12),
                                default=False,
                                key="-TUE-",
                                enable_events=False,
                                size=(6, 10),
                            ),
                            sg.Checkbox(
                                "Wed",
                                font=("Arial", 12),
                                default=False,
                                key="-WED-",
                                enable_events=False,
                                size=(6, 10),
                            ),
                        ],
                        [
                            sg.Checkbox(
                                "Thu",
                                font=("Arial", 12),
                                default=False,
                                key="-THU-",
                                enable_events=False,
                                size=(6, 10),
                            ),
                            sg.Checkbox(
                                "Fri",
                                font=("Arial", 12),
                                default=False,
                                key="-FRI-",
                                enable_events=False,
                                size=(6, 10),
                            ),
                        ],
                        [
                            sg.Checkbox(
                                "Sat",
                                font=("Arial", 12),
                                default=False,
                                key="-SAT-",
                                enable_events=False,
                                size=(6, 10),
                            ),
                            sg.Checkbox(
                                "Sun",
                                font=("Arial", 12),
                                default=False,
                                key="-SUN-",
                                enable_events=False,
                                size=(6, 10),
                            ),
                        ],
                    ],
                    size=(180, 100),
                    pad=(0, 0),
                ),
            ],
        ]
    )
]

right_column = [
    sg.Frame(
        "Ingredients",
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
                    size=(16, 10),
                    font=("Arial", 14),
                    key="-MEAL_INGREDIENTS_LIST-",
                    auto_size_text=True,
                    enable_events=False,
                    select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                )
            ],
        ],
    )
]

item_selection_section = [
    [
        sg.Column([left_column], element_justification="c", pad=((0, 0), (0, 0))),
        sg.Column([middle_column], element_justification="c", pad=((0, 0), (0, 0))),
        sg.Column([right_column], element_justification="c", pad=((0, 0), (0, 0))),
    ]
]

# Bottom left quadrant - New meal submission - meal, ingredients, links, submit, clear
input_text = [
    sg.Text("New Meal", font=("Arial", 18), size=(50, 1), justification="c"),
]
input_section = [
    sg.Column(
        [
            [
                sg.Text(
                    "Meal", font=("Arial", 14), size=(10, 1), justification="center", expand_x=True,
                )
            ],
            [sg.Input(size=(15, 2), font=("Arial", 14), key="-MEAL-", enable_events=False)],
        ],
        element_justification="c",
    ),
    sg.Column(
        [
            [
                sg.Text(
                    "Ingredients",
                    font=("Arial", 14),
                    size=(10, 1),
                    justification="center",
                    expand_x=True,
                )
            ],
            [sg.In(size=(15, 2), font=("Arial", 14), key="-INGREDIENTS-", enable_events=False,)],
        ],
        element_justification="c",
    ),
    sg.Column(
        [
            [
                sg.Text(
                    "Recipe Link",
                    font=("Arial", 14),
                    size=(10, 1),
                    justification="center",
                    expand_x=True,
                )
            ],
            [sg.In(size=(15, 2), font=("Arial", 14), key="-RECIPE-", enable_events=False)],
        ],
        element_justification="c",
    ),
    sg.Column(
        [
            [
                sg.Text(
                    "Meal Category",
                    font=("Arial", 14),
                    size=(10, 1),
                    justification="center",
                    expand_x=True,
                )
            ],
            [
                sg.Combo(
                    default_value=meal_categories[1],
                    values=meal_categories[1:],
                    font=("Arial", 12),
                    size=(15, 1),
                    key="-NEWCATEGORY-",
                    enable_events=False,
                    readonly=True,
                    expand_x=True,
                ),
            ],
        ],
        element_justification="c",
    ),
]
advanced_section = [
    sg.Column(
        [
            [
                sg.Column(
                    [
                        [
                            sg.Text(
                                "Genre",
                                font=("Arial", 14),
                                size=(10, 1),
                                justification="center",
                                expand_x=True,
                            )
                        ],
                        [
                            sg.Input(
                                size=(15, 2), font=("Arial", 14), key="-GENRE-", enable_events=False
                            )
                        ],
                    ],
                    element_justification="c",
                ),
                sg.Column(
                    [
                        [
                            sg.Text(
                                "Serving Size",
                                font=("Arial", 14),
                                size=(10, 1),
                                justification="center",
                                expand_x=True,
                            )
                        ],
                        [
                            sg.In(
                                size=(15, 2),
                                font=("Arial", 14),
                                key="-SERVINGS-",
                                enable_events=False,
                            )
                        ],
                    ],
                    element_justification="c",
                ),
            ],
        ],
        visible=False,
        key="-ADV_SECTION-",
    ),
]

input_section_buttons = [
    sg.Column(
        [
            [
                sg.Button("Add to Database", visible=True, key="-MEAL_SUBMIT-", enable_events=True),
                sg.Button("Clear", visible=True, key="-MEAL-CLEAR-", enable_events=True),
                sg.Button("More Options", visible=False, key="-MORE-OPTIONS-", enable_events=True),
            ]
        ],
        element_justification="c",
    )
]

main_left_column = [
    sg.Column(
        [
            [
                sg.Frame(
                    "Item Selection", layout=item_selection_section, pad=(0, 0), size=(600, 300)
                )
            ],
            [sg.HorizontalSeparator()],
            [
                sg.Frame(
                    "New Meals",
                    element_justification="c",
                    layout=[input_text, input_section_buttons, input_section, advanced_section],
                    pad=(0, 0),
                    size=(600, 200),
                )
            ],
        ]
    )
]

# ---------------------------MAIN RIGHT COLUMN---------------------------
# Top right quadrant - Meal Plan - Date, Meal Name, Link (if any)

current_plan = read_current_plans(db_file, str(start))
if not current_plan:
    current_plan_table = table_data
else:
    current_plan = current_plan[str(start)]
    current_plan_table = [] if current_plan else table_data
    for day in current_plan:
        meal = current_plan[day]
        current_plan_table.append([day, meal])
    table_data = current_plan_table

meal_plan_section = [
    sg.Column(
        [
            [
                sg.Text(
                    "Week's Plan",
                    size=(36, 1),
                    font=("Arial", 18),
                    justification="l",
                    key="-WEEK-",
                    expand_x=True,
                ),
                sg.Button("Available Plans", key="-AVAILABLE_PLANS-",),
            ],
            [
                sg.Table(
                    values=current_plan_table,
                    display_row_numbers=False,
                    justification="l",
                    num_rows=7,
                    headings=["Day", "Meal"],
                    font=("Arial", 14),
                    text_color="black",
                    alternating_row_color="lightgray",
                    key="-TABLE-",
                    auto_size_columns=False,
                    col_widths=(10, 30),
                    selected_row_colors="lightblue on blue",
                    enable_events=True,
                    enable_click_events=False,
                    size=(40, 40),
                    hide_vertical_scroll=True,
                )
            ],
        ],
        element_justification="c",
    ),
]
plan_section_buttons = [
    sg.Column(
        [
            [
                sg.Button("Finalize Plan", visible=True, key="-PLAN-SUBMIT-", enable_events=True),
                sg.Button("Clear", visible=True, key="-PLAN-CLEAR-", enable_events=True),
            ]
        ],
        element_justification="c",
    )
]
# Get meal and ingredient information from the database
meals = {meal: info for meal, info in read_all_meals(db_file).items()}
plan = ", ".join([": ".join(day) for day in table_data[:-1]])
plan_meals = list(set(", ".join([day[1].lower() for day in table_data[:-1] if day[1]]).split(", ")))
plan_ingredients = sorted(
    list(
        set(
            ", ".join([", ".join(meals[meal]["ingredients"]) for meal in plan_meals if meal])
            .title()
            .split(", ")
        )
    )
)
plan_ingredients = [plan_ingredient for plan_ingredient in plan_ingredients if plan_ingredient]
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
                    size=(40, 18),
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
                    size=(600, 230),
                    pad=(0, 0),
                )
            ],
            [sg.HorizontalSeparator()],
            [
                sg.Frame(
                    "Shopping List",
                    layout=[ingredients_list_section],
                    element_justification="c",
                    size=(600, 340),
                    pad=(0, 0),
                )
            ],
        ],
        element_justification="c",
    )
]

# ----- Full layout -----
full_layout = [
    [
        [sg.Text("Meal Planner PRO", font=("Arial", 20), justification="center", expand_x=True)],
        [sg.HorizontalSeparator()],
        sg.Column([main_left_column], size=(400, 600), element_justification="c", expand_x=True),
        sg.VSeperator(),
        sg.Column([main_right_column], size=(400, 600), element_justification="c", expand_x=True),
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


# --------------------------------- Create the Window ---------------------------------
# Use the full layout to create the window object
icon_file = "/Users/GFahmy/Documents/projects/meal-planner/resources/burger-10956.png"
sg.set_options(icon=base64.b64encode(open(str(icon_file), "rb").read()))
themes = sg.theme_list()
chosen_theme = choice(themes)
sg.theme(chosen_theme)

window = sg.Window("Meal Planner PRO", full_layout, resizable=True, size=(1280, 660), finalize=True)


# Get meal and ingredient information from the database
meals = {meal: info for meal, info in read_all_meals(db_file).items()}


window["-WEEK-"].update(value=week_date)
plan_ingredients = None

# Start the window loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    if event:
        # DEBUG to print out the events and values
        print(event, values)

    # Future to expand for more options - will need to update the databse for additional columns
    if event == "-MORE-OPTIONS-":
        if window["-ADV_SECTION-"].visible:
            window["-ADV_SECTION-"].update(visible=False)
        else:
            window["-ADV_SECTION-"].update(visible=True)

    if event == "Change Meal Name":
        selected_meal = values["-MEAL_LIST-"][0].lower()
        _, new_meal_name = sg.Window(
            "Change Meal Name",
            [
                [sg.Text("Change Name of Meal", font=("Arial", 14), justification="c")],
                [
                    sg.Input(
                        default_text=selected_meal.title(),
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
        update_meal_name(db_file, new_meal_name, selected_meal)
        meals = {meal: info for meal, info in read_all_meals(db_file).items()}
        window["-MEAL_LIST-"].update(
            sorted([meal.title() for meal in read_all_meals(db_file).keys()])
        )

    if event == "Edit Category":
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
        update_meal_category(db_file, new_category, selected_meal)
        meals = {meal: info for meal, info in read_all_meals(db_file).items()}
        window["-MEAL_LIST-"].update(
            sorted([meal.title() for meal in read_all_meals(db_file).keys()])
        )

    if event == "Add Ingredient":
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
            [ingredient.title() for ingredient in ingredients_list]
        )

    if event == "Edit Ingredients":
        selected_meal = values["-MEAL_LIST-"][0].lower()
        ingredients = read_specific_meals(db_file, selected_meal)[selected_meal]
        _, edited_ingredients = sg.Window(
            "Edit Ingredients",
            [
                [sg.Text("Edit Ingredient(s)", font=("Arial", 14), justification="c",)],
                [
                    sg.Multiline(
                        default_text=", ".join(sorted(ingredients)).title(),
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
            [ingredient.title() for ingredient in ingredients_list]
        )

    if event == "Delete Meal":
        selected_meal = values["-MEAL_LIST-"][0].lower()
        confirm_delete = sg.popup_yes_no(f"Confirm delete: {selected_meal}")
        if confirm_delete == "Yes":
            remove_meal(db_file, selected_meal)
            meals = {meal: info for meal, info in read_all_meals(db_file).items()}
            window["-MEAL_LIST-"].update(
                sorted([meal.title() for meal in read_all_meals(db_file).keys()])
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
                size=(200, 100),
            ).read(close=True)

    if event == "-CFILTER-":
        if values["-CFILTER-"] == "All":
            values["-CFILTER-"] = ""
        filtered_meals = sorted([meal.title() for meal in matchingKeys(meals, values["-CFILTER-"])])
        window["-MEAL_LIST-"].update(filtered_meals)

    if event == "-MFILTER-":
        # Typing in the search box will filter the main meal list based on the name of the meal
        # as well as ingredients in any meal
        filtered_meals = sorted([meal.title() for meal in matchingKeys(meals, values["-MFILTER-"])])
        window["-MEAL_LIST-"].update(filtered_meals)

    if event == "-MEAL_LIST-":
        # Choosing an item from the list of meals will update the ingredients list for that meal
        if not values["-MEAL_LIST-"]:
            continue
        selected_meal = values["-MEAL_LIST-"][0].lower()
        ingredients_list = meals[selected_meal]["ingredients"]
        window["-MEAL_INGREDIENTS_LIST-"].update(
            sorted([ingredient.title() for ingredient in ingredients_list])
        )

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
        window["-CFILTER-"].update(value="")
        window["-MEAL_LIST-"].update(sorted([meal.title() for meal in meals.keys()]))
        window["-MEAL_INGREDIENTS_LIST-"].update([])

    if event == "-MEAL-CLEAR-":
        # Clear the new meal submission boxes
        window["-MEAL-"].update(value="")
        window["-INGREDIENTS-"].update(value="")
        window["-RECIPE-"].update(value="")
        window["-NEWCATEGORY-"].update(value="")

    if event == "-MEAL_SUBMIT-":
        # Submit a new meal and the ingredients and recipe (if available) then add the meal to
        # the database
        new_meal = values["-MEAL-"].lower()
        new_ingredients = values["-INGREDIENTS-"].lower()
        new_recipe = values["-RECIPE-"].lower()
        new_category = values["-NEWCATEGORY-"].lower()

        if not new_ingredients:
            new_ingredients = new_meal

        if new_meal:
            add_meal(
                db_file,
                new_meal,
                ingredients=new_ingredients,
                recipe_link=new_recipe,
                category=new_category,
            )
            meals = {meal: info for meal, info in read_all_meals(db_file).items()}
            window["-MEAL_LIST-"].update(sorted([meal.title() for meal in meals.keys()]))
            window["-MEAL-"].update(value="")
            window["-INGREDIENTS-"].update(value="")
            window["-RECIPE-"].update(value="")
            window["-NEWCATEGORY-"].update(value="")
        else:
            sg.Window(
                "ERROR",
                [
                    [sg.Text("No Meal Added", font=("Arial", 16), justification="c")],
                    [sg.Button("Okay")],
                ],
                disable_close=False,
                size=(150, 80),
            ).read(close=True)

    if event == "-PLAN-CLEAR-":
        # Empty out the table and return it to the default values
        for row in table_data:
            row[1] = ""
        window["-TABLE-"].update(blank_table_data)
        window["-PLAN_INGREDIENTS_LIST-"].update([])

    if event == "-ADD_TO_PLAN-":
        # Add a selected meal to a day of the week in the plan table
        selected_meal = ", ".join(values["-MEAL_LIST-"])

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
                size=(150, 80),
            ).read(close=True)
            continue
        days_of_week = {
            "Monday": values["-MON-"],
            "Tuesday": values["-TUE-"],
            "Wednesday": values["-WED-"],
            "Thursday": values["-THU-"],
            "Friday": values["-FRI-"],
            "Saturday": values["-SAT-"],
            "Sunday": values["-SUN-"],
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

            if not table_data[day_index[day]][1]:
                table_data[day_index[day]][1] = selected_meal

            elif table_data[day_index[day]][1] == selected_meal:
                continue

            else:
                table_data[day_index[day]][1] = table_data[day_index[day]][1] + ", " + selected_meal

        # Update the table information with the plan meals and get the ingredients for those meals
        # then create a unique list that is sorted and put it into the ingredients listbox
        plan_meals = list(
            set(", ".join([day[1].lower() for day in table_data[:-1] if day[1]]).split(", "))
        )
        plan_ingredients = sorted(
            list(
                set(
                    ", ".join([", ".join(meals[meal]["ingredients"]) for meal in plan_meals])
                    .title()
                    .split(", ")
                )
            )
        )
        plan_ingredients = [
            plan_ingredient for plan_ingredient in plan_ingredients if plan_ingredient
        ]

        # Update and clear the checkboxes once the meal is submitted to the plan
        window["-TABLE-"].update(values=table_data)
        window["-PLAN_INGREDIENTS_LIST-"].update(plan_ingredients)
        window["-MON-"].update(value=False)
        window["-TUE-"].update(value=False)
        window["-WED-"].update(value=False)
        window["-THU-"].update(value=False)
        window["-FRI-"].update(value=False)
        window["-SAT-"].update(value=False)
        window["-SUN-"].update(value=False)

    if event == "-PLAN-SUBMIT-":
        plan = ", ".join([": ".join(day) for day in table_data[:-1]])
        plan_meals = list(
            set(", ".join([day[1].lower() for day in table_data[:-1] if day[1]]).split(", "))
        )
        plan_ingredients = sorted(
            list(
                set(
                    ", ".join([", ".join(meals[meal]["ingredients"]) for meal in plan_meals])
                    .title()
                    .split(", ")
                )
            )
        )
        plan_ingredients = [
            plan_ingredient for plan_ingredient in plan_ingredients if plan_ingredient
        ]
        if plan_ingredients:
            plan_ingredients = ", ".join(plan_ingredients)

            add_plan(db_file, start, plan, plan_ingredients)
            okay = sg.popup_ok(
                f"Meal Plan submitted for {week_date}",
                font=("Arial", 16),
                auto_close=True,
                auto_close_duration=10,
            )
        else:
            sg.Window(
                "ERROR",
                [
                    [sg.Text("Plan is Empty", font=("Arial", 16), justification="c")],
                    [sg.Button("Okay")],
                ],
                disable_close=False,
                size=(150, 80),
            ).read(close=True)
            continue
        if okay:
            for row in table_data:
                row[1] = ""
            window["-TABLE-"].update(table_data)
            window["-PLAN_INGREDIENTS_LIST-"].update([])
            window["-MEAL_INGREDIENTS_LIST-"].update([])

    if event == "-AVAILABLE_PLANS-":
        plans = read_all_plans(db_file)
        plan_text = []
        for date, meal_options in plans.items():
            days_text = []
            for day, meal in meal_options.items():
                if day == "ingredients":
                    continue
                days_text.append(f"{day}: {meal}")
            days_text = "\n".join(days_text)
            plan_text.append(f"{date}\n\n{days_text}")
        plan_text = "\n\n".join(plan_text)
        sg.Window(
            "Available Meal Plans",
            [
                [sg.Text("Available Meal Plans", font=("Arial", 16), justification="c")],
                [sg.Text(f"{plan_text}\n", font=("Arial", 12))],
                [sg.Button("Okay")],
            ],
            disable_close=False,
        ).read(close=True)
