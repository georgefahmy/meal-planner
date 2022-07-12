import PySimpleGUI as sg
import os
import datetime

from utils.sql_functions import add_meal, read_all_meals, search_meals, create_connection

# --------------------------------- Define Layout ---------------------------------
# Top left quadrant - three columns, list of meals, selection checkboxes, submit or cancel
left_col = [
    [
        sg.Text(
            "Meal Selection",
            font=("Ariel", 18),
            size=(20, 1),
            justification="center",
            expand_x=True,
        )
    ],
    [
        sg.Listbox(
            values=[meal.capitalize() for meal in read_all_meals().keys()],
            size=(20, 10),
            font=("Ariel"),
            key="-MEAL LIST-",
            enable_events=True,
            auto_size_text=True,
        )
    ],
    [
        sg.Column(
            [
                [
                    sg.Button("Submit", visible=True, key="-SUBMIT-", enable_events=True),
                    sg.Button("Cancel", visible=True, key="-CANCEL-", enable_events=True),
                ]
            ]
        )
    ],
]

right_column = [
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

item_selection_section = [
    sg.Column(left_col, element_justification="c"),
    sg.Column([right_column], element_justification="l"),
]

# Bottom left quadrant - New meal submission - meal, ingredients, links, submit, clear
input_text = [
    sg.Text("New Meal", font=("Ariel", 18), size=(20, 1), justification="c", expand_x=True),
]
input_section = [
    sg.Column(
        [
            [
                sg.Text(
                    "Meal",
                    font=("Helvetica", 10),
                    size=(10, 1),
                    justification="center",
                    expand_x=True,
                )
            ],
            [sg.Input(size=(10, 1), key="-MEAL-", enable_events=False)],
        ],
        element_justification="c",
    ),
    sg.Column(
        [
            [
                sg.Text(
                    "Ingredients",
                    font=("Helvetica", 10),
                    size=(10, 1),
                    justification="center",
                    expand_x=True,
                )
            ],
            [sg.Input(size=(10, 1), key="-INGREDIENTS-", enable_events=False)],
        ],
        element_justification="c",
    ),
    sg.Column(
        [
            [
                sg.Text(
                    "Recipe Link",
                    font=("Helvetica", 10),
                    size=(10, 1),
                    justification="center",
                    expand_x=True,
                )
            ],
            [sg.Input(size=(10, 1), key="-RECIPE-", enable_events=False)],
        ],
        element_justification="c",
    ),
]

input_section_buttons = [
    sg.Column(
        [
            [
                sg.Button("Submit", visible=True, key="-MEAL-SUBMIT-", enable_events=True),
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

# Top right quadrant - Meal Plan - Date, Meal Name, Link (if any)

meal_plan_section = [
    sg.Column(
        [
            [
                sg.Text(
                    "Week's Plan",
                    size=(40, 1),
                    font=("Ariel", 18),
                    justification="c",
                    expand_x=True,
                )
            ],
            [
                sg.Table(
                    values=[
                        ["Monday", ""],
                        ["Tuesday", ""],
                        ["Wednesday", ""],
                        ["Thursday", ""],
                        ["Friday", ""],
                    ],
                    display_row_numbers=False,
                    justification="l",
                    num_rows=5,
                    headings=["Day", "Meal"],
                    font=("Ariel", 16),
                    alternating_row_color="lightblue",
                    key="-TABLE-",
                    auto_size_columns=False,
                    col_widths=20,
                    selected_row_colors="lightblue on blue",
                    enable_events=True,
                    enable_click_events=False,
                    size=(40, 40),
                    hide_vertical_scroll=True,
                )
            ],
        ],
        element_justification="c",
    )
]

# Bottom Right Quadrant - Table of ingredients
ingredients_list_section = [
    sg.Column(
        [
            [
                sg.Text(
                    "This Weeks Shopping List",
                    size=(40, 1),
                    font=("Ariel", 16),
                    justification="c",
                    expand_x=True,
                )
            ],
            [
                sg.Listbox(
                    values=[],
                    font=("Ariel", 12),
                    size=(40, 20),
                    key="-INGREDIENTS LIST-",
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
    sg.Column([meal_plan_section, ingredients_list_section], element_justification="c")
]

# ----- Full layout -----
full_layout = [
    [
        [
            sg.Text(
                "Meal Planner PRO",
                size=(100, 1),
                font=("Helvetica", 20),
                justification="center",
                expand_x=True,
            )
        ],
        [sg.Text("_" * 300, size=(1000, 1), expand_x=True)],
        sg.Column([main_left_column], size=(400, 600), element_justification="c", expand_x=True),
        sg.VSeperator(),
        sg.Column([main_right_column], size=(400, 600), element_justification="c", expand_x=True),
    ]
]

window = sg.Window("Meal Planner PRO", full_layout, resizable=True, size=(1000, 600))

meals = [meal.capitalize() for meal in read_all_meals().keys()]


while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    if event:
        print(event, values)

    if event == "-FILTER-":
        filtered_meals = [meal for meal in meals if values["-FILTER-"].lower() in meal.lower()]
        window["-MEAL LIST-"].update(filtered_meals)
