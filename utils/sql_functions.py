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


def add_meal(db_file, meal, ingredients=None, recipe_link=None, category="Dinner"):
    conn = create_connection(db_file)
    """
    Create a new category in the Categories table
    :param conn:
    :param kwargs:
    :return id:
    """
    values = (meal, ingredients, recipe_link, category)
    sql = f""" INSERT INTO meals (meal, ingredients, recipe_link, category) VALUES(?,?,?,?)"""
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    conn.close()
    return


def read_all_meals(db_file):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute("SELECT meal, ingredients, recipe_link, category FROM meals")
    all_meals = cur.fetchall()
    meals = {}
    for meal in all_meals:
        meals[meal[0]] = {
            "ingredients": meal[1].split(", "),
            "recipe": meal[2],
            "category": meal[3],
        }
    conn.close()
    return meals


def read_specific_meals(db_file, meal_name):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute(f"SELECT meal, ingredients FROM meals WHERE meal LIKE '{meal_name}'")
    raw_meal = cur.fetchall()[0]
    meal = {}
    meal[raw_meal[0]] = raw_meal[1].split(", ")
    conn.close()
    return meal


def update_meal_name(db_file, new_meal_name, selected_meal):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute(f"UPDATE meals SET meal = '{new_meal_name}' WHERE meal LIKE '{selected_meal}'")
    conn.commit()
    conn.close()
    return


def update_meal_ingredients(db_file, meal_name, ingredients):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute(f"UPDATE meals SET ingredients = '{ingredients}' WHERE meal LIKE '{meal_name}'")
    conn.commit()
    conn.close()
    return


def remove_meal(db_file, meal_name):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute(f"DELETE FROM meals WHERE meal LIKE '{meal_name}'")
    conn.commit()
    conn.close()
    return


def add_plan(db_file, date, meal_plan, ingredients):
    conn = create_connection(db_file)
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


def read_all_plans(db_file):
    conn = create_connection(db_file)
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


def read_current_plans(db_file, week_date):
    conn = create_connection(db_file)
    cur = conn.cursor()
    cur.execute(
        f"SELECT week_date, meals, ingredients FROM plans WHERE week_date LIKE '{week_date}'"
    )
    current_plan = cur.fetchall()
    if not current_plan:
        return
    else:
        current_plan = current_plan[0]
    plan = {}

    date = current_plan[0]
    meals = {day.split(": ")[0]: day.split(": ")[1] for day in current_plan[1].split(", ")}
    meals["ingredients"] = current_plan[2].split(", ")
    plan[date] = meals
    conn.close()
    return plan
