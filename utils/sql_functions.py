import json
import os
import sqlite3
import sys
from collections import OrderedDict
from string import capwords

try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()

file_path = os.path.join(wd, "settings.json")

settings = json.load(open(file_path, "r"))
db_file = os.path.join(wd, "database.db")


def create_connection(db_file=db_file):
    """
    create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)
    return conn


def add_meal(
    db_file, meal, ingredients=None, recipe_link=None, recipe=None, category=None
):
    conn = create_connection(db_file)
    """
    Create a new category in the Categories table
    :param conn:
    :param kwargs:
    :return id:
    """
    values = (meal, ingredients, recipe_link, recipe, category)
    sql = """
        INSERT OR IGNORE INTO meals (meal, ingredients, recipe_link, recipe_data, category)
        VALUES(?,?,?,?,?)
        """
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    conn.close()
    return


def read_all_meals(db_file):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute(
        "SELECT meal, ingredients, recipe_link, recipe_data, category FROM meals"
    )
    all_meals = cur.fetchall()
    meals = {}
    for meal in all_meals:
        meals[meal[0]] = {
            "ingredients": meal[1].split(", "),
            "recipe_link": meal[2],
            "recipe_data": meal[3],
            "category": meal[4],
        }
    conn.close()
    return meals


def read_specific_meals(db_file, selected_meal):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute(
        "SELECT meal, ingredients FROM meals WHERE meal LIKE ? ", (selected_meal,)
    )
    raw_meal = cur.fetchall()[0]
    meal = {}
    meal[raw_meal[0]] = raw_meal[1].split(", ")
    conn.close()
    return meal


def update_meal_name(db_file, new_meal_name, selected_meal):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute(
        "UPDATE meals SET meal = ? WHERE meal LIKE ?", (new_meal_name, selected_meal)
    )
    conn.commit()
    conn.close()
    return


def update_meal_recipe(db_file, recipe_data, selected_meal):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute(
        "UPDATE meals SET recipe_data = ? WHERE meal LIKE ? ",
        (recipe_data, selected_meal),
    )
    conn.commit()
    conn.close()
    return


def read_meal_recipe(db_file, selected_meal):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute("SELECT recipe_data FROM meals WHERE meal LIKE ?", (selected_meal,))
    recipe = cur.fetchone()
    if recipe:
        try:
            recipe = json.loads(recipe[0]) if recipe else None
        except:
            recipe = None
    conn.commit()
    conn.close()
    return recipe


def read_all_recipes(db_file):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute("SELECT meal, recipe_data FROM meals WHERE LENGTH(recipe_data) > 10")
    meals = cur.fetchall()
    available_meals = {}
    for meal in meals:
        available_meals[meal[0]] = meal[1]
    conn.close()
    return available_meals


def update_meal_category(db_file, new_category, selected_meal):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute(
        "UPDATE meals SET category = ? WHERE meal LIKE ? ",
        (new_category, selected_meal),
    )
    conn.commit()
    conn.close()
    return


def update_meal_ingredients(db_file, meal_name, ingredients):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute(
        "UPDATE meals SET ingredients = ? WHERE meal LIKE ? ", (ingredients, meal_name)
    )
    conn.commit()
    conn.close()
    return


def remove_meal(db_file, meal_name):
    conn = create_connection(db_file)
    cur = conn.cursor()
    print(meal_name)
    cur.execute("DELETE FROM meals WHERE meal LIKE ? ", (meal_name,))
    conn.commit()
    conn.close()
    return


def add_plan(db_file, plan, overwrite=False):
    conn = create_connection(db_file)
    cur = conn.cursor()

    """
    Create a new category in the Categories table
    :param conn:
    :param kwargs:
    :return id:
    """

    def join_list(in_list):
        return ", ".join(in_list)

    if overwrite:
        sql = """
        UPDATE plans SET
        monday = ?, tuesday = ?, wednesday = ?, thursday = ?, friday = ?, saturday = ?, sunday = ?,
        ingredients = ?
        WHERE week_date LIKE ?
        """

        cur.execute(
            sql,
            (
                join_list(plan["meals"]["Monday"]),
                join_list(plan["meals"]["Tuesday"]),
                join_list(plan["meals"]["Wednesday"]),
                join_list(plan["meals"]["Thursday"]),
                join_list(plan["meals"]["Friday"]),
                join_list(plan["meals"]["Saturday"]),
                join_list(plan["meals"]["Sunday"]),
                plan["ingredients"],
                plan["date"],
            ),
        )

    else:
        sql = """
        INSERT OR IGNORE INTO plans
        (week_date, sunday, monday, tuesday, wednesday, thursday, friday, saturday, ingredients)
        VALUES(?,?,?,?,?,?,?,?,?)
        """

        cur.execute(
            sql,
            (
                plan["date"],
                join_list(plan["meals"]["Sunday"]),
                join_list(plan["meals"]["Monday"]),
                join_list(plan["meals"]["Tuesday"]),
                join_list(plan["meals"]["Wednesday"]),
                join_list(plan["meals"]["Thursday"]),
                join_list(plan["meals"]["Friday"]),
                join_list(plan["meals"]["Saturday"]),
                plan["ingredients"],
            ),
        )

    conn.commit()
    conn.close()
    return


def read_all_plans(db_file):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute(
        """SELECT
        week_date, monday, tuesday, wednesday, thursday, friday, saturday, sunday, ingredients
        FROM plans"""
    )
    all_plans = cur.fetchall()
    days_of_week = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    plans = {}
    for raw_plan in all_plans:
        plan = {}
        plan["date"] = raw_plan[0]
        plan["meals"] = OrderedDict()
        for i, meal in enumerate(list(raw_plan[1:-1])):

            plan["meals"][capwords(days_of_week[i])] = [
                capwords(meal)
                for meal in meal.split(", ")
                if meal.lower() in read_all_meals(db_file).keys()
            ]
        plan["ingredients"] = raw_plan[-1]
        plans[plan["date"]] = plan
    conn.close()
    return plans


def read_current_plans(db_file, week_date):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute(
        """SELECT
        week_date, monday, tuesday, wednesday, thursday, friday, saturday, sunday, ingredients
        FROM plans WHERE week_date LIKE ? """,
        (week_date,),
    )
    current_plan = cur.fetchall()
    if not current_plan:
        return False
    else:
        current_plan = current_plan[0]
        days_of_week = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        plan = {}
        plan["date"] = current_plan[0]
        plan["meals"] = {}
        for i, meal in enumerate(list(current_plan[1:-1])):
            plan["meals"][capwords(days_of_week[i])] = [
                capwords(meal)
                for meal in meal.split(", ")
                if meal.lower() in read_all_meals(db_file).keys()
            ]
        plan["ingredients"] = current_plan[-1]
    conn.close()
    return plan


def remove_plan(db_file, plan_date):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute("DELETE FROM plans WHERE week_date LIKE ? ", (plan_date,))
    conn.commit()
    conn.close()
    return True
