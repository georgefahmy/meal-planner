import sqlite3
import json

settings = json.load(open("settings.json", "r"))
db_file = settings["database_file"]


def create_connection(db_file=db_file):
    """create a database connection to the SQLite database
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


def add_meal(meal, ingredients=None, recipe_link=None):
    conn = create_connection()
    """
    Create a new category in the Categories table
    :param conn:
    :param kwargs:
    :return id:
    """
    values = (meal, ingredients, recipe_link)
    sql = f""" INSERT INTO meals (meal, ingredients, recipe_link) VALUES(?,?,?)"""
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    conn.close()
    return


def read_all_meals():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT meal, ingredients FROM meals")
    all_meals = cur.fetchall()
    meals = {}
    for meal in all_meals:
        meals[meal[0]] = meal[1]
    conn.close()
    return meals


def add_plan(date, meal_plan, ingredients):
    conn = create_connection()
    """
    Create a new category in the Categories table
    :param conn:
    :param kwargs:
    :return id:
    """
    values = (date, meal_plan, ingredients)
    sql = f"""INSERT OR IGNORE INTO plans (week_date, meals, ingredients) VALUES(?,?,?)"""
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    conn.close()
    return


def read_all_plans():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT week_date, meals, ingredients FROM plans")
    all_plans = cur.fetchall()
    plans = {}
    for plan in all_plans:
        date = plan[0]
        meals = {day.split(": ")[0]: day.split(": ")[1] for day in plan[1].split(", ")}
        meals["ingredients"] = plan[2].split(", ")
        plans[date] = meals
    conn.close()
    return plans
