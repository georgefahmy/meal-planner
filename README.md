# Meal Planner PRO

This program helps you (and your SO) plan meals weekly. Cooking food, buying food, ordering. All of that is the easy part. The hard part is deciding what to eat... This program should help with that.

## Database
The meat of the program is a sql database with multiple tables keeping track of all different kinds of foods that you like. There are multiple interfaces for inserting food choices in different categories - Meats (beef, poultry, etc.), Veggies (salad, asparagus, brussle sprouts, etc.), Starches (rice, potatoes, quinoa, etc.), or anything other category with items. The goal is to be flexible in how you want to plan your meals


## Usage
### Meal Selection
Choose from the available meals and choose a day of the week, then add it to the plan and see it appear in the table on the right. View ingredients associated with that meal in the ingredients list.


### New Meal
Add new meals to the database along with any ingredients and a link to a recipe


### Planning table
The planning table shows the meals chosen for each day of the week.


### Plan Ingredients List (Shopping List)

This ingredients list is a unique list of all the items you may need for all the meals. It does not double count, so if you need the same item for multiple meals, you'll have to account for that in the quantities purchased.


#### Building The Application

NOTE: DO NOT DO THIS STEP FROM WITHIN A VIRTUAL ENVIRONMENT
* Make the setup file `py2applet --make-setup planner_app.py`
* Finally make the application: run `python3 setup.py py2app`.


## Updates

### Version 2
#### Whats New
* Added ability to multi select items from the meal selection window using shift key
* Added ability to export and load databases via the file option in menu
* Added ability to clear a single day from the plan (Right click and remove it)
* Added ability to supply a new category, if it doesn't exist.
* Added the ability to see the selected meal's category
* Added the ability to export Meal plan & ingredients to a text file
* Each main GUI box now has a tooltip explaining what to do
* Added a date selection calendar to allow you to pick and plan future weeks

#### Fixed
* Updated working for some buttons and texts
* Increase font size for error messages
* Numerous bugs and strangeness


### FUTURE V3 - Recipe Interface
A Completely separate interface for adding detailed recipes including exact proportions and instructions.
* Add a popup window that allows for a detailed recipe to be added
* Meal name (also add meal to meal list)
* ingredients and proportions in a paired list (either tuples or paired list of lists)
* serving size - look up with is included in most recipes

* Add functional menu options
    * File -> add meal and ingredients
    * Edit -> Edit meal, edit ingredients, edit plan
    * Options -> increase font size (maybe)
    * Help -> about, guide, FAQs?, send feedback
