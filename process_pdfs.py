from pdfminer.high_level import extract_text
from time import sleep
from pprint import pprint
import collections
from itertools import pairwise
from utils.recipe_units import units

categories = [
    "APPETIZERS & BEVERAGES",
    "SOUPS & SALADS",
    "VEGETABLES & SIDE DISHES",
    "MAIN DISHES",
    "DESSERTS",
    "BREADS & ROLLS",
    "COOKIES & CANDY",
    "THIS & THAT",
]

cookbook_file = "/Users/GFahmy/Downloads/CopticCooking_Cookbook-111804 FINAL 2-19-07.pdf"
raw_text = extract_text(cookbook_file)
text_list = raw_text.split("\n")
j = 0
title_indexes = []
for i, line in enumerate(text_list):
    line = line.split("\x0c")[-1]
    if i - j <= 6:
        continue
    if line not in categories:
        if line.strip().isupper():
            title_indexes.append(i)
            j = i
title_indexes.append(len(text_list))

flat_units = [unit_sub_list for unit in units for unit_sub_list in unit]
meals = {}
k = 2
for i, j in pairwise(title_indexes):
    clean_meal = []
    ingredients = []
    meal = text_list[i:j]
    for line in meal:
        if line == "":
            clean_meal.append(line)
        elif line not in clean_meal:
            clean_meal.append(line)
    title_words = [line for line in clean_meal if line.isupper() and line not in categories]
    title = " ".join(title_words).split("\x0c")[0]
    subtitle_words = [line for line in clean_meal if line.startswith("(") and line.endswith(")")]
    subtitle = " ".join(subtitle_words)
    ingredients = [
        line for line in clean_meal if [word for word in line.split() if word.strip() in flat_units]
    ]
    for x in title_words + subtitle_words + ingredients:
        clean_meal.remove(x)
    if title in meals.keys():
        title = title + f" #{k}"
    meals[title] = {
        "raw_meal": clean_meal,
        "title": title,
        "subtitle": subtitle,
        "ingredients": ingredients,
    }
