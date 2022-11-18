# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v4.0.0] - 2022-11-17

Version 4.0 is here! This version features a highly simplified interface for entering new recipes. You can either enter them manually or from a URL.

The new plan interface allows you to easily move meals from one day to another with a simple right click on the table, choosing your meal and then an action. Speaking of plans, when a meal is added to the weekly plan, the plan is automatically saved in the database, so if you close the program and come back you won't lose your progress.

Meal plans are now easily accessible from the "Available Plans" button. You can load past plans, view plans and export them to a text file to share.  

The Plan Ingredients list now features adding like ingredients together to get a proper total quantity. This makes generating a shopping list much easier now that the total ingredients across all meals is known.

A lot of background work has been done to clean up the underlying code for efficiency. Also, to make things a bit clearly, Monday is now the first day of the week on the calendar as well as the table. 

### New
- Formatting of the ingredients list with quantities
- Adding like ingredients to calculate an accurate list of ingredients
- Cleaned up the plan and table interface buttons to handle everything through "Available Plans"
- Plans are now saved automatically when adding a new meal to the plan
- The plan table now supports dynamically managing meals
    - Right clicking on the table displays options for each meal
    - The ability to move meals from one day to another day via the right click menu

### Improvements
- Within the Available Plans window, can now manage plans (Export, Load, Delete)
- Monday is now the first day of the week, all the backend database support can now handle this
- Simplified the New Meal interface to only have one way to enter a meal, via a recipe
- Online Recipe Parser library compatibility, as well as if it fails a blank recipe screen now opens
- All meals now have a corresponding recipe, even if there are no detailed quantities, etc.
- Meal List right click now has limited options based on the changes to all meals having a recipe
