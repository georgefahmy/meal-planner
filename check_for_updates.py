import os
import PySimpleGUI as sg
import requests
import sys
from string import capwords

try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()

FILENAME = "meal-planner-pro.dmg"
VOLUME_NAME = capwords(FILENAME.replace("-", "\ ").split(".")[0])

version_response = requests.get(
    "https://raw.githubusercontent.com/georgefahmy/meal-planner/main/resources/VERSION"
)
new_version = version_response.text.strip() if version_response.ok else None

current_version = open(wd + "/resources/VERSION", "r").read().strip()


def download_new_version(url, file_name):

    # Download the file from `url` and save it locally under `file_name`:
    with open(file_name, "wb") as out_file:
        content = requests.get(url, stream=True).content
        out_file.write(content)


# Check if outdated
def check_for_update():
    if current_version >= new_version:
        print("Version is up to date")
        confirm = False

    elif current_version < new_version:
        print("New Version available")
        new_version_url = (
            "https://github.com/georgefahmy/meal-planner/releases/download/v"
            + new_version
            + "/"
            + FILENAME
        )

        confirm, _ = sg.Window(
            "Meal Planner Pro Update Available",
            [
                [sg.Text("Update available Would you like to download?", font=("Arial", 16),)],
                [
                    sg.Button("Download", auto_size_button=True),
                    sg.Button("Cancel", auto_size_button=True),
                ],
            ],
            disable_close=False,
            size=(300, 100),
            element_justification="c",
        ).read(close=True)

    if confirm == "Download":
        pass
        download_new_version(new_version_url, wd + "/" + FILENAME)
        os.system(f"hdiutil attach {wd + '/' + FILENAME}")
        os.system(
            ("cp -r /Volumes/" + VOLUME_NAME + "/" + VOLUME_NAME + ".app")
            + (" /Volumes/" + VOLUME_NAME + "/" + "Applications/")
        )
        os.system("hdiutil detach " + ("/Volumes/" + VOLUME_NAME))
        os.remove(f"{wd + '/' + FILENAME}")


# check_for_update()
