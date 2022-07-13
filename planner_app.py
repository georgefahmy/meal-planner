import PySimpleGUI as sg
import os
import datetime
import textwrap

from utils.sql_functions import (
    add_meal,
    read_all_meals,
    add_plan,
    read_all_plans,
    create_connection,
)

table_data = [
    ["Monday", ""],
    ["Tuesday", ""],
    ["Wednesday", ""],
    ["Thursday", ""],
    ["Friday", ""],
]

# --------------------------------- Define Layout ---------------------------------

# ---------------------------MAIN LEFT COLUMN---------------------------
# Top left quadrant - three columns, list of meals, selection checkboxes, submit or cancel
left_column = [
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
            values=sorted([meal.title() for meal in read_all_meals().keys()]),
            size=(20, 10),
            font=("Arial"),
            key="-MEAL_LIST-",
            enable_events=True,
            auto_size_text=True,
        )
    ],
    [
        sg.Column(
            [
                [
                    sg.Button("Add to Plan", visible=True, key="-ADD_TO_PLAN-", enable_events=True),
                    sg.Button("Cancel", visible=True, key="-CANCEL-", enable_events=True),
                ]
            ]
        )
    ],
]

middle_column = [
    sg.Column(
        [
            [
                sg.Text("Search"),
                sg.Input("Filter", size=(10, 1), key="-FILTER-", enable_events=True),
            ],
            [sg.Checkbox("Mon", default=False, key="-MON-", enable_events=False)],
            [sg.Checkbox("Tue", default=False, key="-TUE-", enable_events=False)],
            [sg.Checkbox("Wed", default=False, key="-WED-", enable_events=False)],
            [sg.Checkbox("Thu", default=False, key="-THU-", enable_events=False)],
            [sg.Checkbox("Fri", default=False, key="-FRI-", enable_events=False)],
        ]
    )
]

right_column = [
    [sg.Text("Ingredients", font=("Arial", 14), size=(20, 1), justification="l", expand_x=True,)],
    [
        sg.Listbox(
            values=[],
            size=(16, 10),
            font=("Arial"),
            key="-MEAL_INGREDIENTS_LIST-",
            auto_size_text=True,
            enable_events=False,
            select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
        )
    ],
]

item_selection_section = [
    sg.Column(left_column, element_justification="c", pad=((0, 0), (0, 0))),
    sg.Column([middle_column], element_justification="l", pad=((0, 0), (0, 0))),
    sg.Column(right_column, element_justification="c", pad=((0, 0), (0, 0))),
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
            [sg.Input(size=(20, 2), font=("Arial", 12), key="-MEAL-", enable_events=False)],
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
            [sg.In(size=(20, 2), font=("Arial", 12), key="-INGREDIENTS-", enable_events=False)],
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
            [sg.In(size=(20, 2), font=("Arial", 12), key="-RECIPE-", enable_events=False)],
        ],
        element_justification="c",
    ),
]

input_section_buttons = [
    sg.Column(
        [
            [
                sg.Button("Add to Database", visible=True, key="-MEAL_SUBMIT-", enable_events=True),
                sg.Button("Clear", visible=True, key="-MEAL-CLEAR-", enable_events=True),
            ]
        ],
        element_justification="c",
    )
]

main_left_column = [
    sg.Column(
        [
            item_selection_section,
            [sg.Text("_" * 300, size=(400, 1), expand_x=True)],
            input_text,
            input_section,
            input_section_buttons,
        ]
    )
]

# ---------------------------MAIN RIGHT COLUMN---------------------------
# Top right quadrant - Meal Plan - Date, Meal Name, Link (if any)

meal_plan_section = [
    sg.Column(
        [
            [
                sg.Text(
                    "Week's Plan",
                    size=(36, 1),
                    font=("Arial", 18),
                    justification="c",
                    key="-WEEK-",
                    expand_x=True,
                ),
                sg.Button("Available Plans", key="-AVAILABLE_PLANS-",),
            ],
            [
                sg.Table(
                    values=table_data,
                    display_row_numbers=False,
                    justification="l",
                    num_rows=5,
                    headings=["Day", "Meal"],
                    font=("Arial", 13),
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
                sg.Button("Cancel", visible=True, key="-PLAN-CLEAR-", enable_events=True),
            ]
        ],
        element_justification="c",
    )
]

# Bottom Right Quadrant - Table of ingredients
ingredients_list_section = [
    sg.Column(
        [
            [sg.HorizontalSeparator()],
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
                    values=[],
                    font=("Arial", 12),
                    size=(40, 20),
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
        [meal_plan_section, plan_section_buttons, ingredients_list_section],
        element_justification="c",
    )
]

# ----- Full layout -----
full_layout = [
    [
        [sg.Text("Meal Planner PRO", font=("Arial", 20), justification="center", expand_x=True,)],
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
        or any(searchString.lower() in s.lower() for s in val)
    ]


# --------------------------------- Create the Window ---------------------------------
# Use the full layout to create the window object
window = sg.Window("Meal Planner PRO", full_layout, resizable=True, size=(1200, 650), finalize=True)


# Get meal and ingredient information from the database
meals = {meal: ingredients.split(", ") for meal, ingredients in read_all_meals().items()}

today = datetime.date.today()
start = today - datetime.timedelta(days=today.weekday())
week_date = f"Week of {str(start)}"
window["-WEEK-"].update(value=week_date)
plan_ingredients = None

# Start the window loop
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        # if the close button is pressed, stop the loop
        full_layout = []
        break

    if event:
        # DEBUG to print out the events and values
        print(event, values)

    if event == "-FILTER-":
        # Typing in the search box will filter the main meal list based on the name of the meal
        # as well as ingredients in any meal
        filtered_meals = sorted([meal.title() for meal in matchingKeys(meals, values["-FILTER-"])])
        window["-MEAL_LIST-"].update(filtered_meals)

    if event == "-MEAL_LIST-":
        # Choosing an item from the list of meals will update the ingredients list for that meal
        selected_meal = values["-MEAL_LIST-"][0].lower()
        ingredients_list = meals[selected_meal]
        window["-MEAL_INGREDIENTS_LIST-"].update(
            [ingredient.title() for ingredient in ingredients_list]
        )

    if event == "-CANCEL-":
        # Meal selection Cancel, clear out all the values for the checkboxes and meal list and
        # ingredients for that selected meal
        window["-MON-"].update(value=False)
        window["-TUE-"].update(value=False)
        window["-WED-"].update(value=False)
        window["-THU-"].update(value=False)
        window["-FRI-"].update(value=False)
        window["-FILTER-"].update(value="")
        window["-MEAL_LIST-"].update(sorted([meal.title() for meal in meals.keys()]))
        window["-MEAL_INGREDIENTS_LIST-"].update([])

    if event == "-MEAL-CLEAR-":
        # Clear the new meal submission boxes
        window["-MEAL-"].update(value="")
        window["-INGREDIENTS-"].update(value="")
        window["-RECIPE-"].update(value="")

    if event == "-MEAL_SUBMIT-":
        # Submit a new meal and the ingredients and recipe (if available) then add the meal to
        # the database
        new_meal = values["-MEAL-"].lower()
        new_ingredients = values["-INGREDIENTS-"].lower()
        new_recipe = values["-RECIPE-"].lower()
        if new_meal:
            add_meal(new_meal, ingredients=new_ingredients, recipe_link=new_recipe)
            meals = {
                meal: ingredients.split(", ") for meal, ingredients in read_all_meals().items()
            }
            window["-MEAL_LIST-"].update(sorted([meal.title() for meal in meals.keys()]))
            window["-MEAL-"].update(value="")
            window["-INGREDIENTS-"].update(value="")
            window["-RECIPE-"].update(value="")
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
        window["-TABLE-"].update(table_data)
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
        }
        day_index = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
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
            set(", ".join([day[1].lower() for day in table_data if day[1]]).split(", "))
        )
        plan_ingredients = sorted(
            list(
                set(", ".join([", ".join(meals[meal]) for meal in plan_meals]).title().split(", "))
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

    if event == "-PLAN-SUBMIT-":
        plan = ", ".join([": ".join(day) for day in table_data])
        if plan_ingredients:
            plan_ingredients = ", ".join(plan_ingredients)

            add_plan(week_date, plan, plan_ingredients)
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
        plans = read_all_plans()
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
            "Previous Meal Plans",
            [
                [sg.Text("Previous Meal Plans", font=("Arial", 16), justification="c")],
                [sg.Text(f"{plan_text}\n", font=("Arial", 12))],
                [sg.Button("Okay")],
            ],
            disable_close=False,
            size=(200, 200),
        ).read(close=True)
