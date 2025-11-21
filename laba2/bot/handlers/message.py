from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.inline import aim_menu, model_choice_menu, continue_menu
from config_.settings import (
    HF_TOKEN,
    GPT_MODEL_NAME,
    GPT_URL,
    LLAMA_MODEL_NAME,
    LLAMA_URL
)
from models.client_l import LlamaModelClient
from models.client_o import GPTClient

router = Router()

class TaskStates(StatesGroup):
    """
        Группа состояний для процесса решения задачи.

        waiting_for_task  - ожидание задания
        waiting_for_aim - ожидание цели ( разбор задания \ проверка )
        waiting_for_language - ожидание выбора языка программирования
        waiting_for_question - ожидание дополнительного вопроса к модели

    """
    waiting_for_task = State()      
    waiting_for_aim = State()       
    waiting_for_language = State() 
    waiting_for_question = State() 


@router.message(F.text == "Назад")
async def return_handler(message: Message, state: FSMContext) -> None:
    """
        Обрабатывает нажание на кнопку назад

        Возвращает пользователя к выбору модели, сбрасывая текущее состояние
        и отображая меню выбора модели.

        На вход: 
            message Message - входящее сообщение от юзера (НАЗАД)
            state FSMContext - контекст состояния FSM для управления диалогом

    """
    await message.answer("Выбери модель для использования:", reply_markup=model_choice_menu)
    await state.clear()
    await state.set_state(TaskStates.waiting_for_task)

@router.message(F.text == "Супер! Мне всё понятно")
async def return_handler(message: Message, state: FSMContext) -> None:
    """
        Обрабатывает нажание на кнопку "супер .... "

        На вход: 
            message Message - входящее сообщение от юзера (НАЗАД)
            state FSMContext - контекст состояния FSM для управления диалогом

    """
    await message.answer("Отлично! Рад, что смог помочь!\n\n Если появится новая задачка - просто напиши её мне!",
                         reply_markup=model_choice_menu)
    await state.clear()
    await state.set_state(TaskStates.waiting_for_task)


@router.message(lambda message: message.text in ["Llama", "GPT"])
async def model_choice_handler(message: Message, state: FSMContext) -> None:
    """
        Обрабатывает выбор модели
        Сохраняет модель в состоянии и переводит к состоянию 
        выбора языка программирования

        На вход: 
            message Message - входящее сообщение от юзера (Llama или gpt)
            state FSMContext - контекст состояния FSM для управления диалогом

    """
    selected_model = message.text
    await state.update_data(selected_model=selected_model)
    await message.answer(
        f"Ты выбрал {selected_model}. Будем ли мы использовать какой-нибудь язык программирования для написания кода?",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(TaskStates.waiting_for_language)


@router.message(TaskStates.waiting_for_language, F.text)
async def get_prog_language(message: Message, state: FSMContext) -> None:
    """
        Обрабатывает ввод языка программирования пользователем.

        Сохраняет выбранный язык в состоянии и переводит пользователя
        к этапу ввода задачи.

        На вход: 
            message Message - входящее сообщение от юзера (ЯЗЫК ПРОГРАММИРОВАНИЯ)
            state FSMContext - контекст состояния FSM для управления диалогом

    """
    selected_language = message.text.strip()
    await state.update_data(selected_language=selected_language)
    await message.answer("Пришли свой вопрос или задание",reply_markup=ReplyKeyboardRemove())
    await state.set_state(TaskStates.waiting_for_task)


@router.message(TaskStates.waiting_for_task, F.text)
async def task_handler(message: Message, state: FSMContext) -> None:
    """
        Обрабатывает ввод цели использования чата

        Сохраняет цель в состоянии и переводит пользователя
        к этапу ответа на вопрос.

        На вход: 
            message Message - входящее сообщение от юзера (конкретный вопрос пользователя)
            state FSMContext - контекст состояния FSM для управления диалогом

    """
    user_task = message.text.strip()
    await state.update_data(user_task=user_task)
    await message.answer("Задачка принята! Тебе необходима помощь с решением или хочешь, чтобы я проверил твое решение?",
                         reply_markup=aim_menu
    )
    await state.set_state(TaskStates.waiting_for_aim)


@router.message(TaskStates.waiting_for_aim, F.text == "Хочу разобраться в задачке")
async def help_with_solution_handler(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает запрос на помощь в решении задачи.

    Получает сохраненные данные (задачу, модель, язык) из состояния,
    отправляет запрос к выбранной модели для получения пошагового решения.

    На вход:
        message: Сообщение с выбором режима помощи
        state: Контекст состояния FSM для получения данных
    """
    data = await state.get_data()
    user_task = data.get("user_task")
    model = data.get("selected_model")
    language = data.get("selected_language")

    await message.answer("Хорошо! Ты скоро получишь ответ на вопрос\n\n""Если у тебя останутся вопросы - задавай!",
                         reply_markup=continue_menu)
    if model == 'Llama':
        llama_client = LlamaModelClient(LLAMA_URL, LLAMA_MODEL_NAME)
        ans = await llama_client.get_model_response(user_task, 'e', language)
    elif model == 'GPT':
        gpt_client = GPTClient(GPT_MODEL_NAME, HF_TOKEN, GPT_URL)
        ans = await gpt_client.get_model_response(user_task, 'e', language)
    await message.answer(ans, parse_mode=None)
    await state.set_state(TaskStates.waiting_for_aim)


@router.message(TaskStates.waiting_for_aim, F.text == "Проверь моё решение")
async def check_solution_handler(message: Message, state: FSMContext) -> None:
    """
        Обрабатывает запрос на проверку в решения задачи.

        Получает сохраненные данные (задачу, модель, язык) из состояния 
        и отправляет запрос к выбранной модели ИИ
        для получения обучающих подсказок и пошагового решения.

        На вход: 
            message Message - входящее сообщение от юзера (ПРОВЕРЬ МОЁ РЕШЕНИЕ)
            state FSMContext - контекст состояния FSM для управления диалогом

    """
    data = await state.get_data()
    user_task = data.get("user_task")
    model = data.get("selected_model")
    language = data.get("selected_language")
    if model == 'Llama':
        llama_client = LlamaModelClient(LLAMA_URL, LLAMA_MODEL_NAME)
        ans = await llama_client.get_model_response(user_task, 'c', language)
    elif model == 'GPT':
        gpt_client = GPTClient(GPT_MODEL_NAME, HF_TOKEN, GPT_URL)
        ans = await gpt_client.get_model_response(user_task, 'c', language)
    await message.answer(ans, parse_mode=None)
    await state.set_state(TaskStates.waiting_for_aim)

@router.message()
async def additional_questions_handler(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает дополнительные вопросы пользователя после получения основного ответа.
    
    На входЖ
    message Message - сообщение от пользователя (дополнительный вопрос)
    state FSMContext - контекст состояния FSM для управления диалогом

    """
    data = await state.get_data()
    model = data.get("selected_model") 
    language = data.get("selected_language")
    additional_question = message.text
    if model == 'Llama':
        llama_client = LlamaModelClient(LLAMA_URL, LLAMA_MODEL_NAME)
        ans = await llama_client.get_model_response(additional_question, 'a', language)
    if  model == 'GPT':
            gpt_client = GPTClient(GPT_MODEL_NAME, HF_TOKEN, GPT_URL)
            ans = await gpt_client.get_model_response(additional_question, 'a', language)
    await message.answer(ans, parse_mode=None)

    await message.answer("Есть ещё вопросы по этой задаче?", reply_markup=continue_menu)
    await state.set_state(TaskStates.waiting_for_aim)
