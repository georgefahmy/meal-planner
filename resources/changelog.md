# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v3.4.5] - 2022-09-04
Fixed a bug with exporting a plan. Ingredients were separated by a comma for every letter.

### New
- Fixed a plan export bug with commas.


## [v3.4.4] - 2022-08-23
Fixed an issue with capitalizing recipe names in the recipe interface.

### New
- Fixed an issue with capitalizing meal names in the recipe interface after submitting a new recipe.


## [v3.4.3] - 2022-08-22
Fixed an issue with clearing the meal selection window not erasing the keyword filter. Now when Cancel is chosen, the Keyword box will be cleared as well. Also updated the overwrite plan confirmation with the current selected date to be more clear for which plan the system thinks its overwriting.

### New
- Fixed an issue with clearing the keyword filter box when choose Cancel.
- Updated the plan submit overwrite prompt to be more clear as to which plan is being overwritten.


## [v3.4.2] - 2022-08-15
Fixed a bug with renaming meals. Now when changing a meal with a recipe, it will also update the recipe name.

### Fixed
- Fixed a bug with the renaming of meals and recipes


## [v3.4.1] - 2022-08-15
When selecting a new day checkbox, any other days already checked will be deselected.

### Added
- Auto deselect of checkboxes when selecting a new day.


## [v3.4.0] - 2022-08-15
Added a new search feature to the recipe viewer. This will allow searching through all available recipes for ingredients, or categories, or titles. Looking for all your available recipes that have 'Chicken' as an ingredient, now you can!

### Added
- Added a search bar to the recipe viewer window.


## [v3.3.2] - 2022-08-13
Fixed a bug with saving plans that would use the wrong date.

### Fixed
- Fixed a save bug with submitting plans.


## [v3.3.1] - 2022-08-11
When updating a recipe, if the overwrite is confirmed, will also update the basic recipe ingredients list.

### Fixed
- Fixed an issue that did not update the basic list of ingredients when a detailed recipe is updated


## [v3.3.0] - 2022-08-11
Improved the overall format of the meal selection and new meal sections. Larger viewing areas for the available meals, as well as ingredients makes it easier to read meal names that are more characters. Also improved the week day selection to be a completely vertically aligned list of days.

### New
- Reformatted the Filters section to be above the available meals section and the same width
- Made the overall available meal section larger, while reducing the new meal section to fit better
- Improved the day-of-week check boxes to be easier to use/read


## [v3.2.11] - 2022-08-10
Fixed a minor bug with the subtitles of recipes not updating if the subtitle is blank.

### Fixed
- Fixed subtitles updating.


## [v3.2.10] - 2022-08-10
Removed the history option from the import/export file popup for the recipe viewer.

### Removed
- Removed history from loading file popup window.


## [v3.2.9] - 2022-08-09
Fixed a big bug with loading an existing database. If a meal is removed from the database, but exists in a saved plan, it would crash the program if trying to load the plan.

### Fixed
- Updated sql functions to better handle loading plans with meals that have bee


## [v3.2.8] - 2022-08-09
Fixed a weird crash with editing plans. If no food was selected (because it was blank) the program would crash. This will no longer happen.

### Reverted
- Fixed crash with editing meals already in a plan if no meal is selected.


## [v3.2.7] - 2022-08-06
Loading files no longer forces the prompt window to remain on top. Much nicer on the eyes.

### Reverted
- Removed "stay_on_top=True" from the window generation for loading files.


## [v3.2.6] - 2022-08-05
Shopping list is now sorted.

### Changed
- The plan list of ingredients on the bottom right is now sorted alphabetically to make it easier to read.


## [v3.2.5] - 2022-08-01
Fixed a problem with python < 3.10.

### Changed
- Fixed an import issue for python <3.10. itertools has a pairwise() function for python >=3.10. for earlier versions, the functions needs to be defined separately.


## [v3.2.4] - 2022-07-30
Updated the recipe viewer with a dash in front of the ingredients to clearly identify a new ingredient from a newline.

### Changed
- Added dashes to the ingredient list when displaying the ingredients.


## [v3.2.3] - 2022-07-30
Minor changes to the recipe viewer to better handle wide texts.

### Changed
- Recipe Viewer now supports wider texts by wrapping them after 40 characters to a new line.


## [v3.2.2] - 2022-07-30
The checkboxes for choosing a day no longer clear after submitting a meal to the plan.

### Changed
- No longer clear the checkboxes after submitting a meal to the plan.


## [v3.2.1] - 2022-07-30
Fixed a small bug with the date picker not actually picking a date, now it does.

### Fixed
- Date picker not picking the actual date, but now it does.


## [v3.2.0] - 2022-07-30
Added the ability to import and export recipes as .rcp files! You can now share them with your friends and family!

### Added
- Added the ability to export a recipe from the recipe viewer interface as a .rcp file.
- Added the ability to import a recipe from the recipe viewer interface, if the file exists and is a valid .rcp file.

### Changed
- Changed how the database is made to now limit meal names to be unique.
- Updated the sql functions used to query the database to handle the new import/export of recipes
- Recipe names that already exist will be ignored during import (this may change in the future to auto increment the recipe name - i.e. Recipe(2))


## [v3.1.5] - 2022-07-30
Fixed a minor bug with a capitalization of the parsed recipe from a recipe link.

### Changed
- Fixed a bug capitalizing the title of a parsed recipe


## [v3.1.4] - 2022-07-29
Fixed a couple bugs

### Changed
- Fixed a bug with handling apostrophes


## [v3.1.3] - 2022-07-29
Fixed a couple bugs

### Changed
- Fixed a bug with windows not being visible. PySimpleGUI now sets alpha to .99 to workaround this problem.
- Fixed a bug with recipe link decoding into a constructed recipe.


## [v3.1.2] - 2022-07-28
Minor fixes to the Recipe Viewer interface

### Changed
- Bug fixes


## [v3.1.1] - 2022-07-27
Minor fixes to the Recipe Viewer interface

### Changed
- Bug fixes


## [v3.1.0] - 2022-07-26
New Recipe Viewer interface. This new view allows you to look at all your detailed recipes in a single place.

### Added
- New interface for viewing recipes


## [v3.0.0] - 2022-07-25
Release of Recipe Interface and all the related work. Provide a recipe link and let the app interpret it for you!

### Added
- Recipe Interface!
- Ability to provide a detailed recipe with quantities and instructions, stored in the database
- Ability to decode a recipe link into a structured recipe
- Additional menu items - Edit, Help. Additional ways to edit your meals, plans, and recipes.

### Changed
- Numerous fixes across the board for ease of use.


## [v2.1.0] - 2022-07-24
Fixed a bunch of small things to make the app more user friendly

### Added
- Added the ability to delete a plan from the database permanently

### Changed
- Fixed bug with adding meals to the plan, this should now work correctly
- Fixed a bug with the date picker picking the wrong date


## [v2.0.0] - 2022-07-15
This is a big release, fixes a lot of the nuances of the first release

### Added
- Added ability to multi select items from the meal selection window using shift key
- Added ability to export and load databases via the file option in menu
- Added ability to clear a single day from the plan (Right click and remove it)
- Added ability to supply a new category, if it doesn't exist.
- Added the ability to see the selected meal's category
- Added the ability to export Meal plan & ingredients to a text file
- Each main GUI box now has a tooltip explaining what to do
- Added a date selection calendar to allow you to pick and plan future weeks

### Changed
- Updated working for some buttons and texts
- Increase font size for error messages
- Numerous bugs and strangeness


## [v1.0.0] - 2022-07-10
First Release of Meal Planner PRO

### Added
- First release
- Basic functions including browsing meals, adding meals to the plan
