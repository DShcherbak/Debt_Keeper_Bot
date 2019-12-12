import json

json_database = "data_file.json"

class Debt:
    payer = -1
    debtors = []
    sum = 0


class Group:
    id = 0
    id_lib = {}
    names_lib = {}
    current_debt_id = 0
    debts = []

    def encode_to_JSON(group):
        return {"id": {0: group.id}, "id_lib": group.id_lib, "names_lib": group.names_lib,
                "debt_id": {0: group.current_debt_id}, "debts": {0: group.debts}}

    def decode_from_JSON(self, json_group):
        self.id = json_group["id"]["0"]
        self.id_lib = json_group["id_lib"]
        self.names_lib = json_group["names_lib"]
        self.id_lib = json_group["debt_id"]["0"]
        self.id_lib = json_group["debts"]["0"]


def save_to_database(group):
    groups = group.encode_to_JSON()
    with open(json_database, "w") as write_file:
        json.dump(groups, write_file)


def read_from_database():
    file_info = {}
    with open(json_database, "r") as read_file:
        file_info = json.load(read_file)
    return file_info
