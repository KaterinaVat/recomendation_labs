from aiogram.fsm.state import State, StatesGroup

class SurveyStates(StatesGroup):
    """
        Состояния для опроса пользователя
    """
    asking_about_purchases = State()      
    choosing_category_type = State()
    choosing_index = State()  
    choosing_product = State()               
    asking_about_item = State()
    collaba_resc = State()
    