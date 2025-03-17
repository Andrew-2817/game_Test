import os
import re
from aiogram import Router, types, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, UserProfilePhotos
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext 
from keyboards import main_keyboard, info_keyboard, start_keyboard, profile_keyboard, play_keyboard, tour_keyboard, leadboards_keyboard,info_cuefa_keyboard, history_of_matches_keyboard, extended_static_keyboard, leadboards_season_back_keyboards, leadboards_season_3_back_keyboards, history_of_matches_back_keyboard, shop_keyboard, start_keyboard_premium, start_keyboard_standart
from db import get_db_connection
from datetime import datetime
from db_moves.add_db import add_user, change_user_design, make_buy, update_days_for_user, init_player_statistics, add_shop, update_user_coins, buy_premium_or_check_end_date
from db_moves.get_db import check_chop_el, display_main_leaderboard, display_main_statistics, display_penalty_cuefa_leaderboard, display_total_days, get_player_shop, get_user_coins, check_user_role, check_player_design
import time
from db_moves.get_db import check_user_role
from dotenv import load_dotenv
import asyncio
from math import *

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
player_router = Router()

# сюда пожалуйста фоток немного по теме приблизительно прям с инета спизди 
cached_photo_path = types.FSInputFile(os.path.join("img", "heart.webp"))
cached_photo_path2 = types.FSInputFile(os.path.join("img", "i.webp"))
cached_photo_path3 = types.FSInputFile(os.path.join("img", "КМН.jpg"))
cached_photo_path4 = types.FSInputFile(os.path.join("img", "6195669.jpg"))
cached_photo_path5 = types.FSInputFile(os.path.join("img", "5711954.jpg"))
cached_photo_path6 = types.FSInputFile(os.path.join("img", "61867.jpg"))
cached_photo_path7 = types.FSInputFile(os.path.join("img", "11698.jpg"))
cached_photo_path8 = types.FSInputFile(os.path.join("img/default", "play_game_default.jpg"))
cached_photo_path9 = types.FSInputFile(os.path.join("img", "tours1.jpg"))
cached_photo_path10 = types.FSInputFile(os.path.join("img", "table_leaders.jpg"))
cached_photo_path11 = types.FSInputFile(os.path.join("img", "menu_back.jpg"))
cached_photo_path12 = types.FSInputFile(os.path.join("img", "matches.jpg")) 
cached_photo_path13 = types.FSInputFile(os.path.join("img", "tours3.jpg"))
cached_photo_path14 = types.FSInputFile(os.path.join("img", "statistic.jpg"))
cached_photo_path15 = types.FSInputFile(os.path.join("img", "main_chest.jpg"))
cached_photo_path16 = types.FSInputFile(os.path.join("img", "statistic2.jpg"))
cached_photo_path17 = types.FSInputFile(os.path.join("img", "bj.jpg"))
cached_photo_path18 = types.FSInputFile(os.path.join("img", "shop.jpg"))
cached_photo_path19 = types.FSInputFile(os.path.join("img/default", "trophy_default.jpg"))
cached_photo_path20 = types.FSInputFile(os.path.join("img/premium", "penalty_premium.jpg"))
cached_photo_path21 = types.FSInputFile(os.path.join("img/premium", "kmn_premium.jpg"))
cached_photo_path22 = types.FSInputFile(os.path.join("img/default", "21_default.jpg"))
cached_photo_path23 = types.FSInputFile(os.path.join("img/premium", "chest_premium.jpg"))
cached_photo_path24 = types.FSInputFile(os.path.join("img/premium", "games_premium.jpg"))
cached_photo_path25 = types.FSInputFile(os.path.join("img/default", "statistic_default.jpg"))
cached_photo_path26 = types.FSInputFile(os.path.join("img/premium", "play_game_premium.jpg"))
man = types.FSInputFile(os.path.join("img", "men.png"))



# функция для фонового добавления пользователя
async def add_user_in_background(user_id: int, username: str, join_date: datetime):
    await add_user(user_id, username, join_date)


@player_router.message(Command("start"))
async def start(message: Message):
    start_time = time.time()
    # Проверяем, что команда вызвана в личном чате
    if message.chat.type != "private":
        # Отправляем временное уведомление о недоступности команды в группе
        await message.reply("Эта команда доступна только в личных сообщениях с ботом.🔒", reply=False)
        return

    user_id = message.from_user.id
    username = message.from_user.username
    join_date = datetime.now()
    asyncio.create_task(add_user_in_background(user_id, username, join_date))
    await init_player_statistics(user_id)
    await add_shop(user_id)

    await message.answer_photo(
        photo=cached_photo_path4,
        caption=(
            f'<b>Привет {username}</b>!\n'
            '<b>Добро пожаловать в (Название бота)</b> 👋\n\n'
            'Здесь ты сможешь погрузиться в интересные игры, такие как "Цуефа 🪨✂️🧻", "Пенальти ⚽", соревноваться с другими игроками и друзьями и повышать свое место в таблице лидеров.\n\n'
            '🏆 Также визитной карточкой нашего бота являются турниры, где победитель получит приятный денежный приз!\n\n'
            'Правила игры и другую интересующую информацию можно найти в разделе <b>"О боте 🔎"</b>\n\n'
            'Также <b>"Перейди в сообщество 🔗"</b> чтобы не пропускать важные события\n\n'
            'Чтобы начать игру нажми <b>"Старт 🚀"</b>\n\n'
        ),
        reply_markup=main_keyboard,
        parse_mode='HTML'
    )
    end_time = time.time()
    print(f"Время срабатывания команды старт: {end_time - start_time:.2f} секунд ")

   


   
@player_router.callback_query(lambda c: c.data == "info_back")
async def bot_info_back(callback_query: CallbackQuery):
    username = callback_query.from_user.username

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path4,
            caption=(
            f'<b>Привет {username}</b>!\n'
            '<b>Добро пожаловать в (Название бота)</b> 👋\n\n'
            'Здесь ты сможешь погрузитья в интересные игры, такие как "Цуефа 🪨✂️🧻", "Пенальти ⚽", соревноваться с другими игроками и друзьями и повышать свое место в таблице лидеров.\n\n'
            '🏆 Также визитной карточкой нашего бота являютя турниры, где победитель получит приятный денежный приз!\n\n'
            'Правила игры и другую интересующую информацию можно найти в разделе <b>"О боте 🔎"</b>\n\n'
            'Также <b>"Перейти в сообщество 🔗"</b> чтобы не пропускать важные события\n\n'
            'Чтобы начать игру нажми <b>"Старт 🚀"</b>\n\n'
            ),
            parse_mode='HTML'
        ),
        reply_markup=main_keyboard
    )
    
@player_router.callback_query(lambda c: c.data == "start")
async def bot_start(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    request_role = await check_user_role(user_id)
    premium_design = await check_player_design(user_id)
    current_keyboard = []
    player_role = [role["role"] for role in request_role][0]
    print(player_role)
    if player_role == 'premium':
        await buy_premium_or_check_end_date(user_id=user_id, type_change='update')
    # Существующие кнопки
    if player_role == 'player':
        current_keyboard = start_keyboard
    else:
        if premium_design: current_keyboard = start_keyboard_premium
        else: current_keyboard = start_keyboard_standart

    # Создание новой клавиатуры

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path6,
            caption="\n\n<b>Меню 📌</b>\n\n",
            parse_mode='HTML'
        ),
        reply_markup=current_keyboard
    )

@player_router.callback_query(lambda c: c.data == "premium_design")
async def bot_start(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await change_user_design(user_id=user_id)
    premium_design = await check_player_design(user_id)
    print(premium_design)
    # Существующие кнопки


    # Создание новой клавиатуры

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path6,
            caption="\n\n<b>Меню 📌</b>\n\n",
            parse_mode='HTML'
        ),
        reply_markup=start_keyboard_premium if premium_design else start_keyboard_standart
    )
   

@player_router.callback_query(lambda c: c.data == "profile_back")
async def bot_start(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    # await change_user_design(user_id=user_id)
    premium_design = await check_player_design(user_id)
    request_role = await check_user_role(user_id)
    current_keyboard = []
    player_role = [role["role"] for role in request_role][0]
    print(premium_design)
    if player_role == 'player':
        current_keyboard = start_keyboard
    else:
        if premium_design: current_keyboard = start_keyboard_premium
        else: current_keyboard = start_keyboard_standart
    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path6,
            caption="\n\n<b>Меню 📌</b>\n\n",
            parse_mode='HTML'
        ),
        reply_markup=current_keyboard
    )
   
    

@player_router.callback_query(lambda c: c.data=="start_match")
async def select_game(callback_query: CallbackQuery):

    user_id = callback_query.from_user.id
    player_role = await check_player_design(user_id)

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path8 if not player_role else cached_photo_path26,
            caption=f"\n\nВыбери игру\n\n"
        ),
        reply_markup=play_keyboard
    )

@player_router.callback_query(lambda c: c.data == 'start_match_back')
async def end_ls_game_state(callback_query : CallbackQuery, state: FSMContext):
    await callback_query.message.answer_photo(
    photo=cached_photo_path8,
    caption=f"Выбери игру",
    reply_markup=play_keyboard
    )
    await state.clear()
    print('выход из состояния(кнопка назад)')

@player_router.callback_query(lambda c: c.data=="start_tournaments")
async def start_reg_on_tour(callback_query: CallbackQuery):
    start_time  = time.time()
    user_id = callback_query.from_user.id

    player_role = await check_player_design(user_id)

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path9 if player_role else cached_photo_path19,
            caption="Предыдущие победители:\n"
            " ◦ Игрок 1\n"
            " ◦ Игрок 2\n"
            " ◦ Игрок 3\n\n"
            "Информация о турнире:\n"
            " • 1 место: 500₽\n"
            " • 2 место: 100₽\n"
            " • 3 место: 50₽\n\n"
            "Турнир проводится каждое воскресенье в ХХ:00\n"
            "Регистрация закрывается за час"
        ), 
        reply_markup=tour_keyboard
    )
    end_time = time.time()
    print(f"Время срабатывания кнопки турниры: {end_time - start_time:.2f} секунд ")
    

