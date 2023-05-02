from enum import Enum
from state.user import User, UserState


class State:
    def __init__(self):
        self.groups = {}
        self.reachable_users = []

    def add_group(self, group):
        self.groups[group.id] = group

    def knows_group(self, group_id):
        return group_id in self.groups

    def add_user(self, group, user_id, user_name):
        self.groups[group].add_user(user_id, user_name)

    def reach_user(self, user_id):
        self.reachable_users.append(user_id)

    def is_reachable(self, user_id):
        print(user_id, "NOT IN", self.reachable_users)
        return user_id in self.reachable_users

    def set_user_state(self, group_id, user_id, state):
        self.groups[group_id].set_user_state(user_id, state)

    def get_id(self, group_id, name):
        return self.groups[group_id].get_id(name)
    
    def get_name(self, group_id, user_id):
        return self.groups[group_id].get_name(user_id)


def get_state():
    return State()
