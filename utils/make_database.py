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
        week_date text NOT NULL,
        meals list NOT NULL
    );
"""

conn = s.connect("meals_database.db")
c = database_conn.cursor()

if conn:
    c.execute(create_categories_table)
    c.execute(create_meals_table)
    c.execute(create_ingredients_table)
    c.execute(create_plan_table)
    conn.commit()
else:
    print("Error")
