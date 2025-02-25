import os
from aiogram import Router, types, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, UserProfilePhotos
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext 
from keyboards import main_keyboard, info_keyboard, start_keyboard, profile_keyboard, play_keyboard, tour_keyboard, leadboards_keyboard,info_cuefa_keyboard, history_of_matches_keyboard, extended_static_keyboard, leadboards_season_back_keyboards, leadboards_season_3_back_keyboards, history_of_matches_back_keyboard, shop_keyboard
from db import get_db_connection
from datetime import datetime
from db_moves.add_db import add_user, make_buy, update_days_for_user, init_player_statistics, add_shop, update_user_coins
from db_moves.get_db import check_chop_el, display_main_leaderboard, display_main_statistics, display_penalty_cuefa_leaderboard, display_total_days, get_player_shop, get_user_coins
import time
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
cached_photo_path8 = types.FSInputFile(os.path.join("img", "all_games.jpg"))
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
    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path6,
            caption="\n\n<b>Меню 📌</b>\n\n",
            parse_mode='HTML'
        ),
        reply_markup=start_keyboard
    )
   

@player_router.callback_query(lambda c: c.data == "profile_back")
async def bot_start(callback_query: CallbackQuery):

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path6,
            caption="\n\n<b>Меню 📌</b>\n\n",
            parse_mode='HTML'
        ),
        reply_markup=start_keyboard
    )
   
    

@player_router.callback_query(lambda c: c.data=="start_match")
async def select_game(callback_query: CallbackQuery):

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path8,
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

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path9,
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
    

