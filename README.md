# Meal Planner PRO

This program helps you (and your SO) plan meals weekly. Cooking food, buying food, ordering. All of that is the easy part. The hard part is deciding what to eat... This program should help with that.

### Database

The meat of the program is a sql database with multiple tables keeping track of all different kinds of foods that you like. There are multiple interfaces for inserting food choices in different categories - Meats (beef, poultry, etc.), Veggies (salad, asparagus, brussle sprouts, etc.), Starches (rice, potatoes, quinoa, etc.), or anything other category with items. The goal is to be flexible in how you want to plan your meals


### TODO

* Create underlying database functions for inserting tables, and items within those tables
* build interface for adding items, and new categories (tables)
* design UI for easy use
* build a table viewer that shows the weeks' food choices with dates.
* Auto increment the dates (google docs doesnt have this)
* auto generate shopping list and quantities based on ingredients for larger recipes
* email report?
* table of past recipes that include links and can be referenced in the interface and opens up a the website (or downloads a pdf and saves it to the database)

### Required Items
* sqlite3
* pysimplegui
