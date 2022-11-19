import paramiko
import os
import sys
import json

try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()

db_file = os.path.join(wd, "database.db")
settings = json.load(open(os.path.join(wd, "settings.json"), "r"))
username, password = settings["username"], settings["password"]


def connect_to_remote_server():
    transport = paramiko.Transport(("trading-pi-meal-planner.at.remote.it", 33000))
    transport.connect(None, "meal-planner", "meal-planner")
    sftp = paramiko.SFTPClient.from_transport(transport)
    if sftp:
        print("Connected to Meal Planner server")
        return sftp, transport
    else:
        return None, None


def close_connection_to_remote_server(sftp, transport):
    if sftp:
        sftp.close()
    if transport:
        transport.close()


def check_username_password(sftp, username, password):

    remote_username_password_file = "meal-planner/user_password.json"
    with sftp.open(remote_username_password_file, "r") as fp:
        json_file = json.loads(fp.read(fp.stat().st_size))

    if not username or not password:
        # add a future update to make usernames an email
        return False

    if username in json_file:
        stored_password = json_file[username]["password"]
        if stored_password == password:
            authentication = True
        else:
            # password is incorrect
            authentication = False
    else:
        json_file[username] = {"password": password, "username": username, "email": ""}
        authentication = True

    with sftp.open(remote_username_password_file, "w") as fp:
        json.dump(json_file, fp, indent=4, sort_keys=True)
    return authentication


def get_database_from_remote(sftp, username, password):
    try:
        remote_databases_folder = "meal-planner/databases/"
        database_files = [
            database
            for database in sftp.listdir(remote_databases_folder)
            if database.endswith(".db")
        ]
        database_file = [file for file in database_files if username == file.split("_")[0]]
        if not database_file:
            return None
        database_file = database_file[0]
        destination_file_name = database_file.split("_")[-1]
        sftp.get(
            os.path.join(remote_databases_folder, database_file.strip()),
            os.path.join(wd, destination_file_name),
        )
    except OSError:
        print("Logged out...Please Login again")


def send_database_to_remote(sftp, username, password):
    auth = check_username_password(sftp, username, password)
    if not auth:
        print("Incorrect Username or Password")
        return
    try:
        remote_databases_folder = "meal-planner/databases/"
        database_file = os.path.join(wd, "database.db")
        sftp.put(database_file, os.path.join(remote_databases_folder, username + "_database.db"))
    except OSError:
        print("Logged out...Please Login again")


# sftp, transport = connect_to_remote_server()
# close_connection_to_remote_server(sftp, transport)
# send_database_to_remote(sftp, username)
# get_database_from_remote(sftp, username)
