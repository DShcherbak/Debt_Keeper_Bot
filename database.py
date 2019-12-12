import json

json_database = "data_file.json"
users_database = "reachable_users.json"


def save_to_database(group):
    groups = group.encode_to_JSON()
    with open(json_database, "w") as write_file:
        json.dump(groups, write_file)


def read_from_database():
    file_info = {}
    with open(json_database, "r") as read_file:
        file_info = json.load(read_file)
    return file_info


def get_users():
    file_info = {}
    with open(users_database, "r") as read_file:
        file_info = json.load(read_file)
    return file_info


def remember_users(users):
    with open(users_database, "w") as write_file:
        json.dump(users, write_file)
