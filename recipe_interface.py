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
