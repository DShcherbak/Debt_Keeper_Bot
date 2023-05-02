from state.user import User


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


class Group:
    def __init__(self, id):
        self.id = id
        self.users = {}
        self.users_by_name = {}
        self.debts = []

    def add_user(self, user_id, user_name):
        self.users[user_id] = User(user_id, user_name)
        self.users_by_name[user_name] = User(user_id, user_name)

    def add_transaction(self, t):
        self.debts.append(t)

    def set_user_state(self, id, state):
        self.users[id].set_state(state)

    def get_name(self, user_id):
        if user_id in self.users:
            return self.users[user_id].name
        return "???"

    def debt_to_text(self, debt):
        text = self.get_name(debt.payer) + ' : ' + str(debt.sum) + ' <- '
        for d in debt.debtors:
            text += self.get_name(d) + ', '
        text = text[:-2] + ';'
        return text

    def get_debts(self):
        text = ""
        for debt in self.debts:
            text += self.debt_to_text(debt)

    def get_id(self, name):
        if name in self.users_by_name:
            return self.users_by_name[name]
        return ""


    def resolve(self):
        pass


    def settle(self):
        self.debts = []


    def encode_to_json(self):
        encoded_debts = []
        for x in self.debts:
            encoded_debts.append(x.encode_to_json())
        return {"id": {0: self.id}, "id_lib": self.users, "names_lib": dict(self.names_lib),  "debts": {0: encoded_debts}}

    def decode_from_json(self, json_group):
        self.id = json_group["id"]["0"]
        self.id_lib = json_group["id_lib"]

        self.names_lib = json_group["names_lib"]
        encoded_debts = json_group["debts"]["0"]
        self.debts = []
        for x in encoded_debts:
            y = Debt()
            y.decode_from_json(x)
            self.debts.append(y)
