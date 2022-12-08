import re
from dataclasses import dataclass, field, fields
from recipe_units import units

fixed_units = []
for unit in units:
    for detailed_unit in unit:
        fixed_unit = []
        for character in detailed_unit:
            if character == ".":
                character = r"\{}".format(character)
            fixed_unit.append(character)
        fixed_units.append("".join(fixed_unit))

fixed_units.reverse()
unit_expression = "|".join(fixed_units)
match_expression = f"([0-9\/\.\-\s]*)?\s?({unit_expression})?\s*?([a-zA-Z0-9\s\-\.]*),?\s?(.*)?"

@dataclass
class Ingredient():
    raw: str = ""
    def __init__(self, raw):
        parsed_ingredient = list(
            re.match(match_expression, raw, flags=re.IGNORECASE).groups()
        )
        for i, val in enumerate(parsed_ingredient):
            if val:
                parsed_ingredient[i] = val.strip()
        self.raw = raw
        self.quantity: int = parsed_ingredient[0]
        self.units: str = parsed_ingredient[1]
        self.name: str = parsed_ingredient[2]
        self.special_instruction: str = parsed_ingredient[3]


@dataclass
class Recipe:
    title: str
    ingredients: list[Ingredient] = field(default_factory=list)
    link: str = ""
    recipe_data: str = ""
    category: str = ""
    def __init__(self, title, ingredients):
        self.title = title
        self.ingredients = []
        for ingredient in ingredients:
            self.ingredients.append(Ingredient(ingredient))



@dataclass
class Plan:
    monday: list[Recipe] = field(default_factory=list)
    tuesday: list[Recipe] = field(default_factory=list)
    wednesday: list[Recipe] = field(default_factory=list)
    thursday: list[Recipe] = field(default_factory=list)
    friday: list[Recipe] = field(default_factory=list)
    saturday: list[Recipe] = field(default_factory=list)
    sunday: list[Recipe] = field(default_factory=list)

@dataclass
class ShoppingList:
    plan: Plan = field(repr=False)
    ingredients: list[Ingredient] = field(default_factory=list)
