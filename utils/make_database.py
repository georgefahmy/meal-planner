import sqlite3 as s
import json
import os
import sys

try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()

file_path = os.path.join(wd, "settings.json")

settings = json.load(open(file_path, "r"))
db_file = os.path.join(wd, "databse.db")


def make_database(db_file=db_file):
    create_meals_table = """
        CREATE TABLE IF NOT EXISTS meals
        (
            id integer PRIMARY KEY,
            meal text NOT NULL,
            ingredients text,
            recipe_link text,
            category text
        );
    """

    create_plan_table = """
        CREATE TABLE IF NOT EXISTS plans
        (
            id integer PRIMARY KEY,
            week_date text NOT NULL UNIQUE,
            sunday text,
            monday text,
            tuesday text,
            wednesday text,
            thursday text,
            friday text,
            saturday text,
            ingredients text
        );
    """

    conn = s.connect(db_file)
    c = conn.cursor()

    if conn:
        c.execute(create_meals_table)
        c.execute(create_plan_table)
        conn.commit()
    else:
        print("Error")
