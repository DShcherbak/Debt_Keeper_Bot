class Debt:
    payer = -1
    debtors = []
    sum = 0

    def encode_to_json(self):
        return {"payer": {0: self.payer}, "debtors": {0 : self.debtors}, "sum": {0 : self.sum}}

    def decode_from_json(self, json_group):
        self.payer = json_group["payer"]["0"]
        self.debtors = json_group["debtors"]["0"]
        self.sum = json_group["sum"]["0"]


class IncomingDebt:
    group_id = -1
    debt = Debt()


class Group:
    id = ""
    id_lib = {}
    names_lib = {}
    current_debt_id = 0
    debts = []

    def add_user(self, user_id, name='/unknown'):
        if user_id in self.names_lib:
            old_name = self.names_lib[user_id]
            self.id_lib.pop(old_name)
        self.id_lib.update([(name, user_id)])
        self.names_lib.update([(user_id, name)])

    def encode_to_json(self):
        encoded_debts = []
        for x in self.debts:
            encoded_debts.append(x.encode_to_json())
        return {"id": {0: self.id}, "id_lib": self.id_lib, "names_lib": dict(self.names_lib),
                "debt_id": {0: self.current_debt_id}, "debts": {0: encoded_debts}}

    def decode_from_json(self, json_group):
        self.id = json_group["id"]["0"]
        self.id_lib = json_group["id_lib"]

        self.names_lib = json_group["names_lib"]
        self.current_debt_id = json_group["debt_id"]["0"]
        encoded_debts = json_group["debts"]["0"]
        self.debts = []
        for x in encoded_debts:
            y = Debt()
            y.decode_from_json(x)
            self.debts.append(y)


    def renew(self, another_group):
        self.id = another_group.id
        self.id_lib = dict(another_group.id_lib)
        self.names_lib = dict(another_group.names_lib)
        self.current_debt_id = another_group.current_debt_id
        self.debts = list(another_group.debts)



