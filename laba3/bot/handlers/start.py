
from aiogram import Bot, Router,F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.keyboards.inline import start_button, choice_buttons, like_or_dislike, category_button, index_group_button,product_group_button
from core.states import SurveyStates
from storage.json_storage import load_user_data, save_user_data
from models.data_loader import top_at_all, get_name_by_label, articles
from models.topk import top_popularity_items_by_product, top_popularity_items_by_index
from models.data_loader import prepare_date
from models.features import create_item_id_to_iid, get_vector_for_new_customers
from models.collaborative_filtering import create_user_item_matrix, create_item_item_matrix, get_k_recommendations, get_top_k_items

router = Router() 

def init_user_data(user_id: int) -> dict:
    """Инициализирует данные нового пользователя"""
    return {
        "user_id": user_id,
        "bought_items": []
    }

@router.message(Command("start"))
async def start_command_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_data({
        "selected_index_names": [],
        "selected_product_names": [],
    })
    await message.answer(
        "Привет🧚🏻‍♀️! Сегодня у нас по планам шоппинг!.🤍 \n\n" \
        "Посмотрим делал ли ты уже покупки...🎀🍒. \n\n",
        reply_markup=start_button
    )

@router.message(F.text == "ура-ура!🪇")
async def check_user(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user_data = load_user_data(user_id)

    if not user_data:
        user_data = init_user_data(user_id)
        save_user_data(user_id, user_data)
        await message.answer(
            f"Ты у нас впервые! \n" \
            f"Готов ли ты ответить на пару вопросов о своих покупках за последний год?",
            reply_markup=choice_buttons
        )
        await state.set_state(SurveyStates.asking_about_purchases)
    else:
        await message.answer(f"С возвращением! У тебя уже есть история покупок. \n \n Готов ответить на пару вопросов?",
                                 reply_markup=choice_buttons)
        await state.set_state(SurveyStates.asking_about_purchases)

@router.callback_query(lambda c: c.data == "no", SurveyStates.asking_about_purchases)
async def handle_exception(callback: CallbackQuery, state: FSMContext):
    result = get_name_by_label()
    await state.update_data(recommended_items=result, current_item_index=0)
    await show_next_item(callback.message, state)
    await callback.answer()

async def show_next_item(message: Message, state: FSMContext):
    data = await state.get_data()
    items = data.get('recommended_items', [])
    current_index = data.get('current_item_index', 0)
    
    if current_index < len(items):
        item = items[current_index]
        await message.answer(
            f"{item['name']}\n"
            f"{item['desc']}",
            reply_markup=like_or_dislike
        )
        await state.set_state(SurveyStates.asking_about_item)
    else:
        await state.set_state(SurveyStates.asking_about_purchases)

@router.callback_query(lambda c: c.data == "like", SurveyStates.asking_about_item)
async def handle_like(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    items = data.get('recommended_items', [])
    current_index = data.get('current_item_index', 0)
    
    if current_index < len(items):
        from models.data_loader import articles, top_at_all
        item_name = items[current_index]['name']
        matching_article = articles[articles['prod_name'] == item_name]
        
        if not matching_article.empty:
            article_id = matching_article.iloc[0]['article_id']
            
            user_data = load_user_data(user_id)
            if article_id not in user_data['bought_items']:
                user_data['bought_items'].append(article_id)
                save_user_data(user_id, user_data)
            
            await callback.answer("Добавлено в понравившиеся!")
    
    await state.update_data(current_item_index=current_index + 1)
    await callback.message.delete()
    await show_next_item(callback.message, state)


@router.callback_query(lambda c: c.data == "dislike", SurveyStates.asking_about_item)
async def handle_dislike(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_index = data.get('current_item_index', 0)
    
    await state.update_data(current_item_index=current_index + 1)
    await callback.message.delete()
    await show_next_item(callback.message, state)

    
@router.callback_query(lambda c: c.data == "yes", SurveyStates.asking_about_purchases) 
async def handle_yes(callback: CallbackQuery, state: FSMContext) -> None: 
    await callback.message.answer( 
        f"🎀 Индекс - это деление товаров по половому, возрастному признаку \n" \
        f"🎀 Тип - это категория товара",
        reply_markup=category_button
    )
    await state.set_state(SurveyStates.choosing_category_type)
    await callback.answer()


@router.message(F.text == 'Индекс', SurveyStates.choosing_category_type)
async def handle_index(message: Message, state:FSMContext)-> None:
    await message.answer(
        f"Теперь выбери категорию",
        reply_markup=index_group_button
        )
    await state.set_state(SurveyStates.choosing_index)

@router.message(F.text == 'Тип')
async def handle_index(message: Message, state:FSMContext)-> None:
    await message.answer(
        f"Теперь выбери категорию",
        reply_markup=product_group_button
        )
    await state.set_state(SurveyStates.choosing_product) 

@router.message(F.text.in_(["Ladieswear", "Menswear", "Divided", "Baby/Children", "Sport"]), SurveyStates.choosing_index)
async def handle_specific_index(message: Message, state: FSMContext):
    index_name = message.text
    await message.answer(
        "Эти товары были самыми популярные в течение прошлого года! Может быть ты успел что-нибудь прикупить?"
    )
    top_items = top_popularity_items_by_index(prepare_date, index_name, k=6)
    result = get_name_by_label(top_at_all=top_items)

    await state.update_data(
        recommended_items=result,
        current_item_index=0,
        selected_category=index_name
    )
    
    await message.answer(f"Отлично! Выбрана продуктовая группа: {index_name} \
                         \n Когда закончишь с опросом - напиши **готово**, я подготовлю для тебя персональные рекомендации")
    await show_next_item(message, state)


@router.message(F.text.in_([
    "Garment Upper body", "Underwear", "Garment Lower body", "Accessories", 
    "Nightwear", "Swimwear", "Garment Full body", "Shoes", "Bags"
]), SurveyStates.choosing_product)
async def handle_specific_product(message: Message, state: FSMContext):
    product_name = message.text
    top_items = top_popularity_items_by_product(prepare_date, product_name, k=6)
    result = get_name_by_label(top_at_all=top_items)
    await state.update_data(
        recommended_items=result,
        current_item_index=0,
        selected_category=product_name
    )
    await message.answer(f"Отлично! Выбрана продуктовая группа: {product_name} \
                         \n Когда закончишь с опросом - напиши **готово**, я подготовлю для тебя персональные рекомендации")
    await show_next_item(message, state)

@router.message(F.text == "Готово")
async def send_recomendations(message: Message, state: FSMContext):
    await message.answer(
        "Расчитываю рекомендации!"
    )
    user_id = message.from_user.id
    user_data = load_user_data(user_id)
    print(user_data)
    item_id_to_iid = create_item_id_to_iid(prepare_date)
    user_vector = get_vector_for_new_customers(user_data, item_id_to_iid, articles)
    await message.answer(
        "Вектор взаимодействий получен!"
    )
    user_item =create_user_item_matrix(prepare_date)
    await message.answer(
        "Матрица юзер-айтем создана!"
    )
    item_item = create_item_item_matrix(user_item.T)
    await message.answer(
        "Матрица айтем-айтем создана!!"
    )
    item_item_top_k = get_top_k_items(item_item, TOP = 50)
    recommendations = get_k_recommendations(user_vector, item_item_top_k, k = 5)
    await message.answer(
        "Рекомендации получены!"
    )
    await state.update_data(
        recommended_items=recommendations,
        current_item_index=0
    )
    await show_next_item(message, state)
    