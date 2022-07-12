import sqlite3 as s

create_meals_table = """
    CREATE TABLE IF NOT EXISTS meals
    (
        id integer PRIMARY KEY,
        meal text NOT NULL,
        ingredients text,
        recipe_link text
    );
"""

create_plan_table = """
    CREATE TABLE IF NOT EXISTS plans
    (
        id integer PRIMARY KEY,
        week_date text NOT NULL UNIQUE,
        meals text NOT NULL,
        ingredients text
    );
"""

conn = s.connect("meals_database.db")
c = conn.cursor()

if conn:
    c.execute(create_meals_table)
    c.execute(create_plan_table)
    conn.commit()
else:
    print("Error")
