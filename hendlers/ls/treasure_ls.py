from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext 
from db_moves.get_db import check_player_design, check_user_el_in_game, check_user_role
from db_moves.add_db import use_el_in_game
from hendlers.ls.player import player_router, cached_photo_path8, cached_photo_path23
from aiogram.filters import Command
from db import get_db_connection
from aiogram import types 
import os 
from keyboards import attack_buttons_treasures_ls,  defense_buttons_treasures_ls, test_button, buy_button, game_ls_back_keyboard, play_keyboard
import asyncio

cached_photo_path5 = types.FSInputFile(os.path.join("img", "main_chest.jpg"))
cached_photo_path6 = types.FSInputFile(os.path.join("img", "tours2.jpg"))
cached_photo_path3 = types.FSInputFile(os.path.join("img", "chest1.jpg"))
cached_photo_path7 = types.FSInputFile(os.path.join("img", "chest2.jpg"))


# Словарь для хранения активных таймеров
active_timers = {}

you_can = False
help_history = []
help_penalty_text = []
supershot_plus = 0
supersave_plus = 0

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
                print(f"Игрок {player_id} не успел спрятать золото🟡.")
                # game['history'][player_id]+='🧤'
                game['history'][game["current_defender"]]+='💰'
                game["scores"][game["current_defender"]] += 1
                # game['round']+=1
                await callback_query.bot.send_message(
                    chat_id=player_id, text="Вы не успели выполнить атаку! Ход переходит к сопернику."
                )
                # Передаем ход
                await end_round(game, callback_query)

            elif game["state"] == "waiting_for_defense" and game["current_defender"] == player_id:
                print(f"Игрок {player_id} не успел выполнить защиту.")
                await callback_query.bot.send_message(
                    chat_id=player_id, text="Вы не успели выполнить защиту! Противник забивает гол!"
                )
                # гол напу за ожидание
                game['history'][game["current_defender"]]+='🔒'
                # game["scores"][game["current_attacker"]] += 1
                await callback_query.bot.send_message(
                    chat_id=game["current_attacker"], text="Вы забили гол!"
                )
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
    if game["round"] < 6 or (game["round"] < 10 and game["scores"][game["attacker"]] == game["scores"][game["defender"]]):
        # Переход к следующему раунду
        game["round"] += 1

        # Меняем роли игроков
        game["current_attacker"], game["current_defender"] = game["current_defender"], game["current_attacker"]

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
            photo=cached_photo_path3,
            caption=f"Теперь ваша очередь прятать\n\n"
            f"Счёт:\n"
            f"<b>{game['usernames'][game['attacker']]}</b>: {game['scores'][game['attacker']]}\n"
            f"<b>{game['usernames'][game['defender']]}</b>: {game['scores'][game['defender']]}\n\n"
            f"История ходов\n"
            f"<b>{game['usernames'][game['attacker']]}</b>: {game['history'][game['attacker']]}\n"
            f"<b>{game['usernames'][game['defender']]}</b>: {game['history'][game['defender']]}\n"
            "Выберите куда спрятать золото🟡",
            parse_mode = "HTML",
            reply_markup=attack_buttons_treasures_ls,
        )
        game["messages"][next_attacker_id] = attack_message.message_id

        # Уведомляем защитника ожидать
        defender_wait_message = await callback_query.bot.send_photo(
            chat_id=game["current_defender"],
            photo=cached_photo_path7,
            caption="Ожидайте, пока противник прячет золото🟡",
        )
        game["messages"][game["current_defender"]] = defender_wait_message.message_id

        # Запускаем таймер для атакующего
        await start_turn_timer(game, callback_query, next_attacker_id)
    elif (game["round"] >= 6 and game["scores"][game["attacker"]] != game["scores"][game["defender"]] and game['round']<10 and game['round']%2==0)  or (game["round"] == 10 and game["scores"][game["attacker"]] == game["scores"][game["defender"]]):
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
            f"История ходов\n"
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
class Treasure(StatesGroup):
    waiting_for_message = State()
        

# Обработчик нажатия кнопки "profile_treasures"
@player_router.callback_query(lambda c: c.data == "profile_treasures")
async def ls_treasures(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    player_role = await check_player_design(user_id=user_id)
    # Когда выбрали игру входим в сосотояние
    await state.set_state(Treasure.waiting_for_message)
    print('вход в сосотояние')
    # Проверка: если боец в игре то не даем ему вызовами кидаться
    # ВОТ ЭТО КОМЕНТИТЬ И СМОЖЕШЬ ИГРАТЬ
    if any(user_id in (game["attacker"], game["defender"]) for game in ongoing_games.values()):
        await callback_query.message.answer("Вы уже участвуете в игре! Завершите текущую игру, чтобы начать новую.")
        return
    await callback_query.message.answer(
        text = "Напишите юзернейм противника:",
        reply_markup=game_ls_back_keyboard
        )
    
    

    # если мы в состоянии, то этот обработчик сработает(начинаем катку или ввели неправильно юзернейм)
    # 
    @player_router.message(Treasure.waiting_for_message)
    async def check_username(message: Message, state: FSMContext):
        # if message.chat.type != 'private':
        #     return
        print(1345)
        opponent_username = message.text.strip("@")
        conn = await get_db_connection()
        try:
            # Ищем ID пользователя по введённому username
            query = "SELECT user_id FROM users WHERE username = $1"
            opponent_id = await conn.fetchval(query, opponent_username)
            player_design = await check_player_design(opponent_id)

            if opponent_id:
                # Проверка: если противник уже в игре, не разрешаем начать с ним игру
                # ТОЖЕ НА КОМЕНТ 
                if any(opponent_id in (game["attacker"], game["defender"]) for game in ongoing_games.values()):
                    await message.answer(f"Пользователь @{opponent_username} уже участвует в игре. Попробуйте позже.")
                    return

                # Кнопка "Принять вызов"
                treasures_accept_keyboard_ls = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="|Принять вызов|",
                            callback_data=f"accept_treasures_ls:{user_id}"
                        )
                    ]
                ])

                # Отправляем вызов пользователю 
                await message.bot.send_photo(
                    chat_id=opponent_id,
                    photo=cached_photo_path5 if not player_design else cached_photo_path23,
                    caption=f"<b>Игрок @{callback_query.from_user.username}</b> вызывает вас на дуэль в <i>Сокровища 💰🗝️!</i>\n\n"
                            "Нажмите <b>Принять вызов</b>, чтобы присоединиться!",
                    parse_mode="HTML",
                    reply_markup=treasures_accept_keyboard_ls,
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
@player_router.callback_query(lambda c: c.data.startswith("accept_treasures_ls"))
async def accept_treasures(callback_query: CallbackQuery):
    initiator_id = int(callback_query.data.split(":")[1])
    defender_id = callback_query.from_user.id

    # Проверка: если любой из игроков уже в игре, отменяем создание новой игры
    # B ЭТО ТОЖЕ КОМЕНТ
    if any(initiator_id in (game["attacker"], game["defender"]) or defender_id in (game["attacker"], game["defender"]) for game in ongoing_games.values()):
        await callback_query.answer("Один из игроков уже участвует в игре! Завершите текущую игру, чтобы начать новую.")
        return
    global help_history
    help_history = []
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
        photo=cached_photo_path3,
        caption=f"Вы ходите первым!\n Счёт: \n<b>{game['usernames'][initiator_id]}</b> {game['scores'][initiator_id]} - {game['scores'][defender_id]} <b>{game['usernames'][defender_id]}</b>\n"
        "Выберите куда спрятать золото🟡",
        parse_mode='HTML',
        reply_markup=attack_buttons_treasures_ls,
    )
    wait_message = await callback_query.bot.send_photo(
        chat_id=defender_id,
        photo=cached_photo_path7,
        parse_mode='HTML',
        caption=f"Счёт: \n<b>{game['usernames'][game['attacker']]}</b> {game['scores'][game['attacker']]} - {game['scores'][game['defender']]} <b>{game['usernames'][game['defender']]}</b>\n"
        "Ожидайте, пока противник прячет золото🟡",
    )

    # Сохраняем ID сообщений
    game["messages"][initiator_id] = attack_message.message_id
    game["messages"][defender_id] = wait_message.message_id

    # Запускаем таймер для атакующего
    await start_turn_timer(game, callback_query, initiator_id)


# Обработчик атаки
@player_router.callback_query(lambda c: c.data.startswith("treasuresA_"))
async def handle_attack(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    game = next((g for g in ongoing_games.values() if g.get("current_attacker") == user_id), None)
    help_penalty_text.clear()
    
    if not game or game["state"] != "waiting_for_attack":
        print('okkkkkkkkkkkkkkkkkk')
        await callback_query.answer("Это не ваш ход!")
        return

    # Сброс таймера перед атакой
    await reset_timer(user_id)

    # Защита от Елисеев
    if "attack_locked" in game and game["attack_locked"]:
        await callback_query.answer("Вы уже выбрали куда спрятать золото🟡!")
        return

    game["attack_locked"] = True
    attack_direction = callback_query.data.split("_")[1]
    game["attack"] = attack_direction
    game["state"] = "waiting_for_defense"

    global you_can
    you_can = True
    help_penalty_text.append(game["attack"])

    # Обновляем сообщение атакующего
    await callback_query.bot.edit_message_media(
        chat_id=user_id,
        message_id=game["messages"][user_id],
        media=types.InputMediaPhoto(
            media=cached_photo_path3,
            caption=f"Вы спрятали золото🟡. Ожидайте, пока противник сделает ход",
        ),
    )

    # Обновляем сообщение защитника
    await callback_query.bot.edit_message_media(
        chat_id=game["current_defender"],
        message_id=game["messages"][game["current_defender"]],
        media=types.InputMediaPhoto(
            media=cached_photo_path7,
            caption=f"Противник прячет! \nСчёт: \n<b>{game['usernames'][game['attacker']]}</b> {game['scores'][game['attacker']]} - {game['scores'][game['defender']]} <b>{game['usernames'][game['defender']]}</b>\n\n"
            f"История ходов\n"
            f"<b>{game['usernames'][game['attacker']]}</b>: {game['history'][game['attacker']]}\n"
            f"<b>{game['usernames'][game['defender']]}</b>: {game['history'][game['defender']]}\n"
            f"Угадайте где лежит золото🟡",
            parse_mode='HTML',
        ),
        reply_markup=defense_buttons_treasures_ls,
    )

    # Запускаем таймер для защитника
    await start_turn_timer(game, callback_query, game["current_defender"])

@player_router.callback_query(lambda c: c.data.startswith("treasuresD_"))
async def handle_defense(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    global supershot_plus
    global supersave_plus
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
    global you_can
    you_can = False
    # Определяем результат удара
    if attack_direction == defense_direction:
        result = "Вы угадали! Отличная работа! 💰"
        game["scores"][defender_id] += 1+supershot_plus
        game['history'][defender_id]+='💰'
    else:
        result = "Вы не угадали! 🔒"
        game['history'][defender_id]+='🔒'
        game["scores"][attacker_id] += supersave_plus

    # Уведомляем игроков о результате
    attacker_message = (
        f"{result}\n\nСчёт: {game['usernames'][attacker_id]} {game['scores'][attacker_id]} - "
        f"{game['scores'][defender_id]} {game['usernames'][defender_id]}\n\n"
    )
    defender_message = (
        f"{result}\n\nСчёт: {game['usernames'][attacker_id]} {game['scores'][attacker_id]} - "
        f"{game['scores'][defender_id]} {game['usernames'][defender_id]}"
    )

    # Удаляем сообщения игроков
    await callback_query.bot.delete_message(chat_id=attacker_id, message_id=game["messages"][attacker_id])
    await callback_query.bot.delete_message(chat_id=defender_id, message_id=game["messages"][defender_id])

    # Проверка на завершение игры
    if game["round"] < 6 or (game["round"] < 10 and game["scores"][game["attacker"]] == game["scores"][game["defender"]]):
        # Переключение ролей
        game["round"] += 1
        supershot_plus = 0
        supersave_plus = 0
        game["current_attacker"], game["current_defender"] = game["current_defender"], game["current_attacker"]
        game["state"] = "waiting_for_attack"
        game.pop("attack_locked", None)
        game.pop("defense_locked", None)

        # Новое сообщение для следующего атакующего
        next_attacker_id = game["current_attacker"]
        attack_message = await callback_query.bot.send_photo(
            chat_id=next_attacker_id,
            photo=cached_photo_path3,
            caption=f"Теперь ваша очередь прятать! \n\nСчёт: \n<b>{game['usernames'][game['attacker']]}</b> {game['scores'][game['attacker']]} - {game['scores'][game['defender']]} <b>{game['usernames'][game['defender']]}</b>\n\n"
            f"История ходов\n"
            f"<b>{game['usernames'][game['attacker']]}</b>: {game['history'][game['attacker']]}\n"
            f"<b>{game['usernames'][game['defender']]}</b>: {game['history'][game['defender']]}\n\n"
            f"Выберите куда спрятать золото🟡",
            parse_mode='HTML',
            reply_markup=attack_buttons_treasures_ls,
        )
        game["messages"][next_attacker_id] = attack_message.message_id

        # Уведомляем защитника ожидать
        defender_wait_message = await callback_query.bot.send_photo(
            chat_id=game["current_defender"],
            photo=cached_photo_path7,
            caption="Ожидайте, пока противник спрячет золото🟡\n",
        )
        game["messages"][game["current_defender"]] = defender_wait_message.message_id

        # Запускаем таймер для атакующего
        await start_turn_timer(game, callback_query, next_attacker_id)
    elif (game["round"] >= 6 and game["scores"][game["attacker"]] != game["scores"][game["defender"]] and game['round']<10 and game['round']%2==0)  or (game["round"] == 10 and game["scores"][game["attacker"]] == game["scores"][game["defender"]]):
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
            f"История ходов\n"
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


@player_router.callback_query(lambda c: c.data in ["help_in_treasure_ls","supershot_in_treasure_ls","supersave_in_treasure_ls"])
async def handle_defense_act(callback_query: types.CallbackQuery):
    global help_history
    user_id = callback_query.from_user.id
    user_el = await check_user_el_in_game(user_id=user_id)
    choice = callback_query.data
    if user_id not in help_history:
        if choice == "help_in_treasure_ls":
            if 'Подсказка' in user_el:
                shoot_various = ['left', 'center', 'right']
                print(help_penalty_text[0] in shoot_various)
                for i in shoot_various:
                    if i != help_penalty_text[0]:
                        shoot_various.remove(i)
                        break
                # shoot_various.remove(help_penalty_text[0])
                print(choice == "help_in_game", len(shoot_various)!=3)
                if len(shoot_various)!=3:
                    await callback_query.answer(
                        text=f"Игрок пробил в {shoot_various[0]} или {shoot_various[1]}",
                        show_alert=True
                    )
                    await use_el_in_game(user_id = user_id, sale_name='Подсказка')
                help_history.append(user_id)
            elif 'Подсказка' not in user_el:
                await callback_query.answer(
                        text=f"У вас нет этого бонуса",
                        show_alert=True
                    )

        elif choice =="supershot_in_treasure_ls":
            if 'Суперудар' in user_el:
                global supershot_plus
                print('1=!!!+!+!')
                if supershot_plus ==0:
                    supershot_plus+=1
                else: 
                    supershot_plus = 1
                await callback_query.answer(
                            text=f"Супернаходка использована, выбирайте!",
                            show_alert=True
                        )
                await use_el_in_game(user_id = user_id, sale_name='Суперудар')
                help_history.append(user_id)
            elif 'Суперудар' not in user_el:
                await callback_query.answer(
                        text=f"У вас нет этого бонуса",
                        show_alert=True
                    )
        elif choice == "supersave_in_treasure_ls":
            if 'Суперсейв' in user_el:
                global supersave_plus
                print("23e232323")
                supersave_plus += 1
                await callback_query.answer(
                            text=f"Суперпрятка использована, выберите сундук!",
                            show_alert=True
                        )
                await use_el_in_game(user_id = user_id, sale_name='Суперсейв')
                help_history.append(user_id)
            elif 'Суперсейв' not in user_el:
                await callback_query.answer(
                        text=f"У вас нет этого бонуса",
                        show_alert=True
                    )
    else:
        await callback_query.answer(
                        text=f"Усиление можно использовать только один раз за игру",
                        show_alert=True
                    )
