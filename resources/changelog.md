# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
