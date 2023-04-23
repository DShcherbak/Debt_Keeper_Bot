def parse_float(value):
    try:
        val = float(value)
        if val > 0:
            return val
        return 0
    except ValueError:
        return 0
    

def is_private(message):
    return message.chat.type == 'private'


def is_group(message):
    return not is_private(message)


def check_user_state(state, user_state):
    return lambda message: state.is_reachable(message.from_user.id) and state.check_user_state(message.from_user.id, user_state)


def parse_message(message):
    user_id = str(message.from_user.id)
    chat_id = str(message.chat.id)
    return (user_id, chat_id)


def parse_user(state, message, group_id):
    name = message.text
    id = state.get_id(group_id, name)
    return (name, id)


def parse_group_message(state, message):
    (user_id, group_id) = parse_message(message)
    user = state.groups[group_id].users[user_id]
    return (user_id, group_id, user)


def pretty_debts(debts):
    

