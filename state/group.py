from state.user import User

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