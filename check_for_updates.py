import os
import sys
from string import capwords
from time import sleep

import PySimpleGUI as sg
import requests
from packaging import version

from utils.remote_database_functions import internet_on

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
    if not internet_on():
        return False

    version_response = requests.get(
        "https://raw.githubusercontent.com/georgefahmy/meal-planner/main/resources/VERSION"
    )
    new_version = version_response.text.strip() if version_response.ok else None

    current_version = open(f"{wd}/resources/VERSION", "r").read().strip()

    restart = False
    if version.parse(current_version) >= version.parse(new_version):
        print("Version is up to date")

    elif version.parse(current_version) < version.parse(new_version):
        print("New Version available")
        new_version_url = f"https://github.com/georgefahmy/meal-planner/releases/download/v{new_version}/{FILENAME}"

        update_window = sg.Window(
            "Meal Planner Pro Update Available",
            [
                [
                    sg.Text(
                        "Update available...",
                        font=("Arial", 16),
                        key="title",
                    )
                ],
                [
                    sg.Text("", font=("Arial", 13), key="p_status", size=(50, 1)),
                ],
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
                    sg.Button("Download", key="d_b", auto_size_button=True),
                    sg.Button("Cancel", key="c_b", auto_size_button=True),
                ],
            ],
            disable_close=False,
            size=(300, 150),
            element_justification="c",
        )

        while True:
            update_event, values = update_window.read()
            if update_event:
                print(update_event, values)
            if update_event in ("c_b", sg.WIN_CLOSED):
                update_window.close()
                break

            if update_event == "d_b":
                update_window["p_status"].update(value="Downloading")
                update_window["progress"].update(visible=True)
                update_window["d_b"].update(visible=False)
                update_window["c_b"].update(visible=False)
                update_window["progress"].update(10)

                download_new_version(new_version_url, f"{wd}/resources/{FILENAME}")
                update_window["progress"].update(30)
                update_window["p_status"].update(value="Installing...")
                os.system(
                    "hdiutil attach " + wd.replace(" ", "\ ") + "/resources/" + FILENAME
                )
                update_window["progress"].update(50)
                update_window["p_status"].update(value="Removing old files...")
                os.system(
                    (
                        f"cp -r /Volumes/{VOLUME_NAME}/{VOLUME_NAME}.app"
                        + f" /Volumes/{VOLUME_NAME}/Applications/"
                    )
                )
                update_window["progress"].update(65)
                update_window["p_status"].update(value="Cleaning up download")

                os.system(f"hdiutil detach /Volumes/{VOLUME_NAME}")
                update_window["progress"].update(80)
                update_window["p_status"].update(value="Done!...Please Restart...")
                os.remove(f"{wd}/resources/{FILENAME}")
                update_window["progress"].update(100)
                restart = True
                sleep(5)
                update_window.close()
                break

    return restart
