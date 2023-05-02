import json
from state.state import State
from state.user import User, UserState
from state.debt import Debt
from state.group import Group

json_database = "parsing/data_file.json"
users_database = "parsing/reachable_users.json"


def save_to_database(state):
    with open(json_database, "w") as write_file:
        write_file.write(state_to_json(state))


def read_from_database():
    with open(users_database, "r") as file:
        json_data = json.load(file)

    json_string = json.dumps(json_data)
    state = json_to_state(json_string)
    return state


def state_to_json(state):
    def group_to_dict(group):
        return {
            'id': group.id,
            'users': {user_id: user_to_dict(user) for user_id, user in group.users.items()},
            'debts': [debt_to_dict(debt) for debt in group.debts],
        }

    def user_to_dict(user):
        return {
            'id': user.id,
            'name': user.name,
            'state': user.state.name,
        }

    def debt_to_dict(debt):
        return {
            'payer': debt.payer,
            'amount': debt.amount,
            'debtors': debt.debtors,
        }

    return json.dumps({
        'groups': {group_id: group_to_dict(group) for group_id, group in state.groups.items()},
        'reachable_users': state.reachable_users,
    })

def json_to_state(json_string):
    def dict_to_group(dict_):
        group = Group(dict_['id'])
        group.users = {int(user_id): dict_to_user(user_dict) for user_id, user_dict in dict_['users'].items()}
        group.debts = [dict_to_debt(debt_dict) for debt_dict in dict_['debts']]
        return group

    def dict_to_user(dict_):
        user = User(dict_['id'], dict_['name'])
        user.state = UserState[dict_['state']]
        return user

    def dict_to_debt(dict_):
        return Debt(dict_['payer'], dict_['amount'], dict_['debtors'])

    dict_ = json.loads(json_string)
    state = State()
    state.groups = {int(group_id): dict_to_group(group_dict) for group_id, group_dict in dict_['groups'].items()}
    state.reachable_users = dict_['reachable_users']
    return state