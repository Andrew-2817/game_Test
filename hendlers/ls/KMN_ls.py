from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from hendlers.ls.player import player_router, cached_photo_path5
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext 
from db import get_db_connection
from aiogram import types 
import os 
from keyboards import attack_buttons_KMN_ls, defense_buttons_KMN_ls, game_ls_back_keyboard
import asyncio

cached_photo_path3 = types.FSInputFile(os.path.join("img", "КМН.jpg"))
cached_photo_path5 = types.FSInputFile(os.path.join("img", "tours2.jpg"))
cached_photo_path6 = types.FSInputFile(os.path.join("img", "kmn_play.jpg"))
cached_photo_path7 = types.FSInputFile(os.path.join("img", "kmn_waiting.jpg"))


# Словарь для хранения активных таймеров
active_timers = {}
emojis = {"kamen": "🪨", "bumaga": "📃", "nognichi": "✂️", "none": "❌"}
choices = {
    "kamen": {"bumaga": "проиграл", "nognichi": "победил", "kamen": 'ничья', "none": "победил"},
    "bumaga": {"nognichi": "проиграл", "kamen": "победил", "bumaga": "ничья", "none": "победил"},
    "nognichi": {"kamen": "проиграл", "bumaga": "победил", "nognichi": "ничья", "none": "победил"},
    "none": {"kamen": "проиграл", "bumaga": "проиграл", "nognichi": "проиграл"}
}


# Функция для сброса таймера для игрока
async def reset_timer(player_id):
    if player_id in active_timers:
        active_timers[player_id].cancel()  
        del active_timers[player_id]  



async def start_turn_timer(game, callback_query, player_id, timeout=15):
    await reset_timer(player_id)

    async def countdown():
        for remaining in range(timeout, 0, -1):
            print(f"Оставшееся время для игрока {player_id}: {remaining} секунд")
            await asyncio.sleep(1)

        # Найти игру по ID игрока
        game = next(
            (g for g in ongoing_games.values() if player_id in (g["current_attacker"], g["current_defender"])),
            None
        )
        if game:
            if game["state"] == "waiting_for_attack" and game["current_attacker"] == player_id:
                print(f"Игрок {player_id} не успели сделать ход")
                game['history'][game["current_attacker"]]+='❌'
                # game['round']+=1
                await callback_query.bot.send_message(
                    chat_id=player_id, text="Вы не успели сделать ход!"
                )
                # Передаем ход
                await end_round(game, callback_query)


            elif game["state"] == "waiting_for_defense" and game["current_defender"] == player_id:
                print(f"Игрок {player_id} не успели сделать ход")
                await callback_query.bot.send_message(
                    chat_id=player_id, text="Вы не успели сделать ход!"
                )
                # гол напу за ожидание
                game['history'][game["current_defender"]]+='❌'
                print(game["history"][game['current_attacker']][-1])
                if game["history"][game['current_attacker']][-1] != '❌': 
                    game["scores"][game["current_attacker"]] += 1
                # Завершаем раунд
                await end_round(game, callback_query)

            else:
                await callback_query.bot.send_message(
                    chat_id=player_id, text="Неизвестное состояние игры. Попробуйте снова."
                )
        else:
            await callback_query.bot.send_message(
                chat_id=player_id, text="Игра не найдена или уже завершена."
            )

    task = asyncio.create_task(countdown())
    active_timers[player_id] = task


# Функция для завершения раунда и перехода к следующему
async def end_round(game, callback_query):
    if game["round"] < 10 or (game["round"] < 16 and game["scores"][game["attacker"]] == game["scores"][game["defender"]]):
        # Переход к следующему раунду
        # game["round"] += 1
        # Меняем роли игроков
        if game["history"][game['current_attacker']][-1] == '❌':
            print('велесо')
            game["attack"] = 'none'
            game["state"] = "waiting_for_defense"
            await callback_query.bot.edit_message_media(
            chat_id=game['current_attacker'],
            message_id=game["messages"][game['current_attacker']],
            media=types.InputMediaPhoto(
                media=cached_photo_path7,
                caption=f"Вы сделали ход. Ожидайте противника",
            ),
            )

            # Обновляем сообщение защитника
            await callback_query.bot.edit_message_media(
                chat_id=game["current_defender"],
                message_id=game["messages"][game["current_defender"]],
                media=types.InputMediaPhoto(
                    media=cached_photo_path6,
                    caption=f"Счёт: \n<b>{game['usernames'][game['attacker']]}</b> {game['scores'][game['attacker']]} - {game['scores'][game['defender']]} <b>{game['usernames'][game['defender']]}</b>\n\n"
                    # f"История ударов\n"
                    # f"<b>{game['usernames'][game['attacker']]}</b>: {game['history'][game['attacker']]}\n"
                    # f"<b>{game['usernames'][game['defender']]}</b>: {game['history'][game['defender']]}\n\n"
                    f"Сделайте ход!",
                    parse_mode='HTML',
                ),
                reply_markup=defense_buttons_KMN_ls,
            )
            game['round']+=1
            # Запускаем таймер для защитника
            await start_turn_timer(game, callback_query, game["current_defender"])
        else:  

            game["current_attacker"], game["current_defender"] = game["current_defender"], game["current_attacker"]
            # game["current_attacker"], game["current_defender"] = game["current_defender"], game["current_attacker"]
            game["round"]+=1
            # Обновляем состояние игры
            game["state"] = "waiting_for_attack"
            game.pop("attack_locked", None)
            game.pop("defense_locked", None)


            await callback_query.bot.delete_message(chat_id=game["attacker"], message_id=game["messages"][game["attacker"]])
            await callback_query.bot.delete_message(chat_id=game["defender"], message_id=game["messages"][game["defender"]])
            # Отправляем новые сообщения
            next_attacker_id = game["current_attacker"]
            attack_message = await callback_query.bot.send_photo(
                chat_id=next_attacker_id,
                photo=cached_photo_path6,
                caption=
                f"Счёт:\n"
                f"<b>{game['usernames'][game['attacker']]}</b>: {game['scores'][game['attacker']]}\n"
                f"<b>{game['usernames'][game['defender']]}</b>: {game['scores'][game['defender']]}\n\n"
                f"История ударов\n"
                f"<b>{game['usernames'][game['attacker']]}</b>: {game['history'][game['attacker']]}\n"
                f"<b>{game['usernames'][game['defender']]}</b>: {game['history'][game['defender']]}\n\n"
                "Сделайте ход!",
                parse_mode = "HTML",
                reply_markup=attack_buttons_KMN_ls,
            )
            game["messages"][next_attacker_id] = attack_message.message_id

            # Уведомляем защитника ожидать
            defender_wait_message = await callback_query.bot.send_photo(
                chat_id=game["current_defender"],
                photo=cached_photo_path7,
                caption="Ожидайте, пока противник сделает ход 🪨✂️📃",
            )
            game["messages"][game["current_defender"]] = defender_wait_message.message_id

            # Запускаем таймер для атакующего
            await start_turn_timer(game, callback_query, next_attacker_id)
    elif (game["round"] >= 10 and game["scores"][game["attacker"]] != game["scores"][game["defender"]]) and game['round']<16 or (game["round"] == 16 and game["scores"][game["attacker"]] == game["scores"][game["defender"]]):
        print("01111111111111111111111111111111111111111111111111111111111111111111111")
        result_message = (
            f"Игра завершена!\n"
            
        )
        result_message += (
            f"🎉 Победил <b>{game['usernames'][game['attacker']]}!</b>\n\n" if game["scores"][game['attacker']] > game["scores"][game['defender']]
            else f"🎉 Победил <b>{game['usernames'][game['defender']]}!</b>\n" if game["scores"][game['attacker']] < game["scores"][game['defender']]
            else "🤝 Ничья!\n"
        )
        result_message += (
            f"Счёт:\n"
            f"<b>{game['usernames'][game['attacker']]}</b>: {game['scores'][game['attacker']]}\n"
            f"<b>{game['usernames'][game['defender']]}</b>: {game['scores'][game['defender']]}\n\n"
            f"История ударов\n"
            f"<b>{game['usernames'][game['attacker']]}</b>: {game['history'][game['attacker']]}\n"
            f"<b>{game['usernames'][game['defender']]}</b>: {game['history'][game['defender']]}\n"
        )
        for player_id in [game["attacker"], game["defender"]]:
            await callback_query.bot.send_photo(
                chat_id=player_id,
                photo = cached_photo_path6,
                caption=result_message,
                parse_mode='HTML'
            )

        # Удаляем игру
        ongoing_games.pop(game["attacker"], None)

        
# Класс для отслеживания состояния
class KMN(StatesGroup):
    waiting_for_message = State()

# Обработчик нажатия кнопки "profile_penality"
@player_router.callback_query(lambda c: c.data == "profile_RPS")
async def ls_penki(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    print('fffff')
    # Когда выбрали игру входим в сосотояние
    await state.set_state(KMN.waiting_for_message)
    # Проверка: если боец в игре то не даем ему вызовами кидаться
    # ВОТ ЭТО КОМЕНТИТЬ И СМОЖЕШЬ ИГРАТЬ
    if any(user_id in (game["attacker"], game["defender"]) for game in ongoing_games.values()):
        await callback_query.message.answer("Вы уже участвуете в игре! Завершите текущую игру, чтобы начать новую.")
        return

    await callback_query.message.answer(
        text = "Напишите юзернейм противника:",
        reply_markup=game_ls_back_keyboard
        )

    @player_router.message(KMN.waiting_for_message)
    async def check_username(message: Message):
        opponent_username = message.text.strip("@")
        conn = await get_db_connection()
        try:
            # Ищем ID пользователя по введённому username
            query = "SELECT user_id FROM users WHERE username = $1"
            opponent_id = await conn.fetchval(query, opponent_username)

            if opponent_id:
                # Проверка: если противник уже в игре, не разрешаем начать с ним игру
                # ТОЖЕ НА КОМЕНТ 
                if any(opponent_id in (game["attacker"], game["defender"]) for game in ongoing_games.values()):
                    await message.answer(f"Пользователь @{opponent_username} уже участвует в игре. Попробуйте позже.")
                    return

                # Кнопка "Принять вызов"
                KMN_accept_keyboard_ls = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Принять вызов",
                            callback_data=f"accept_KMN_ls:{user_id}"
                        )
                    ]
                ])

                # Отправляем вызов пользователю 
                await message.bot.send_photo(
                    chat_id=opponent_id,
                    photo=cached_photo_path3,
                    caption=f"<b>Игрок @{callback_query.from_user.username}</b> вызывает вас на дуэль в <i>Цуефа!🪨✂️📃</i>\n\n"
                            "Нажмите <b>Принять вызов</b>, чтобы присоединиться!",
                    parse_mode="HTML",
                    reply_markup=KMN_accept_keyboard_ls,
                )
                await message.answer(f"Вызов отправлен пользователю @{opponent_username}!")
            else:
                await message.answer("Такой пользователь не найден в системе!")
        finally:
            await conn.close()

        # Выходим из состояния
        await state.clear()
        print('выход из состояния(дефолтное)')

ongoing_games = {}

# Обработчик нажатия кнопки "Принять вызов"
@player_router.callback_query(lambda c: c.data.startswith("accept_KMN_ls"))
async def accept_penalty(callback_query: CallbackQuery):
    initiator_id = int(callback_query.data.split(":")[1])
    defender_id = callback_query.from_user.id

    # Проверка: если любой из игроков уже в игре, отменяем создание новой игры
    # B ЭТО ТОЖЕ КОМЕНТ
    if any(initiator_id in (game["attacker"], game["defender"]) or defender_id in (game["attacker"], game["defender"]) for game in ongoing_games.values()):
        await callback_query.answer("Один из игроков уже участвует в игре! Завершите текущую игру, чтобы начать новую.")
        return

    # Получаем юзернеймы
    initiator_chat = await callback_query.bot.get_chat(initiator_id)
    initiator_username = initiator_chat.username or f"Игрок {initiator_id}"

    defender_chat = callback_query.from_user
    defender_username = defender_chat.username or f"Игрок {defender_id}"

    # Инициализация игры
    ongoing_games[initiator_id] = {
        "attacker": initiator_id,
        "defender": defender_id,
        "round": 1,
        "scores": {initiator_id: 0, defender_id: 0},
        "state": "waiting_for_attack",
        "current_attacker": initiator_id,
        "current_defender": defender_id,
        "history": {initiator_id: '', defender_id: ''},
        "messages": {},  # Для хранения ID сообщений
        "usernames": {initiator_id: initiator_username, defender_id: defender_username},  # Юзернеймы игроков
    }

    game = ongoing_games[initiator_id]
    print(game)
    # Начало игры: отправляем одно сообщение каждому игроку
    attack_message = await callback_query.bot.send_photo(
        chat_id=initiator_id,
        photo=cached_photo_path6,
        caption=f"Вы ходите первым!\n Счёт: \n<b>{game['usernames'][initiator_id]}</b> {game['scores'][initiator_id]} - {game['scores'][defender_id]} <b>{game['usernames'][defender_id]}</b>\n\n"
        "Сделайте ход!",
        parse_mode='HTML',
        reply_markup=attack_buttons_KMN_ls,
    )
    wait_message = await callback_query.bot.send_photo(
        chat_id=defender_id,
        photo=cached_photo_path7,
        parse_mode='HTML',
        caption=f"Счёт: \n<b>{game['usernames'][game['attacker']]}</b> {game['scores'][game['attacker']]} - {game['scores'][game['defender']]} <b>{game['usernames'][game['defender']]}</b>\n"
        "Ожидайте, пока противник сделает ход 🪨✂️📃",
    )

    # Сохраняем ID сообщений
    game["messages"][initiator_id] = attack_message.message_id
    game["messages"][defender_id] = wait_message.message_id

    # Запускаем таймер для атакующего
    await start_turn_timer(game, callback_query, initiator_id)


# Обработчик атаки
@player_router.callback_query(lambda c: c.data.startswith("KMNA_"))
async def handle_attack(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    game = next((g for g in ongoing_games.values() if g.get("current_attacker") == user_id), None)
    print(ongoing_games.values())
    if not game or game["state"] != "waiting_for_attack":
        await callback_query.answer("Это не ваш ход!")
        return

    # Сброс таймера перед атакой
    await reset_timer(user_id)

    # Защита от Елисеев
    if "attack_locked" in game and game["attack_locked"]:
        await callback_query.answer("Вы уже сделали ход!")
        return

    game["attack_locked"] = True
    attack_direction = callback_query.data.split("_")[1]
    game["attack"] = attack_direction
    game["state"] = "waiting_for_defense"
    game['history'][user_id]+=emojis[attack_direction]

    # Обновляем сообщение атакующего
    await callback_query.bot.edit_message_media(
        chat_id=user_id,
        message_id=game["messages"][user_id],
        media=types.InputMediaPhoto(
            media=cached_photo_path7,
            caption=f"Вы сделали ход. Ожидайте противника",
        ),
    )

    # Обновляем сообщение защитника
    await callback_query.bot.edit_message_media(
        chat_id=game["current_defender"],
        message_id=game["messages"][game["current_defender"]],
        media=types.InputMediaPhoto(
            media=cached_photo_path6,
            caption=f"Счёт: \n<b>{game['usernames'][game['attacker']]}</b> {game['scores'][game['attacker']]} - {game['scores'][game['defender']]} <b>{game['usernames'][game['defender']]}</b>\n\n"
            # f"История ударов\n"
            # f"<b>{game['usernames'][game['attacker']]}</b>: {game['history'][game['attacker']]}\n"
            # f"<b>{game['usernames'][game['defender']]}</b>: {game['history'][game['defender']]}\n\n"
            f"Сделайте ход!",
            parse_mode='HTML',
        ),
        reply_markup=defense_buttons_KMN_ls,
    )
    game['round']+=1
    # Запускаем таймер для защитника
    await start_turn_timer(game, callback_query, game["current_defender"])

@player_router.callback_query(lambda c: c.data.startswith("KMND_"))
async def handle_defense(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    game = next((g for g in ongoing_games.values() if g.get("current_defender") == user_id), None)

    if not game or game["state"] != "waiting_for_defense":
        await callback_query.answer("Это не ваш ход!")
        return

    # Сброс таймера перед защитой
    await reset_timer(user_id)

    # Блокировка повторных нажатий
    if "defense_locked" in game and game["defense_locked"]:
        await callback_query.answer("Вы уже выбрали направление защиты!")
        return

    game["defense_locked"] = True
    defense_direction = callback_query.data.split("_")[1]
    attack_direction = game["attack"]
    attacker_id = game["current_attacker"]
    defender_id = game["current_defender"]
    print(game)
    
    game['history'][defender_id]+=emojis[defense_direction]
    # Определяем результат удара
    # if attack_direction == defense_direction:
    #     result = "Удар отбит! Отличная защита! 🧤"
    # else:
    #     result = "Вы не смогли защититься! ⚽"
    #     game["scores"][attacker_id] += 1
    if choices[attack_direction][defense_direction]=='победил':
        game["scores"][attacker_id] +=1
    if choices[defense_direction][attack_direction]=='победил' or game["history"][attacker_id][-1] =='❌':
        game["scores"][defender_id] +=1

    # Уведомляем игроков о результате
    attacker_message = (
        f"\n\nСчёт: {game['usernames'][attacker_id]} {game['scores'][attacker_id]} - "
        f"{game['scores'][defender_id]} {game['usernames'][defender_id]}\n\n"
    )
    defender_message = (
        f"\n\nСчёт: {game['usernames'][attacker_id]} {game['scores'][attacker_id]} - "
        f"{game['scores'][defender_id]} {game['usernames'][defender_id]}"
    )

    # Удаляем сообщения игроков
    await callback_query.bot.delete_message(chat_id=attacker_id, message_id=game["messages"][attacker_id])
    await callback_query.bot.delete_message(chat_id=defender_id, message_id=game["messages"][defender_id])

    # Проверка на завершение игры
    if game["round"] < 10 or (game["round"] < 16 and game["scores"][game["attacker"]] == game["scores"][game["defender"]]):
        # Переключение ролей
        game["round"] += 1
        game["current_attacker"], game["current_defender"] = game["current_defender"], game["current_attacker"]
        game["state"] = "waiting_for_attack"
        game.pop("attack_locked", None)
        game.pop("defense_locked", None)

        # Новое сообщение для следующего атакующего
        next_attacker_id = game["current_attacker"]
        attack_message = await callback_query.bot.send_photo(
            chat_id=next_attacker_id,
            photo=cached_photo_path6,
            caption=f"Счёт: \n<b>{game['usernames'][game['attacker']]}</b> {game['scores'][game['attacker']]} - {game['scores'][game['defender']]} <b>{game['usernames'][game['defender']]}</b>\n\n"
            f"История ударов\n"
            f"<b>{game['usernames'][game['attacker']]}</b>: {game['history'][game['attacker']]}\n"
            f"<b>{game['usernames'][game['defender']]}</b>: {game['history'][game['defender']]}\n\n"
            f"Сделайте ход!",
            parse_mode='HTML',
            reply_markup=attack_buttons_KMN_ls,
        )
        game["messages"][next_attacker_id] = attack_message.message_id

        # Уведомляем защитника ожидать
        defender_wait_message = await callback_query.bot.send_photo(
            chat_id=game["current_defender"],
            photo=cached_photo_path7,
            caption="Ожидайте, пока противник сделает ход 🪨✂️📃\n",
        )
        game["messages"][game["current_defender"]] = defender_wait_message.message_id

        # Запускаем таймер для атакующего
        await start_turn_timer(game, callback_query, next_attacker_id)
    else:
        # Завершение игры
        result_message = (
            f"Игра завершена!\n"
            
        )
        result_message += (
            f"🎉 Победил <b>{game['usernames'][game['attacker']]}!</b>\n\n" if game["scores"][game['attacker']] > game["scores"][game['defender']]
            else f"🎉 Победил <b>{game['usernames'][game['defender']]}!</b>\n" if game["scores"][game['attacker']] < game["scores"][game['defender']]
            else "🤝 Ничья!\n"
        )
        result_message += (
            f"Счёт:\n"
            f"<b>{game['usernames'][game['attacker']]}</b>: {game['scores'][game['attacker']]}\n"
            f"<b>{game['usernames'][game['defender']]}</b>: {game['scores'][game['defender']]}\n\n"
            f"История ударов\n"
            f"<b>{game['usernames'][game['attacker']]}</b>: {game['history'][game['attacker']]}\n"
            f"<b>{game['usernames'][game['defender']]}</b>: {game['history'][game['defender']]}\n"
        )
        for player_id in [game["attacker"], game["defender"]]:
            await callback_query.bot.send_photo(
                chat_id=player_id,
                photo = cached_photo_path5,
                caption=result_message,
                parse_mode='HTML'
            )

        # Удаляем игру
        ongoing_games.pop(game["attacker"], None)
