from aiogram.fsm.state import State, StatesGroup


class MarginStates(StatesGroup):
    waiting_for_price = State()
    waiting_for_cost = State()
