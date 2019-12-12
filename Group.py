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

    def add_user(self, user_id, name='/unknown'):
        if user_id in self.names_lib:
            old_name = self.names_lib[user_id]
            self.id_lib.pop(old_name)
            self.names_lib[user_id] = name
        else:
            self.id_lib.update([(name, id)])
            self.names_lib.update([(id, name)])

    def encode_to_json(self):
        return {"id": {0: self.id}, "id_lib": self.id_lib, "names_lib": self.names_lib,
                "debt_id": {0: self.current_debt_id}, "debts": {0: self.debts}}

    def decode_from_json(self, json_group):
        self.id = json_group["id"]["0"]
        self.id_lib = json_group["id_lib"]
        self.names_lib = json_group["names_lib"]
        self.id_lib = json_group["debt_id"]["0"]
        self.id_lib = json_group["debts"]["0"]
