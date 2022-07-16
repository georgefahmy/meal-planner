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


### TODO
* Add functional menu options
    * add meal, ingredients
    * edit meal, ingredients
    * edit plan
    * about
    * maybe feedback?
* Improve this list to include quantities based on meal recipes or ingredients
* Add date selection rather than just assuming the start of the current week

##### Recipe Interface
* Add a popup window that allows for a detailed recipe to be added
* Meal name (also add meal to meal list)
* ingredients and proportions in a paired list (either tuples or paired list of lists)
* serving size - look up with is included in most recipes

#### Feedback

* You should be able to add a new category by typing a new one into the New Meal, Meal Category field. If it exists, it’s on the list, if not, it adds it.
* When you click on a Meal Selection, you should be able to see somewhere what category it’s in.
* Export Meal plan & Ingredients list to a txt file or note


* DONE ~For each main GUI box, add a sentence with instructions (e.g., add a comma separating multiple ingredients)~
* DONE ~The shopping list should not list duplicates~
* Shopping list should add quantities together to provide total
* DONE ~Change 'Finalize Plan' to 'Save' - It should ask if you want to save your new meal plan before you close the app. (I added a plan but didn’t “finalize” it, and it didn’t save.) Maybe you should change “Finalize” to “Save”~
* DONE ~Change "Meal Filter" to "Keyword Filter"~
* DONE ~Multiple item select in the meals list by holding down Command (shift)~
* DONE ~Add ability to export and load databases~
* DONE ~Increase font size for error messages~
* DONE ~Clear a single day from the plan (Right click and remove it)~
