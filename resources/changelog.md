# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v4.0.0] - 2022-11-17

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
