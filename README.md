# Meal Planner PRO

This program helps you (and your SO) plan meals weekly. Cooking food, buying food, ordering. All of that is the easy part. The hard part is deciding what to eat... This program should help with that.

## Database
The meat of the program is a sql database with multiple tables keeping track of all different kinds of foods that you like. There are multiple interfaces for inserting food choices in different categories - Meats (beef, poultry, etc.), Veggies (salad, asparagus, brussle sprouts, etc.), Starches (rice, potatoes, quinoa, etc.), or anything other category with items. The goal is to be flexible in how you want to plan your meals


## Usage
### Meal Selection
Choose from the available meals and choose a day of the week, then add it to the plan and see it appear in the table on the right. View ingredients associated with that meal in the ingredients list.


### New Meal
Add new meals to the database along with any ingredients and a link to a recipe


### New Recipe
Utilize the recipe interface to write a detailed recipe with quantities and instructions.


### Planning table
The planning table shows the meals chosen for each day of the week.


### Plan Ingredients List (Shopping List)
This ingredients list is a unique list of all the items you may need for all the meals. It does not double count, so if you need the same item for multiple meals, you'll have to account for that in the quantities purchased.


## Building The Application

NOTE: DO NOT DO THIS STEP FROM WITHIN A VIRTUAL ENVIRONMENT
* Make the setup file (if its not already created) `py2applet --make-setup planner_app.py`
* Make the application: run `python3 setup.py py2app`.
