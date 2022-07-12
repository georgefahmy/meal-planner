import sqlite3


def create_connection(db_file="meals_database.db"):
    """ create a database connection to the SQLite database
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
    columns = "(meal, ingredients, recipe_link)"
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
    conn.close()
    return all_meals


def search_meals(keyword):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT meal, ingredients FROM meals
        WHERE meal LIKE '%{keyword}%'
        OR ingredients LIKE '%{keyword}%'
        """
    )
    all_meals = cur.fetchall()
    conn.close()
    return all_meals
