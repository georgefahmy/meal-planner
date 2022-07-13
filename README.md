# Meal Planner PRO

This program helps you (and your SO) plan meals weekly. Cooking food, buying food, ordering. All of that is the easy part. The hard part is deciding what to eat... This program should help with that.

## Database
The meat of the program is a sql database with multiple tables keeping track of all different kinds of foods that you like. There are multiple interfaces for inserting food choices in different categories - Meats (beef, poultry, etc.), Veggies (salad, asparagus, brussle sprouts, etc.), Starches (rice, potatoes, quinoa, etc.), or anything other category with items. The goal is to be flexible in how you want to plan your meals

### Multiple Databases supported!
You can have multiple databases, maybe have one for dinners, desserts, or breakfasts.


## Usage
### Meal Selection
Choose from the available meals and choose a day of the week, then add it to the plan and see it appear in the table on the right. View ingredients associated with that meal in the ingredients list.


### New Meal
Add new meals to the database along with any ingredients and a link to a recipe
* TODO: Add a better recipe interface with steps and proportions


### Planning table
The planning table shows the meals chosen for each day of the week.


### Plan Ingredients List (Shopping List)

This ingredients list is a unique list of all the items you may need for all the meals. It does not double count, so if you need the same item for multiple meals, you'll have to account for that in the quantities purchased.
* TODO: improve this list to include quantities based on meal recipes or ingredients

###Menu Updates
* TODO: add a menu where you can have options to edit meals, edit ingredients, edit database name, etc.
