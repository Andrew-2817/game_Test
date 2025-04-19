from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from db_moves.get_db import check_player_design, check_user_el_in_game, check_user_role
from db_moves.add_db import use_el_in_game
from hendlers.ls.player import player_router, cached_photo_path5, cached_photo_path21
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext 
from db import get_db_connection
from hendlers.ls.player import cached_photo_path17, cached_photo_path22
from aiogram import types 
import os 
from keyboards import attack_buttons_KMN_ls, defense_buttons_KMN_ls, game_ls_back_keyboard, ls_simbols_for_ocko_att, ls_simbols_for_ocko_def
import asyncio
import random
cached_photo_path2 = types.FSInputFile(os.path.join("img", "bj.jpg"))
cached_photo_path3 = types.FSInputFile(os.path.join("img", "bj1.jpg"))
cached_photo_path4 = types.FSInputFile(os.path.join("img", "bj2.jpg"))
cached_photo_path5 = types.FSInputFile(os.path.join("img", "tours2.jpg"))
cached_photo_path6 = types.FSInputFile(os.path.join("img", "kmn_play.jpg"))
cached_photo_path7 = types.FSInputFile(os.path.join("img", "kmn_waiting.jpg"))

remove_big_values = False
remove_small_values = False
help_history = []

# Словарь для хранения активных таймеров
active_timers = {}
def generate_deck():
    suits = ["♠️", "♥️", "♦️", "♣️"]
    ranks = {
        "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
        "J": 2, "Q": 3, "K": 4, "A": 11
    }
    return [(f"{suit} {rank}", value) for suit in suits for rank, value in ranks.items()]

# Функция для сброса таймера для игрока
async def reset_timer(player_id):
    if player_id in active_timers:
        active_timers[player_id].cancel()  
        del active_timers[player_id]  



async def start_turn_timer(game, callback_query, player_id, timeout=15):
    print("&%*$(#*$)")
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
                await callback_query.bot.send_message(
                    chat_id=player_id, text="Вы не успели сделать ход!"
                )
                # Передаем ход
                await end_round(game, callback_query, player_id)


            elif game["state"] == "waiting_for_defense" and game["current_defender"] == player_id:
                print(f"Игрок {player_id} не успели сделать ход")
                await callback_query.bot.send_message(
                    chat_id=player_id, text="Вы не успели сделать ход!"
                )
                await end_round(game, callback_query, player_id)

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
async def end_round(game, callback_query, player_id):
    print(game["round"], game['scores'][game["current_attacker"]] != game['scores'][game['current_defender']])
    if game["round"] < 4 :
        if player_id == game["current_attacker"]:
            game.pop("defense_locked", None)
            print('att')
        # Переход к следующему раунду

            await callback_query.bot.edit_message_media(
                chat_id=game["current_attacker"],
                message_id=game["messages"][game["current_attacker"]],
                media=types.InputMediaPhoto(
                    media=cached_photo_path4,
                    caption=f"Вы сделали ход. Ожидайте соперника\n\n"
                    f"🎮 <b>{game['usernames'][game['current_attacker']]}</b>\n Карты: {', '.join(c[0] for c in game['history'][game['current_attacker']])}\n Очки: {game['scores'][game['current_attacker']]}.\n"
                    f"🎮 <b>{game['usernames'][game['current_defender']]}</b>\n Карты: {', '.join(c[0] for c in game['history'][game['current_defender']])}\n Очки: {game['scores'][game['current_defender']]}.\n\n",
                    parse_mode="HTML"
                ),
            )

        # Обновляем сообщение защитника
            await callback_query.bot.edit_message_media(
                chat_id=game["current_defender"],
                message_id=game["messages"][game["current_defender"]],
                media=types.InputMediaPhoto(
                    media=cached_photo_path3,
                    caption=f"🎮 <b>{game['usernames'][game['current_attacker']]}</b>\n Карты: {', '.join(c[0] for c in game['history'][game['current_attacker']])}\n Очки: {game['scores'][game['current_attacker']]}.\n"
                    f"🎮 <b>{game['usernames'][game['current_defender']]}</b>\n Карты: {', '.join(c[0] for c in game['history'][game['current_defender']])}\n Очки: {game['scores'][game['current_defender']]}.\n\n"
                    f"🎯 Ходит <b>{game['usernames'][game['defender']]}</b>. Что будете делать?",
                    parse_mode='HTML',
                ),
                reply_markup=ls_simbols_for_ocko_def,
            )
            game["round"] += 1
            # game["current_attacker"], game["current_defender"] = game["current_defender"], game["current_attacker"]
            game["state"] = "waiting_for_defense"
            game["attack_locked"] = True
            await start_turn_timer(game, callback_query, game["current_defender"])

        elif player_id == game["current_defender"]:
            game.pop("attack_locked", None)
            print('def')
        # Переход к следующему раунду

            await callback_query.bot.edit_message_media(
                chat_id=game["current_defender"],
                message_id=game["messages"][game["current_defender"]],
                media=types.InputMediaPhoto(
                    media=cached_photo_path4,
                    caption=f"Вы сделали ход. Ожидайте соперника\n\n"
                    f"🎮 <b>{game['usernames'][game['current_attacker']]}</b>\n Карты: {', '.join(c[0] for c in game['history'][game['current_attacker']])}\n Очки: {game['scores'][game['current_attacker']]}.\n"
                    f"🎮 <b>{game['usernames'][game['current_defender']]}</b>\n Карты: {', '.join(c[0] for c in game['history'][game['current_defender']])}\n Очки: {game['scores'][game['current_defender']]}.\n\n",
                    parse_mode="HTML"
                ),
            )

        # Обновляем сообщение защитника
            await callback_query.bot.edit_message_media(
                chat_id=game["current_attacker"],
                message_id=game["messages"][game["current_attacker"]],
                media=types.InputMediaPhoto(
                    media=cached_photo_path3,
                    caption=f"🎮 <b>{game['usernames'][game['current_attacker']]}</b>\n Карты: {', '.join(c[0] for c in game['history'][game['current_attacker']])}\n Очки: {game['scores'][game['current_attacker']]}.\n"
                    f"🎮 <b>{game['usernames'][game['current_defender']]}</b>\n Карты: {', '.join(c[0] for c in game['history'][game['current_defender']])}\n Очки: {game['scores'][game['current_defender']]}.\n\n"
                    f"🎯 Ходит <b>{game['usernames'][game['attacker']]}</b>. Что будете делать?",
                    parse_mode='HTML',
                ),
                reply_markup=ls_simbols_for_ocko_att,
            )
            game["round"] += 1
            # game["current_attacker"], game["current_defender"] = game["current_defender"], game["current_attacker"]
            game["state"] = "waiting_for_attack"
            game["defense_locked"] = True
            await start_turn_timer(game, callback_query, game["current_attacker"])

        #     # Запускаем таймер для атакующего
        # await start_turn_timer(game, callback_query, next_attacker_id)
    elif game["round"] == 4 and game['scores'][game['current_attacker']] != game['scores'][game['current_defender']]:
        print("01111111111111111111111111111111111111111111111111111111111111111111111")
        attacker_id = game["current_attacker"]
        defender_id = game["current_defender"]
        winner_id = attacker_id if game['scores'][attacker_id] > game['scores'][defender_id] else defender_id
        winner_username = game['usernames'][winner_id]

        new_text = (
            f"🎮 <b>{game['usernames'][attacker_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][attacker_id])}\n Очки: {game['scores'][attacker_id]}.\n"
            f"🎮 <b>{game['usernames'][defender_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {game['scores'][defender_id]}.\n\n"
        )

        final_message = (
        f"Игра завершена!\n"
        f"Победитель: <b>{winner_username}</b>\n\n"
        f"{new_text}"
        )

        await callback_query.bot.edit_message_media(
            chat_id=attacker_id,
            message_id=game["messages"][attacker_id],
            media=types.InputMediaPhoto(
                media=cached_photo_path5,
                caption=final_message,
                parse_mode='HTML'
            ),
        )

        # Обновляем сообщение защитника
        await callback_query.bot.edit_message_media(
            chat_id=defender_id,
            message_id=game["messages"][game["current_defender"]],
            media=types.InputMediaPhoto(
                media=cached_photo_path5,
                caption=final_message,
                parse_mode='HTML',
            ),
        )

    elif game["round"] == 4 and game['scores'][game["current_attacker"]] == game['scores'][game["current_defender"]]:
        attacker_id = game["current_attacker"]
        defender_id = game["current_defender"]

        new_text = (
            f"🎮 <b>{game['usernames'][attacker_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][attacker_id])}\n Очки: {game['scores'][attacker_id]}.\n"
            f"🎮 <b>{game['usernames'][defender_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {game['scores'][defender_id]}.\n\n"
        )

        final_message = (
        f"Игра завершена!\n"
        f"Ничья\n\n"
        f"{new_text}"
        )

        await callback_query.bot.edit_message_media(
            chat_id=attacker_id,
            message_id=game["messages"][attacker_id],
            media=types.InputMediaPhoto(
                media=cached_photo_path5,
                caption=final_message,
                parse_mode='HTML'
            ),
        )

        # Обновляем сообщение защитника
        await callback_query.bot.edit_message_media(
            chat_id=defender_id,
            message_id=game["messages"][game["current_defender"]],
            media=types.InputMediaPhoto(
                media=cached_photo_path5,
                caption=final_message,
                parse_mode='HTML',
            ),
        )

        # Удаляем игру
        ongoing_games.pop(game["attacker"], None)

        
# Класс для отслеживания состояния
class Ochko(StatesGroup):
    waiting_for_message = State()

# Обработчик нажатия кнопки "profile_penality"
@player_router.callback_query(lambda c: c.data == "profile_21")
async def ls_ochko(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    player_role = await check_player_design(user_id=user_id)
    print('fffff')
    # Когда выбрали игру входим в сосотояние
    await state.set_state(Ochko.waiting_for_message)
    # Проверка: если боец в игре то не даем ему вызовами кидаться
    # ВОТ ЭТО КОМЕНТИТЬ И СМОЖЕШЬ ИГРАТЬ
    # if any(user_id in (game["attacker"], game["defender"]) for game in ongoing_games.values()):
    #     await callback_query.message.answer("Вы уже участвуете в игре! Завершите текущую игру, чтобы начать новую.")
    #     return

    await callback_query.message.answer(
        text = "Напишите юзернейм противника:",
        reply_markup=game_ls_back_keyboard
        )

    @player_router.message(Ochko.waiting_for_message)
    async def check_username_ochko(message: Message):
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
                # if any(opponent_id in (game["attacker"], game["defender"]) for game in ongoing_games.values()):
                #     await message.answer(f"Пользователь @{opponent_username} уже участвует в игре. Попробуйте позже.")
                #     return

                # Кнопка "Принять вызов"
                ochko_accept_keyboard_ls = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Принять вызов",
                            callback_data=f"accept_ochko_ls:{user_id}"
                        )
                    ]
                ])

                # Отправляем вызов пользователю 
                await message.bot.send_photo(
                    chat_id=opponent_id,
                    photo=cached_photo_path22 if not player_design else cached_photo_path17,
                    caption=f"<b>Игрок @{callback_query.from_user.username}</b> вызывает вас на дуэль в <i>21 ♠️♥️</i>\n\n"
                            "Нажмите <b>Принять вызов</b>, чтобы присоединиться!",
                    parse_mode="HTML",
                    reply_markup=ochko_accept_keyboard_ls,
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
@player_router.callback_query(lambda c: c.data.startswith("accept_ochko_ls"))
async def accept_ochko_ls(callback_query: CallbackQuery):
    initiator_id = int(callback_query.data.split(":")[1])
    defender_id = callback_query.from_user.id

    # Проверка: если любой из игроков уже в игре, отменяем создание новой игры
    # B ЭТО ТОЖЕ КОМЕНТ
    # if any(initiator_id in (game["attacker"], game["defender"]) or defender_id in (game["attacker"], game["defender"]) for game in ongoing_games.values()):
    #     await callback_query.answer("Один из игроков уже участвует в игре! Завершите текущую игру, чтобы начать новую.")
    #     return

    

    deck = generate_deck()
    random.shuffle(deck)

    # Получаем юзернеймы
    initiator_chat = await callback_query.bot.get_chat(initiator_id)
    initiator_username = initiator_chat.username or f"Игрок {initiator_id}"

    defender_chat = callback_query.from_user
    defender_username = defender_chat.username or f"Игрок {defender_id}"

    player1_cards = [deck.pop() for _ in range(2)]
    player2_cards = [deck.pop() for _ in range(2)]

    def calculate_score(cards):
        score = sum(card[1] for card in cards)
        if len(cards) == 2 and cards[0][1] == 11 and cards[1][1] == 11:  # Два туза
            return 21
        return score

    player1_score = calculate_score(player1_cards)
    player2_score = calculate_score(player2_cards)

    # Инициализация игры
    ongoing_games[initiator_id] = {
        "attacker": initiator_id,
        "defender": defender_id,
        "deck": deck,
        "round": 1,
        "scores": {initiator_id: player1_score, defender_id: player2_score},
        "state": "waiting_for_attack",
        "current_attacker": initiator_id,
        "current_defender": defender_id,
        "history": {initiator_id: player1_cards, defender_id: player2_cards},
        "messages": {},  # Для хранения ID сообщений
        "usernames": {initiator_id: initiator_username, defender_id: defender_username},  # Юзернеймы игроков
    }

    game = ongoing_games[initiator_id]
    print(game)


    # game["history"][initiator_id].append(player1_cards)


    # Начало игры: отправляем одно сообщение каждому игроку
    attack_message = await callback_query.bot.send_photo(
        chat_id=initiator_id,
        photo=cached_photo_path3,
        caption=f"Игра началась!\n\n"
        f"🎮 <b>{initiator_username}</b>\n Карты: {', '.join(c[0] for c in game['history'][initiator_id])}\n Очки: {player1_score}.\n"
        f"🎮 <b>{defender_username}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {player2_score}.\n\n"
        f"🎯 Ходит <b>{initiator_username}</b>. Что будете делать?",
        parse_mode="HTML",
        reply_markup=ls_simbols_for_ocko_att,
    )
    wait_message = await callback_query.bot.send_photo(
        chat_id=defender_id,
        photo=cached_photo_path4,
        caption=f"Игра началась!\n\n"
        f"🎮 <b>{initiator_username}</b>\n Карты: {', '.join(c[0] for c in player1_cards)}\n Очки: {player1_score}.\n"
        f"🎮 <b>{defender_username}</b>\n Карты: {', '.join(c[0] for c in player2_cards)}\n Очки: {player2_score}.\n\n"
        f"🎯 Ходит <b>{initiator_username}</b>",
        parse_mode="HTML",
    )
    


    # Сохраняем ID сообщений
    game["messages"][initiator_id] = attack_message.message_id
    game["messages"][defender_id] = wait_message.message_id

    # Запускаем таймер для атакующего
    await start_turn_timer(game, callback_query, initiator_id)


# Обработчик атаки
@player_router.callback_query(lambda c: c.data in ["ochko_go_ferst_ls", "ochko_stop_ferst_ls"])
async def handle_attack_ochko_ls(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    game = next((g for g in ongoing_games.values() if g.get("current_attacker") == user_id), None)
    attacker_id = game["current_attacker"]
    defender_id = game["current_defender"]
    global remove_big_values
    global remove_small_values
    if not game or game["state"] != "waiting_for_attack":
        await callback_query.answer("Это не ваш ход!")
        return

    # Сброс таймера перед атакой
    await reset_timer(user_id)

    # Защита от Елисеев
    if "attack_locked" in game and game["attack_locked"]:
        await callback_query.answer("Вы уже сделали ход!")
        return


    
    game.pop("defense_locked", None)

    if callback_query.data == "ochko_stop_ferst_ls":
        game["state"] = "waiting_for_defense"
        game["attack_locked"] = True
        if game["scores"][attacker_id] == 21:

            new_text = (
                    f"🎮 <b>{game['usernames'][attacker_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][attacker_id])}\n Очки: {game['scores'][attacker_id]}.\n"
                    f"🎮 <b>{game['usernames'][defender_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {game['scores'][defender_id]}.\n\n"
                )

            final_message = (
            f"Игра завершена! 21! \n"
            f"Победитель: <b>{game['usernames'][attacker_id]}</b>\n\n"
            f"{new_text}"
            )

            await callback_query.bot.edit_message_media(
                chat_id=attacker_id,
                message_id=game["messages"][attacker_id],
                media = types.InputMediaPhoto(
                    media=cached_photo_path5,
                    caption=final_message,
                    parse_mode="HTML"
                
                ),
            )
            await callback_query.bot.edit_message_media(
                chat_id=defender_id,
                message_id=game["messages"][defender_id],
                media = types.InputMediaPhoto(
                    media=cached_photo_path5,
                    caption=final_message,
                    parse_mode="HTML"
                
                ),
            )
            ongoing_games.pop(game["attacker"], None)
            return

        await callback_query.bot.edit_message_media(
            chat_id=attacker_id,
            message_id=game["messages"][attacker_id],
            media=types.InputMediaPhoto(
                media=cached_photo_path4,
                caption=f"Вы сделали ход. Ожидайте соперника\n\n"
                f"🎮 <b>{game['usernames'][attacker_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][attacker_id])}\n Очки: {game['scores'][attacker_id]}.\n"
                f"🎮 <b>{game['usernames'][defender_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {game['scores'][defender_id]}.\n\n",
                parse_mode='HTML'
            ),
        )

    # Обновляем сообщение защитника
        await callback_query.bot.edit_message_media(
            chat_id=defender_id,
            message_id=game["messages"][defender_id],
            media=types.InputMediaPhoto(
                media=cached_photo_path3,
                caption=f"🎮 <b>{game['usernames'][attacker_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][attacker_id])}\n Очки: {game['scores'][attacker_id]}.\n"
                f"🎮 <b>{game['usernames'][defender_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {game['scores'][defender_id]}.\n\n"
                f"🎯 Ходит <b>{game['usernames'][game['defender']]}</b>. Что будете делать?",
                parse_mode='HTML',
            ),
            reply_markup=ls_simbols_for_ocko_def,
        )
        game['round']+=1
        # Запускаем таймер для защитника
        await start_turn_timer(game, callback_query, defender_id)
        return
    
    if remove_big_values:
        deck_cur = game["deck"]
        deck_2 = sorted(deck_cur, key=lambda x:x[1])
        deck_small = deck_2[:len(deck_2)//2]
        random.shuffle(deck_small)
        print(deck_small)
        card = deck_small.pop()
        print(card)
    elif remove_small_values:
        deck_cur = game["deck"]
        deck_2 = sorted(deck_cur, key=lambda x:x[1])
        print(deck_2)
        deck_small = deck_2[len(deck_2)//2:]
        random.shuffle(deck_small)
        print(deck_small)
        card = deck_small.pop()
        print(card)
    else:
        print(game["deck"])
        card = game["deck"].pop()
        print(card)

    # card = game["deck"].pop()
    game["history"][attacker_id].append(card)
    game["scores"][attacker_id] += card[1]

    
    if game["scores"][attacker_id] >21:
        print('перебор')

        new_text = (
                f"🎮 <b>{game['usernames'][attacker_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][attacker_id])}\n Очки: {game['scores'][attacker_id]}.\n"
                f"🎮 <b>{game['usernames'][defender_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {game['scores'][defender_id]}.\n\n"
            )

        final_message = (
        f"Игра завершена! Перебор \n"
        f"Победитель: <b>{game['usernames'][defender_id]}</b>\n\n"
        f"{new_text}"
        )

        await callback_query.bot.edit_message_media(
            chat_id=attacker_id,
            message_id=game["messages"][attacker_id],
            media = types.InputMediaPhoto(
                media=cached_photo_path5,
                caption=final_message,
                parse_mode="HTML"
            
            ),
        )
        await callback_query.bot.edit_message_media(
            chat_id=defender_id,
            message_id=game["messages"][defender_id],
            media = types.InputMediaPhoto(
                media=cached_photo_path5,
                caption=final_message,
                parse_mode="HTML"
            
            ),
        )
        ongoing_games.pop(game["attacker"], None)
        return



    new_text = (
        f"🎮 Игрок <b>{game['usernames'][game['attacker']]}</b> взял карту: {card[0]}\n\n"
        f"🎮 <b>{game['usernames'][attacker_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][attacker_id])}\n Очки: {game['scores'][attacker_id]}.\n"
        f"🎮 <b>{game['usernames'][defender_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {game['scores'][defender_id]}.\n\n"
        f"🎯 Ходит <b>{game['usernames'][game['attacker']]}</b>. Что будете делать?"
    )
    # current_markup = group_simbols_for_ocko_att if game["turn"] == 1 else group_simbols_for_ocko_def
    await callback_query.bot.edit_message_media(
        chat_id=attacker_id,
        message_id=game["messages"][attacker_id],
        media = types.InputMediaPhoto(
            media=cached_photo_path3,
            caption=new_text,
            parse_mode="HTML"
         
        ),
        reply_markup=ls_simbols_for_ocko_att)
    await start_turn_timer(game, callback_query, attacker_id)
    await callback_query.answer("Вы взяли карту. Ваш ход продолжается.")
    return



@player_router.callback_query(lambda c: c.data in ["ochko_go_second_ls", "ochko_stop_second_ls"])
async def handle_defense_ochko(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    global remove_small_values
    global remove_big_values
    game = next((g for g in ongoing_games.values() if g.get("current_defender") == user_id), None)

    if not game or game["state"] != "waiting_for_defense":
        await callback_query.answer("Это не ваш ход!")
        return

    # Сброс таймера перед защитой
    await reset_timer(user_id)

    # Блокировка повторных нажатий
    if "defense_locked" in game and game["defense_locked"]:
        await callback_query.answer("Вы уже выбрали направление44444 защиты!")
        return

    
    
    game.pop("attack_locked", None)
    attacker_id = game["current_attacker"]
    defender_id = game["current_defender"]
    print(game)
    
    if callback_query.data == "ochko_stop_second_ls":
        game["state"] = "waiting_for_attack"
        game["defense_locked"] = True

        if game["scores"][defender_id] == 21:

            new_text = (
                    f"🎮 <b>{game['usernames'][attacker_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][attacker_id])}\n Очки: {game['scores'][attacker_id]}.\n"
                    f"🎮 <b>{game['usernames'][defender_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {game['scores'][defender_id]}.\n\n"
                )

            final_message = (
            f"Игра завершена! 21! \n"
            f"Победитель: <b>{game['usernames'][defender_id]}</b>\n\n"
            f"{new_text}"
            )

            await callback_query.bot.edit_message_media(
                chat_id=attacker_id,
                message_id=game["messages"][attacker_id],
                media = types.InputMediaPhoto(
                    media=cached_photo_path5,
                    caption=final_message,
                    parse_mode="HTML"
                
                ),
            )
            await callback_query.bot.edit_message_media(
                chat_id=defender_id,
                message_id=game["messages"][defender_id],
                media = types.InputMediaPhoto(
                    media=cached_photo_path5,
                    caption=final_message,
                    parse_mode="HTML"
                
                ),
            )
            ongoing_games.pop(game["attacker"], None)
            return


        if game["round"] == 4:
            if game['scores'][attacker_id] != game['scores'][defender_id]:
                winner_id = attacker_id if game['scores'][attacker_id] > game['scores'][defender_id] else defender_id
                winner_username = game['usernames'][winner_id]
                

                new_text = (
                    f"🎮 <b>{game['usernames'][attacker_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][attacker_id])}\n Очки: {game['scores'][attacker_id]}.\n"
                    f"🎮 <b>{game['usernames'][defender_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {game['scores'][defender_id]}.\n\n"
                )

                final_message = (
                f"Игра завершена!\n"
                f"Победитель: <b>{winner_username}</b>\n\n"
                f"{new_text}"
                )

                await callback_query.bot.edit_message_media(
                    chat_id=attacker_id,
                    message_id=game["messages"][attacker_id],
                    media=types.InputMediaPhoto(
                        media=cached_photo_path5,
                        caption=final_message,
                        parse_mode='HTML'
                    ),
                )

                # Обновляем сообщение защитника
                await callback_query.bot.edit_message_media(
                    chat_id=defender_id,
                    message_id=game["messages"][game["current_defender"]],
                    media=types.InputMediaPhoto(
                        media=cached_photo_path5,
                        caption=final_message,
                        parse_mode='HTML',
                    ),
                )

                ongoing_games.pop(game["attacker"], None)
                return
            
            else:
                

                new_text = (
                    f"🎮 <b>{game['usernames'][attacker_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][attacker_id])}\n Очки: {game['scores'][attacker_id]}.\n"
                    f"🎮 <b>{game['usernames'][defender_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {game['scores'][defender_id]}.\n\n"
                )

                final_message = (
                f"Игра завершена!\n"
                f"Ничья\n\n"
                f"{new_text}"
                )

                await callback_query.bot.edit_message_media(
                    chat_id=attacker_id,
                    message_id=game["messages"][attacker_id],
                    media=types.InputMediaPhoto(
                        media=cached_photo_path5,
                        caption=final_message,
                        parse_mode='HTML'
                    ),
                )

                # Обновляем сообщение защитника
                await callback_query.bot.edit_message_media(
                    chat_id=defender_id,
                    message_id=game["messages"][game["current_defender"]],
                    media=types.InputMediaPhoto(
                        media=cached_photo_path5,
                        caption=final_message,
                        parse_mode='HTML',
                    ),
                )

                ongoing_games.pop(game["attacker"], None)
                return


        await callback_query.bot.edit_message_media(
            chat_id=attacker_id,
            message_id=game["messages"][attacker_id],
            media=types.InputMediaPhoto(
                media=cached_photo_path3,
                caption=f"🎮 <b>{game['usernames'][attacker_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][attacker_id])}\n Очки: {game['scores'][attacker_id]}.\n"
                f"🎮 <b>{game['usernames'][defender_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {game['scores'][defender_id]}.\n\n"
                f"🎯 Ходит <b>{game['usernames'][game['attacker']]}</b>. Что будете делать?",
                parse_mode="HTML"
                ),            
            reply_markup=ls_simbols_for_ocko_att,
        )

    # Обновляем сообщение защитника
        await callback_query.bot.edit_message_media(
            chat_id=defender_id,
            message_id=game["messages"][game["current_defender"]],
            media=types.InputMediaPhoto(
                media=cached_photo_path4,
                caption=f"Вы сделали ход. Ожидайте соперника\n\n"
                f"🎮 <b>{game['usernames'][attacker_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][attacker_id])}\n Очки: {game['scores'][attacker_id]}.\n"
                f"🎮 <b>{game['usernames'][defender_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {game['scores'][defender_id]}.\n\n",
                parse_mode='HTML',
            ),
        )

        # Обновляем сообщение защитника
        game['round']+=1
        # Запускаем таймер для защитника
        await start_turn_timer(game, callback_query, attacker_id)
        return

    if remove_big_values:
        deck_cur = game["deck"]
        deck_2 = sorted(deck_cur, key=lambda x:x[1])
        deck_small = deck_2[:len(deck_2)//2]
        random.shuffle(deck_small)
        print(deck_small)
        card = deck_small.pop()
        print(card)
    elif remove_small_values:
        deck_cur = game["deck"]
        deck_2 = sorted(deck_cur, key=lambda x:x[1])
        print(deck_2)
        deck_small = deck_2[len(deck_2)//2:]
        random.shuffle(deck_small)
        print(deck_small)
        card = deck_small.pop()
        print(card)
    else:
        print(game["deck"])
        card = game["deck"].pop()
        print(card)

    # card = game["deck"].pop()
    game["history"][defender_id].append(card)
    game["scores"][defender_id] += card[1]

    if game["scores"][defender_id] >21:
        print('перебор2')

        new_text = (
                f"🎮 <b>{game['usernames'][attacker_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][attacker_id])}\n Очки: {game['scores'][attacker_id]}.\n"
                f"🎮 <b>{game['usernames'][defender_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {game['scores'][defender_id]}.\n\n"
            )

        final_message = (
        f"Игра завершена! Перебор \n"
        f"Победитель: <b>{game['usernames'][attacker_id]}</b>\n\n"
        f"{new_text}"
        )

        await callback_query.bot.edit_message_media(
            chat_id=attacker_id,
            message_id=game["messages"][attacker_id],
            media = types.InputMediaPhoto(
                media=cached_photo_path5,
                caption=final_message,
                parse_mode="HTML"
            
            ),
        )
        await callback_query.bot.edit_message_media(
            chat_id=defender_id,
            message_id=game["messages"][defender_id],
            media = types.InputMediaPhoto(
                media=cached_photo_path5,
                caption=final_message,
                parse_mode="HTML"
            
            ),
        )
        ongoing_games.pop(game["attacker"], None)
        return

    new_text = (
        f"🎮 Игрок <b>{game['usernames'][game['attacker']]}</b> взял карту: {card[0]}\n\n"
        f"🎮 <b>{game['usernames'][attacker_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][attacker_id])}\n Очки: {game['scores'][attacker_id]}.\n"
        f"🎮 <b>{game['usernames'][defender_id]}</b>\n Карты: {', '.join(c[0] for c in game['history'][defender_id])}\n Очки: {game['scores'][defender_id]}.\n\n"
        f"🎯 Ходит <b>{game['usernames'][game['defender']]}</b>. Что будете делать?"
    )
    # current_markup = group_simbols_for_ocko_att if game["turn"] == 1 else group_simbols_for_ocko_def
    await callback_query.bot.edit_message_media(
        chat_id=defender_id,
        message_id=game["messages"][defender_id],
        media = types.InputMediaPhoto(
            media=cached_photo_path3,
            caption=new_text,
            parse_mode="HTML"
         
        ),
        reply_markup=ls_simbols_for_ocko_def)
    await start_turn_timer(game, callback_query, defender_id)
    await callback_query.answer("Вы взяли карту. Ваш ход продолжается.")
    return

@player_router.callback_query(lambda c: c.data in ["ochko_remove_big_values_ls", "ochko_remove_small_values_ls"])
async def handle_defense_bonus(callback_query: types.CallbackQuery):
    global help_history
    global remove_big_values
    global remove_small_values
    user_id = callback_query.from_user.id
    user_el = await check_user_el_in_game(user_id=user_id)
    choice = callback_query.data
    if user_id not in help_history:
        if choice =="ochko_remove_big_values_ls":
            if 'Страховка' in user_el:
                print('1=!!!+!+!')
                remove_big_values = True
                await callback_query.answer(
                            text=f"Страховка использована, ходите!",
                            show_alert=True
                        )
                await use_el_in_game(user_id = user_id, sale_name='Страховка')
                help_history.append(user_id)
            elif 'Страховка' not in user_el:
                await callback_query.answer(
                        text=f"У вас нет этого бонуса",
                        show_alert=True
                    )
        elif choice =="ochko_remove_small_values_ls":
            if 'Азарт' in user_el:
                print('1=!!!+!+!')
                remove_small_values = True
                await callback_query.answer(
                            text=f"Азарт использован, бейте!",
                            show_alert=True
                        )
                await use_el_in_game(user_id = user_id, sale_name='Азарт')
                help_history.append(user_id)
            elif 'Азарт' not in user_el:
                await callback_query.answer(
                        text=f"У вас нет этого бонуса",
                        show_alert=True
                    )
    else:
        await callback_query.answer(
                        text=f"Усиление можно использовать только один раз за игру",
                        show_alert=True
                    )