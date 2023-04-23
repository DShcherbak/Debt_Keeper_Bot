from enum import Enum
from user import User, UserState




class Group:
    def __init__(self, id):
        self.id = id
        self.users = {}
        self.user_by_name = {}
        self.debts = []

    def add_user(self, user_id, user):
        self.users[user_id] = user
        self.users_by_name[user.name] = user_id

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
        if name in self.user_by_name:
            return self.user_by_name[name]
        return ""


    def resolve(self):
        pass


    def settle(self):
        self.debts = []


class State:
    def __init__(self):
        self.groups = {}
        self.reachable_users = []
        self.incoming_debts = []

    def add_group(self, group):
        self.groups[group.id] = group

    def add_user(self, group, user_id, user_name):
        self.groups[group].add_user(user_id, user_name)

    def set_user_state(self, group_id, user_id, state):
        self.groups[group_id].set_user_state(user_id, state)

    def get_id(self, group_id, name):
        return self.groups[group_id].get_id(name)
    
    def get_name(self, group_id, user_id):
        return self.groups[group_id].get_name(user_id)


def get_state():
    return State()
