from parsing.lang.lang import load_lang
from state.state import get_state


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

def parse_message(message):
    user_id = str(message.from_user.id)
    chat_id = str(message.chat.id)
    return (user_id, chat_id)


def pretty_debts(debts):
   pass 
    

