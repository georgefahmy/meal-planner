from pdfminer.high_level import extract_text
from time import sleep
from pprint import pprint
import collections
from utils.recipe_units import units
import sys, os


if sys.version_info.minor >= 10:
    from itertools import pairwise
else:
    from itertools import tee

    def pairwise(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)


categories = [
    "APPETIZERS & BEVERAGES",
    "SOUPS & SALADS",
    "VEGETABLES & SIDE DISHES",
    "MAIN DISHES",
    "DESSERTS",
    "BREADS & ROLLS",
    "COOKIES & CANDY",
    "THIS & THAT",
    "Vegetarian",
    "Vegetarian (Seafood)",
    "Coptic Cooking-Egyptian and Other Family Favorites",
]

cookbook_file = "/Users/GFahmy/Downloads/CopticCooking_Cookbook-111804 FINAL 2-19-07.pdf"
raw_text = extract_text(cookbook_file)
text_list = raw_text.split("\n")

j = 0
title_indexes = []
for i, line in enumerate(text_list):
    line = line.split("\x0c")[-1]
    if i - j <= 7:
        continue
    if line not in categories:
        if line.strip().isupper():
            title_indexes.append(i)
            j = i
title_indexes.append(len(text_list))

flat_units = [unit_sub_list for unit in units for unit_sub_list in unit]
meals = {}
k = 2
max_ingredient_lin_length = 45
for i, j in pairwise(title_indexes):
    clean_meal = []
    meal = text_list[i:j]
    for line in meal:
        if line not in clean_meal:
            clean_meal.append(line)
    title_words = [line for line in clean_meal if line.isupper() and line not in categories]
    title = " ".join(title_words).split("\x0c")[0].strip()
    title = title.replace('"', "'")
    subtitle_words = [line for line in clean_meal if line.startswith("(") and line.endswith(")")]
    subtitle = " ".join(subtitle_words)

    for x in title_words + subtitle_words:
        clean_meal.remove(x)

    ingredients = []
    for line in clean_meal:
        if (
            len(line) > max_ingredient_lin_length
            or len(line) == 0
            or line.strip().endswith(".")
            or line.strip().endswith(":")
            or line.startswith(" ")
            or line.isnumeric()
            or line.strip() in categories
            or line.strip == "For double pie crust"
            or line.strip == "For single pie crust"
        ):
            continue
        ingredients.append(line)

    for x in ingredients:
        clean_meal.remove(x)

    clean_meal = [
        x
        for x in clean_meal
        if not (x.isnumeric() or x.startswith(" ") or x.strip().endswith(":") or x in categories)
    ]
    instructions = " ".join([val.strip() for val in clean_meal if val]).strip()
    if title in meals.keys():
        title = title + f" #{k}"
    meals[title] = {
        "raw_meal": clean_meal,
        "title": title,
        "subtitle": subtitle,
        "ingredients": ingredients,
        "instructions": instructions,
    }

for meal in meals.keys():
    print("")
    print(meals[meal]["title"])
    print(meals[meal]["subtitle"])
    pprint(meals[meal]["ingredients"])
    print(meals[meal]["instructions"])
    cont = input("Modify? ")
    if cont != "":
        updated_title = input("Change title?: ")
        if updated_title:
            meals[meal]["title"] = updated_title
        updated_subtitle = input("Change subtitle?: ")
        if updated_subtitle:
            meals[meal]["subtitle"] = updated_subtitle
        updated_ingredients = input("Change/add ingredients?: ")
        if updated_ingredients:
            updated_ingredients = updated_ingredients.split(", ")
            meals[meal]["ingredients"] = meals[meal]["ingredients"] + updated_ingredients
        updated_instructions = input("Change instructions?: ")
        if updated_instructions:
            meals[meal]["instructions"] = updated_instructions

        print("")
        print(meals[meal]["title"])
        print(meals[meal]["subtitle"])
        pprint(meals[meal]["ingredients"])
        print(meals[meal]["instructions"])
