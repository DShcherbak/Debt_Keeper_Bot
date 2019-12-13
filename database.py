import json

json_database = "data_file.json"
users_database = "reachable_users.json"


def save_to_database(groups):
    encoded_groups = {}
    for group_id in groups:
        encoded_groups.update([(group_id, groups[group_id].encode_to_json())])
    with open(json_database, "w") as write_file:
        json.dump(encoded_groups, write_file)


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
