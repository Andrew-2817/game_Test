from db_moves.get_db import check_user_role
from hendlers.ls.player  import player_router, cached_photo_path3, cached_photo_path5, cached_photo_path12, cached_photo_path13,  info_cuefa_keyboard, cached_photo_path20, cached_photo_path21, cached_photo_path24, cached_photo_path19
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import types
import os
from keyboards import info_keyboard
import time




#ЗДЕСЬ ФОТО НЕ НУЖНО
@player_router.callback_query(lambda c: c.data == "info")
async def bot_info(callback_query: CallbackQuery):

    await callback_query.message.delete()
    # Отправляем ответ
    new_message = await callback_query.message.answer(
        text=f"Здесь ты можешь узнать всю информацию о боте и правила игры 👇\n\n",
        parse_mode="HTML",
        reply_markup=info_keyboard
    )

@player_router.callback_query(lambda c : c.data=="info_RPS") 
async def bot_info_RPS(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    request_role = await check_user_role(user_id)
    player_role = [role["role"] for role in request_role][0] 
 
    await callback_query.message.edit_media( 
        media=InputMediaPhoto( 
            media=cached_photo_path3 if player_role == 'player' else cached_photo_path21, 
            caption="<b>Игра Цуефа 🪨✂️🧻</b>\n\n" 
            "Это всем знакомая игра, где ты играешь против другого игрока и тебе нужно выбрать один из трех вариантов: камень🪨 ножницы✂️ или бумага🧻\n\n" 
            "Ты побеждаешь при следующих раскладах:\n" 
            "Твой ход:🪨 Ход соперника:✂️\n" 
            "Твой ход:✂️ Ход соперника:🧻\n" 
            "Твой ход:🧻 Ход соперника:🪨\n\n" 
            "При одинаковом выборе - ничья\n\n" 
            "Чтобы начать игру нужно:\n"
            "Зайти в |игровой чат|\n" 
            "Ознакомиться с инструкцией в закрепленном сообщении\n\n" 
            "Желаем Удачи!", 
            parse_mode='HTML'
        ),  
        reply_markup=info_cuefa_keyboard 
    ) 

@player_router.callback_query(lambda c : c.data=="info_footbal") 
async def bot_info_football(callback_query: CallbackQuery): 
    start_time = time.time()
    user_id = callback_query.from_user.id
    request_role = await check_user_role(user_id)
    player_role = [role["role"] for role in request_role][0] 
 
    await callback_query.message.edit_media( 
        media=InputMediaPhoto( 
            media=cached_photo_path5 if player_role == 'player' else cached_photo_path20, 
            caption="<b>Игра Пенальти⚽</b>\n\n" 
            "Игра для всех любителей футбола. Правила предельно просты: тебе нужно выбрать одну из цифр - 1, 2, или 3, то есть угол, куда ты будешь бить\n" 
            "Твой соперник(Вратарь) должен угадать угол\n" 
            "Если ты забиваешь гол - получаешь очко, иначе его получает твой соперник\n\n" 
            "Чтобы начать игру нужно:\n" 
            "Зайти в |игровой чат|\n" 
            "Ознакомиться с инструкцией в закрепленном сообщении\n\n" 
            "Желаем Удачи!", 
            parse_mode='HTML' 
        ),  
        reply_markup=info_cuefa_keyboard 
    ) 
    end_time = time.time() 
    print(f"Время срабатывания кнопки Инфо->Подробнее: {end_time - start_time:.2f} секунд ")


@player_router.callback_query(lambda c : c.data=="info_match") 
async def bot_info_match(callback_query: CallbackQuery): 
    start_time = time.time()
    user_id = callback_query.from_user.id
    request_role = await check_user_role(user_id)
    player_role = [role["role"] for role in request_role][0] 
 
    await callback_query.message.edit_media( 
        media=InputMediaPhoto( 
            media=cached_photo_path12 if player_role == 'player' else cached_photo_path24, 
            caption="<b>Как проходят матчи</b>\n\n" 
            "Чтобы начать матч, тебе нужно перейти в |игровой чат| и ввести подходящую коману в зависимрсти от того, в какую игру ты хочешь сыграть\n" 
            "После создается приглашение для других участников на |1 минуту|\n" 
            "Как только нашелся оппонент, игра начинается!\n\n" 
            "В закрепленном сообщении в чате ты можешь ознакомиться с более подробной информацией", 
            parse_mode='HTML' 
        ),  
        reply_markup=info_cuefa_keyboard 
    ) 
    end_time = time.time() 
    print(f"Время срабатывания кнопки Инфо->Подробнее: {end_time - start_time:.2f} секунд ") 


@player_router.callback_query(lambda c : c.data=="info_tournaments") 
async def bot_info_tournaments(callback_query: CallbackQuery): 
    start_time = time.time()
    user_id = callback_query.from_user.id
    request_role = await check_user_role(user_id)
    player_role = [role["role"] for role in request_role][0] 
 
    await callback_query.message.edit_media( 
        media=InputMediaPhoto( 
            media=cached_photo_path13 if player_role == 'premium' else cached_photo_path19, 
            caption="<b>Турниры</b>\n\n" 
            "Турниры проходят раз в неделю по воскресеньям в ХХ:00\n" 
            "Формат турнира представлет собой сетку плей-офф(игра на вылет): если побеждаешь, то проходишь дальше, если проигрываешь, то вылетаешь\n" 
            "В каждом раунде участники играют до 3-х побед, а в финале до 5 побед\n" 
            "При этом разновидность игры в каждом матче определяется случайно\n\n" 
            "Чтобы зарегистрироваться, перейди в канал |Турниры|\n\n" 
            "Призовой фонд:\n" 
            " • 1 место: 500₽\n" 
            " • 2 место: 100₽\n" 
            " • 3 место: 50₽\n\n" 
            "Ждём тебя на турнирах!", 
            parse_mode='HTML' 
        ),  
        reply_markup=info_cuefa_keyboard 
    ) 
    end_time = time.time() 
    print(f"Время срабатывания кнопки Инфо->Подробнее: {end_time - start_time:.2f} секунд ")