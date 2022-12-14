import os
import PySimpleGUI as sg
import requests
import sys
from packaging import version
from string import capwords
from utils.remote_database_functions import internet_on
from time import sleep

try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()

FILENAME = "meal-planner-pro.dmg"
VOLUME_NAME = capwords(FILENAME.replace("-", "\ ").split(".")[0])


def download_new_version(url, file_name):

    # Download the file from `url` and save it locally under `file_name`:
    with open(file_name, "wb") as out_file:
        content = requests.get(url, stream=True).content
        out_file.write(content)


# Check if outdated
def check_for_update():
    restart = False

    if not internet_on():
        return False

    version_response = requests.get(
        "https://raw.githubusercontent.com/georgefahmy/meal-planner/main/resources/VERSION"
    )
    new_version = version_response.text.strip() if version_response.ok else None

    current_version = open(wd + "/resources/VERSION", "r").read().strip()

    if version.parse(current_version) >= version.parse(new_version):
        print("Version is up to date")
        confirm = False

    elif version.parse(current_version) < version.parse(new_version):
        print("New Version available")
        new_version_url = (
            "https://github.com/georgefahmy/meal-planner/releases/download/v"
            + new_version
            + "/"
            + FILENAME
        )

        update_window = sg.Window(
            "Meal Planner Pro Update Available",
            [
                [
                    sg.Text(
                        "Update available Would you like to download?",
                        font=("Arial", 16),
                        key="title",
                    )
                ],
                [sg.Text("", font=("Arial", 13), key="p_status", size=(50, 1)),],
                [
                    sg.ProgressBar(
                        max_value=100,
                        orientation="h",
                        size=(150, 20),
                        key="progress",
                        visible=False,
                    ),
                ],
                [
                    sg.Button("Download", auto_size_button=True),
                    sg.Button("Cancel", auto_size_button=True),
                ],
            ],
            disable_close=False,
            size=(300, 150),
            element_justification="c",
        )

        while True:
            update_event, values = update_window.read()
            if update_event in ("Cancel", sg.WIN_CLOSED):
                update_window.close()
                break

            if update_event == "Download":

                update_window["progress"].update(visible=True)
                update_window["progress"].update(10)
                update_window["p_status"].update(value="Downloading")
                download_new_version(new_version_url, wd + "/resources/" + FILENAME)
                update_window["progress"].update(30)
                update_window["p_status"].update(value="Installing...")
                os.system(f"hdiutil attach " + wd.replace(" ", "\ ") + "/resources/" + FILENAME)
                update_window["progress"].update(50)
                update_window["p_status"].update(value="Removing old files...")
                os.system(
                    ("cp -r /Volumes/" + VOLUME_NAME + "/" + VOLUME_NAME + ".app")
                    + (" /Volumes/" + VOLUME_NAME + "/" + "Applications/")
                )
                update_window["progress"].update(65)
                update_window["p_status"].update(value="Cleaning up download")

                os.system("hdiutil detach " + ("/Volumes/" + VOLUME_NAME))
                update_window["progress"].update(80)
                update_window["p_status"].update(value="Done!")
                os.remove(wd + "/resources/" + FILENAME)
                update_window["progress"].update(100)
                update_window["title"].update(value="Reopen Meal Planner Pro")
                restart = True
                sleep(2)
                update_window.close()
                break

    return restart


# check_for_update()
