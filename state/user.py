from enum import Enum
from state.debt import Debt

class UserState(Enum):
    Default = 1
    GetName = 2
    NewDebt = 3
    Payer   = 4
    Debtors = 5
    Sum     = 6


class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.state = UserState.Default
        self.new_debt = Debt()

    def set_state(self, state):
        self.state = state