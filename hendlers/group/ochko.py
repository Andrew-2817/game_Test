import os
import asyncio
from aiogram import Router, types, Bot
from aiogram.filters import Command
from hendlers.ls.player import cached_photo_path17, cached_photo_path22
from keyboards import  group_simbols_for_ocko_att, group_simbols_for_ocko_def, ochko_accept_keyboard
from db_moves.add_db import add_matches, init_player_statistics, update_user_coins, update_user_statistics, use_el_in_game
from db_moves.get_db import check_player_design, check_user_el_in_game, check_user_role, get_player_best_win_streak, get_player_win_streak, get_player_match_points
from datetime import datetime, time, timedelta
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest
import time
import random

# Фотки
cached_photo_path1 = types.FSInputFile(os.path.join("img", "tours2.jpg"))
cached_photo_path2 = types.FSInputFile(os.path.join("img", "bj.jpg"))
cached_photo_path3 = types.FSInputFile(os.path.join("img", "bj1.jpg"))
cached_photo_path4 = types.FSInputFile(os.path.join("img", "bj2.jpg"))

remove_big_values = False
remove_small_values = False
help_history = []
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
ochko_router = Router()
# Функция для удаления сообщений через время
async def delete_message_after_timer(bot: Bot, chat_id: int, message_id: int, timer: int):
    await asyncio.sleep(timer)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")


active_games = {}


# Проверка если игрок уже в игре
def is_player_in_game(user_id):
    for game in active_games.values():
        if game["player1"]["id"] == user_id or game["player2"]["id"] == user_id:
            return True
    return False

# рандом на  колоду (36 карт)
def generate_deck():
    suits = ["♠️", "♥️", "♦️", "♣️"]
    ranks = {
        "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
        "J": 2, "Q": 3, "K": 4, "A": 11
    }
    return [(f"{suit} {rank}", value) for suit in suits for rank, value in ranks.items()]


# Начало игры
@ochko_router.message(Command(commands=["start_21"]))
async def start_21_game(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        await message.reply("Эта команда доступна только в группе!")
        return

    user_id = message.from_user.id
    player_role = await check_player_design(user_id=user_id)
    username = message.from_user.username
    await init_player_statistics(user_id=user_id)
    if is_player_in_game(user_id):
        await message.reply("Вы уже участвуете в игре! Завершите текущую игру, прежде чем начинать новую.")
        return

    sent_message = await message.reply_photo(
        photo=cached_photo_path22 if not player_role else cached_photo_path17,
        caption=f"Игрок @{username} вызывает на игру в 21 ♠️♥️!\n\n"
        "Нажмите <b>Принять вызов</b>, чтобы присоединиться!",
        parse_mode="HTML",
        reply_markup=ochko_accept_keyboard
    )

    # Удалить сообщение через 30 секунд
    await delete_message_after_timer(bot, sent_message.chat.id, sent_message.message_id, 30)

# Принятие вызова
@ochko_router.callback_query(lambda c: c.data == "ochko_accept")
async def handle_accept_21(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username
    message = callback_query.message
    author_id = message.reply_to_message.from_user.id
    global help_history
    help_history = []
    author_username = message.reply_to_message.from_user.username
    await init_player_statistics(user_id=user_id)
    pl_win_streak = await get_player_win_streak(user_id=author_id, game_id=3)
    p2_win_streak = await get_player_win_streak(user_id=user_id, game_id=3)
    pl1_best_win_streak = await get_player_best_win_streak(user_id=author_id, game_id=3)
    pl2_best_win_streak = await get_player_best_win_streak(user_id=user_id, game_id=3)
    # if user_id == author_id:
    #     await callback_query.answer("Вы не можете играть против себя!", show_alert=True)
    #     return
    print('какой нить принт')
    # Инициализация игры
    deck = generate_deck()
    random.shuffle(deck)

    player1_cards = [deck.pop() for _ in range(2)]
    player2_cards = [deck.pop() for _ in range(2)]

    def calculate_score(cards):
        score = sum(card[1] for card in cards)
        if len(cards) == 2 and cards[0][1] == 11 and cards[1][1] == 11:  # Два туза
            return 21
        return score

    player1_score = calculate_score(player1_cards)
    player2_score = calculate_score(player2_cards)

    game_message = await message.answer_photo(
        photo=cached_photo_path3,
        caption=f"Игра началась!\n\n"
        f"🎮 Игрок 1 (<b>{author_username}</b>) Карты: {', '.join(c[0] for c in player1_cards)}. Очки: {player1_score}.\n"
        f"🎮 Игрок 2 (<b>{username}</b>) Карты: {', '.join(c[0] for c in player2_cards)}. Очки: {player2_score}.\n\n"
        f"🎯 Ходит <b>{author_username}</b>. Что будете делать?",
        parse_mode="HTML",
        reply_markup=group_simbols_for_ocko_att
    )

    active_games[game_message.message_id] = {
    "deck": deck,
    "player1": {"id": author_id, "username": author_username, "cards": player1_cards, "score": player1_score, "stopped": False},
    "player2": {"id": user_id, "username": username, "cards": player2_cards, "score": player2_score, "stopped": False},
    "group_message": game_message,
    "turn": 1 
    }
    # deck_cur = active_games[game_message.message_id]["deck"]
    # deck_2 = sorted(deck_cur, key=lambda x:x[1])
    # deck_small = deck_2[:len(deck_2)//2]
    # random.shuffle(deck_small)
    # Запуск таймера

    # Проверка на 21 с первого хода 
    if player1_score == 21 or player2_score == 21:
        print("111")
        winner = author_username if player1_score == 21 else username
        player1_id = active_games[game_message.message_id]["player1"]['id']
        player2_id = active_games[game_message.message_id]["player2"]['id']

        request1_role = await check_user_role(player1_id)
        player1_role = [role["role"] for role in request1_role][0]
        request2_role = await check_user_role(player2_id)
        player2_role = [role["role"] for role in request2_role][0]

        # сохраняем победителя и проигравшего для статистики
        winner_id = player1_id if active_games[game_message.message_id]["player1"]['username'] == winner else player2_id
        losser_id = player1_id if active_games[game_message.message_id]["player1"]['username'] != winner else player2_id
        await game_message.edit_media(
            media = types.InputMediaPhoto(
                media=cached_photo_path1,
                caption=f"Игра завершена!\n"
                f"🎉 Победитель: <b>{winner}</b>!\n Набрано 21 очко 🃏\n\n"
                f"🎮 Игрок 1 (<b>{author_username}</b>) Карты: {', '.join(c[0] for c in player1_cards)}. Очки: {player1_score}.\n"
                f"🎮 Игрок 2 (<b>{username}</b>) Карты: {', '.join(c[0] for c in player2_cards)}. Очки: {player2_score}.\n\n",
                parse_mode="HTML"
            )
            
        )
        # сохраняем матч
        await add_matches(
            game_id=3,
            player1_id=player1_id,
            player2_id=player2_id,
            result=f"{author_username} {player1_score}:{player2_score} {username}",
            start_time= datetime.now()
        )
        if winner_id == player1_id:
            await update_user_coins(10 if player1_role == 'player' else 20, winner_id)
            await update_user_statistics(
                user_id=player1_id,
                game_id=3,
                win=1,
                draw=0,
                loss=0,
                win_streak= pl_win_streak+1,
                best_win_streak=pl1_best_win_streak if pl1_best_win_streak > pl_win_streak+1 else pl_win_streak+1,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=10
            )
            await update_user_statistics(
                user_id=player2_id,
                game_id=3,
                win=0,
                draw=0,
                loss=1,
                win_streak=0,
                best_win_streak= pl2_best_win_streak,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=0 if await get_player_match_points(user_id=player2_id, game_id=3) < 10 else -10
            )
        elif winner_id == player2_id:
            await update_user_coins(10 if player2_role == 'player' else 20, winner_id)
            await update_user_statistics(
                user_id=player2_id,
                game_id=3,
                win=1,
                draw=0,
                loss=0,
                win_streak= p2_win_streak+1,
                best_win_streak= pl2_best_win_streak if pl2_best_win_streak>p2_win_streak+1 else p2_win_streak+1,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=10
            )
            await update_user_statistics(
                user_id=player1_id,
                game_id=3,
                win=0,
                draw=0,
                loss=1,
                win_streak=0,
                best_win_streak= pl1_best_win_streak,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=0 if await get_player_match_points(user_id=player1_id, game_id=3) < 10 else -10
            )

        del active_games[game_message.message_id]
        return

    await start_turn_timer(game_message.message_id, "player1")
    await callback_query.answer()



LAST_ACTION_DELAY = timedelta(seconds=1)  # Задержка между действиями в 1 секунду

@ochko_router.callback_query(lambda c: c.data in ["ochko_go_ferst", "ochko_stop_ferst", "ochko_go_second", "ochko_stop_second"])
async def handle_player_action(callback_query: types.CallbackQuery):
    game_message_id = callback_query.message.message_id
    game = active_games.get(game_message_id)
    global remove_big_values
    global remove_small_values

    request1_role = await check_user_role(game['player1']['id'])
    player1_role = [role["role"] for role in request1_role][0]
    request2_role = await check_user_role(game['player2']['id'])
    player2_role = [role["role"] for role in request2_role][0]

    if not game:
        await callback_query.answer("Игра не найдена!", show_alert=True)
        return

    # Определяем текущего игрока
    current_turn_key = "player1" if game["turn"] == 1 else "player2"
    current_player = game[current_turn_key]
    if callback_query.from_user.id != current_player["id"]:
        await callback_query.answer("Сейчас не ваш ход!", show_alert=True)
        return

    # Проверяем, не нажимает ли игрок слишком часто
    now = datetime.now()
    if "last_action_time" in current_player:
        last_action_time = current_player["last_action_time"]
        if now - last_action_time < LAST_ACTION_DELAY:
            await callback_query.answer("Слишком быстро! Подождите секунду.", show_alert=True)
            return

    # Обновляем время последнего действия игрока
    current_player["last_action_time"] = now

    if "stop_sequence" not in game:
        game["stop_sequence"] = []

    if callback_query.data in ["ochko_stop_ferst", "ochko_stop_second"]:
        # Игрок выбирает "Стоп"
        await handle_stop_action(game_message_id, current_turn_key)
        await callback_query.answer("Вы остановились.")
        return

    # Игрок берет карту
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
    current_player["cards"].append(card)
    current_player["score"] += card[1]
    # Проверка на 21 очко или перебор
    remove_big_values = False
    remove_small_values = False
    if current_player["score"] == 21:
        pl_win_streak = await get_player_win_streak(user_id=game['player1']['id'], game_id=3)
        p2_win_streak = await get_player_win_streak(user_id=game["player2"]["id"], game_id=3)
        pl1_best_win_streak = await get_player_best_win_streak(user_id=game['player1']['id'], game_id=3)
        pl2_best_win_streak = await get_player_best_win_streak(user_id=game["player2"]["id"], game_id=3)
        winner_id = current_player['id']
        losser_id = game['player1']['id'] if game['player1']['id'] != winner_id else game['player2']['id']
        await game["group_message"].edit_media(
            media = types.InputMediaPhoto(
                media=cached_photo_path1,
                caption=f"Игра завершена!\n"
                f"🎉 Победитель: <b>{current_player['username']}</b>!\n Набрано 21 очко! 🃏\n\n"
                f"🎮 Игрок 1 (<b>{game['player1']['username']}</b>):\n Карты: {', '.join(c[0] for c in game['player1']['cards'])}. Очки: {game['player1']['score']}.\n"
                f"🎮 Игрок 2 (<b>{game['player2']['username']}</b>):\n Карты: {', '.join(c[0] for c in game['player2']['cards'])}. Очки: {game['player2']['score']}.\n\n",
                parse_mode="HTML"
            )       
        )
        # добавляем матч
        await add_matches(
            game_id=3,
            player1_id=game['player1']['id'],
            player2_id=game['player2']['id'],
            result=f"{game['player1']['username']} {game['player1']['score']}:{game['player2']['score']} {game['player2']['username']}",
            start_time= datetime.now()
        )
        if winner_id == game['player1']['id']:
            await update_user_coins(10 if player1_role == 'player' else 20, winner_id)
            await update_user_statistics(
                user_id=game['player1']['id'],
                game_id=3,
                win=1,
                draw=0,
                loss=0,
                win_streak= pl_win_streak+1,
                best_win_streak=pl1_best_win_streak if pl1_best_win_streak > pl_win_streak+1 else pl_win_streak+1,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=10
            )
            await update_user_statistics(
                user_id=game['player2']['id'],
                game_id=3,
                win=0,
                draw=0,
                loss=1,
                win_streak=0,
                best_win_streak= pl2_best_win_streak,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=0 if await get_player_match_points(user_id=game['player2']['id'], game_id=3) < 10 else -10
            )
        elif winner_id == game['player2']['id']:
            await update_user_coins(10 if player2_role == 'player' else 20, winner_id)
            await update_user_statistics(
                user_id=game['player2']['id'],
                game_id=3,
                win=1,
                draw=0,
                loss=0,
                win_streak= p2_win_streak+1,
                best_win_streak= pl2_best_win_streak if pl2_best_win_streak>p2_win_streak+1 else p2_win_streak+1,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=10
            )
            await update_user_statistics(
                user_id=game['player1']['id'],
                game_id=3,
                win=0,
                draw=0,
                loss=1,
                win_streak=0,
                best_win_streak= pl1_best_win_streak,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=0 if await get_player_match_points(user_id=game['player1']['id'], game_id=3) < 10 else -10
            )
        del active_games[game_message_id]
        return

    if current_player["score"] > 21:
        opponent_player = game["player2"] if current_turn_key == "player1" else game["player1"]
        winner_id = opponent_player["id"]
        pl_win_streak = await get_player_win_streak(user_id=game['player1']['id'], game_id=3)
        p2_win_streak = await get_player_win_streak(user_id=game["player2"]["id"], game_id=3)
        pl1_best_win_streak = await get_player_best_win_streak(user_id=game['player1']['id'], game_id=3)
        pl2_best_win_streak = await get_player_best_win_streak(user_id=game["player2"]["id"], game_id=3)
        losser_id = current_player["id"]
        await game["group_message"].edit_media(
            media = types.InputMediaPhoto(
                media=cached_photo_path1,
                caption=f"Игра завершена! 🔥 Перебор!\n"
                f"Победитель: <b>{opponent_player['username']}</b>!\n\n"
                f"🎮 Игрок 1 (<b>{game['player1']['username']}</b>): Карты: {', '.join(c[0] for c in game['player1']['cards'])}. Очки: {game['player1']['score']}.\n"
                f"🎮 Игрок 2 (<b>{game['player2']['username']}</b>): Карты: {', '.join(c[0] for c in game['player2']['cards'])}. Очки: {game['player2']['score']}.\n\n",
                parse_mode="HTML"
            )
        )
        # добавляем матч
        await add_matches(
            game_id=3,
            player1_id=game['player1']['id'],
            player2_id=game['player2']['id'],
            result=f"{game['player1']['username']} {game['player1']['score']}:{game['player2']['score']} {game['player2']['username']}",
            start_time= datetime.now()
        )
        if winner_id == game['player1']['id']:
            await update_user_coins(10 if player1_role == 'player' else 20, winner_id)
            await update_user_statistics(
                user_id=game['player1']['id'],
                game_id=3,
                win=1,
                draw=0,
                loss=0,
                win_streak= pl_win_streak+1,
                best_win_streak=pl1_best_win_streak if pl1_best_win_streak > pl_win_streak+1 else pl_win_streak+1,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=10
            )
            await update_user_statistics(
                user_id=game['player2']['id'],
                game_id=3,
                win=0,
                draw=0,
                loss=1,
                win_streak=0,
                best_win_streak= pl2_best_win_streak,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=0 if await get_player_match_points(user_id=game['player2']['id'], game_id=3) < 10 else -10
            )
        elif winner_id == game['player2']['id']:
            await update_user_coins(10 if player2_role == 'player' else 20, winner_id)
            await update_user_statistics(
                user_id=game['player2']['id'],
                game_id=3,
                win=1,
                draw=0,
                loss=0,
                win_streak= p2_win_streak+1,
                best_win_streak= pl2_best_win_streak if pl2_best_win_streak>p2_win_streak+1 else p2_win_streak+1,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=10
            )
            await update_user_statistics(
                user_id=game['player1']['id'],
                game_id=3,
                win=0,
                draw=0,
                loss=1,
                win_streak=0,
                best_win_streak= pl1_best_win_streak,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=0 if await get_player_match_points(user_id=game['player1']['id'], game_id=3) < 10 else -10
            )
        del active_games[game_message_id]
        return

    # Обновление текста хода
    updated_cards = ', '.join([c[0] for c in current_player["cards"]])
    updated_score = current_player["score"]
    new_text = (
        f"🎮 Игрок <b>{current_player['username']}</b> взял карту: {card[0]} (Очки: {updated_score}).\n\n"
        f"🎮 Игрок 1 (<b>{game['player1']['username']}</b>): Карты: {', '.join(c[0] for c in game['player1']['cards'])}. Очки: {game['player1']['score']}.\n"
        f"🎮 Игрок 2 (<b>{game['player2']['username']}</b>): Карты: {', '.join(c[0] for c in game['player2']['cards'])}. Очки: {game['player2']['score']}.\n\n"
        f"🎯 Ходит <b>{current_player['username']}</b>. Что будете делать?"
    )
    current_markup = group_simbols_for_ocko_att if game["turn"] == 1 else group_simbols_for_ocko_def
    await game["group_message"].edit_media(
        media = types.InputMediaPhoto(
            media=cached_photo_path4 if game["turn"] ==2 else cached_photo_path3,
            caption=new_text,
            parse_mode="HTML"
         
        ),
        reply_markup=current_markup)
    await start_turn_timer(game_message_id, current_turn_key)
    await callback_query.answer("Вы взяли карту. Ваш ход продолжается.")


async def start_turn_timer(game_message_id, current_turn_key):
    print('hey')
    game = active_games.get(game_message_id)
    if not game:
        return

    if "current_timer" in game:
        game["current_timer"].cancel()

    timer_task = asyncio.create_task(timer_logic(game_message_id, current_turn_key))
    game["current_timer"] = timer_task
    await timer_task


async def timer_logic(game_message_id, current_turn_key):
    # print('timer')
    try:
        await asyncio.sleep(10)  # Таймер на 10 секунд
    except asyncio.CancelledError:
        return

    # Если игрок не сделал ход за время
    game = active_games.get(game_message_id)
    if not game or game.get("turn") != (1 if current_turn_key == "player1" else 2):
        return

    current_player = game[current_turn_key]
    print(current_player["stopped"])
    if not current_player.get("stopped", False):
        await handle_stop_action(game_message_id, current_turn_key, is_timeout=True)


async def handle_stop_action(game_message_id, current_turn_key, is_timeout=False):
    print('next')
    game = active_games.get(game_message_id)
    if not game:
        return

    current_player = game[current_turn_key]
    opponent_turn_key = "player2" if current_turn_key == "player1" else "player1"

    current_player["stopped"] = True
    # Это я добавил чтобы ошибки не было и таймер работал
    if "stop_sequence" not in game:
        game["stop_sequence"] = []

    game["stop_sequence"].append("timeout" if is_timeout else f"stop_{current_turn_key}")
    
    # Проверка завершения игры
    if len(game["stop_sequence"]) == 4:
        await finish_game(game_message_id)
        return

    # Передача хода следующему игроку
    game["turn"] = 2 if game["turn"] == 1 else 1
    next_player = game["player1"] if game["turn"] == 1 else game["player2"]
    next_player['stopped'] = False

    new_text = (
        f"🎮 Игрок 1 (<b>{game['player1']['username']}</b>) Карты: {', '.join(c[0] for c in game['player1']['cards'])}. Очки: {game['player1']['score']}.\n"
        f"🎮 Игрок 2 (<b>{game['player2']['username']}</b>) Карты: {', '.join(c[0] for c in game['player2']['cards'])}. Очки: {game['player2']['score']}.\n\n"
        f"🎯 Ходит <b>{next_player['username']}</b>. Что будете делать?"
    )
    current_markup = group_simbols_for_ocko_att if game["turn"] == 1 else group_simbols_for_ocko_def
    await game["group_message"].edit_media(
        media = types.InputMediaPhoto(
            media=cached_photo_path4 if game["turn"] ==2 else cached_photo_path3,
            caption=new_text,
            parse_mode="HTML"
        ),
        reply_markup=current_markup)

    asyncio.create_task(start_turn_timer(game_message_id, opponent_turn_key))


async def finish_game(game_message_id):
    game = active_games.get(game_message_id)

    if not game:
        return

    player1 = game["player1"]
    player2 = game["player2"]
    pl_win_streak = await get_player_win_streak(user_id=game["player1"]["id"], game_id=3)
    p2_win_streak = await get_player_win_streak(user_id=game["player2"]["id"], game_id=3)
    pl1_best_win_streak = await get_player_best_win_streak(user_id=game["player1"]["id"], game_id=3)
    pl2_best_win_streak = await get_player_best_win_streak(user_id=game["player2"]["id"], game_id=3)

    request1_role = await check_user_role(game['player1']['id'])
    player1_role = [role["role"] for role in request1_role][0]
    request2_role = await check_user_role(game['player2']['id'])
    player2_role = [role["role"] for role in request2_role][0]

    # достаем карты игроков 
    players_summary = (
        f"🎮 Игрок 1 (<b>{player1['username']}</b>) Карты: {', '.join(c[0] for c in player1['cards'])}. Очки: {player1['score']}.\n"
        f"🎮 Игрок 2 (<b>{player2['username']}</b>) Карты: {', '.join(c[0] for c in player2['cards'])}. Очки: {player2['score']}.\n\n"
    )

    # условия на победу проеб и ничейку 
    if player1["stopped"] and player2["stopped"]:
        if player1["score"] > player2["score"] and player1["score"] <= 21:
            winner = player1
            losser = player2
        elif player2["score"] > player1["score"] and player2["score"] <= 21:
            winner = player2
            losser = player1
        else:
            winner = None
        result_message = (
            f"🎉 Победитель: <b>{winner['username']}</b>!"
            if winner else "🤝 Ничья!"
        )
    else:
        result_message = "Игра завершена без победителя!"

    # сообщение после катки  
    final_message = (
        f"Игра завершена!\n"
        f"{result_message}\n\n"
        f"{players_summary}"
    )

    # сама отправка 
    await game["group_message"].edit_media(
        media = types.InputMediaPhoto(
            media=cached_photo_path1,
            caption=final_message,
            parse_mode="HTML"
        )
    )
    # добавляем матч
    await add_matches(
        game_id=3,
        player1_id=game['player1']['id'],
        player2_id=game['player2']['id'],
        result=f"{game['player1']['username']} {game['player1']['score']}:{game['player2']['score']} {game['player2']['username']}",
        start_time= datetime.now()
    )
    # проверка на налицие победителя
    if winner and winner["id"] == player1["id"]:
        await update_user_coins(10 if player1_role == 'player' else 20, winner["id"])
        # обновляем статистику каждому игроку
        await update_user_statistics(
                user_id=player1["id"],
                game_id=3,
                win=1,
                draw=0,
                loss=0,
                win_streak= pl_win_streak+1,
                best_win_streak= pl1_best_win_streak if pl1_best_win_streak > pl_win_streak+1 else pl_win_streak+1,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=10
            )
        await update_user_statistics(
            user_id=player2["id"],
            game_id=3,
            win=0,
            draw=0,
            loss=1,
            win_streak= 0,
            best_win_streak= pl2_best_win_streak,
            choice_1=0,
            choice_2=0,
            choice_3=0,
            match_points=0 if await get_player_match_points(user_id=losser["id"], game_id=3) < 10 else -10
        )
    elif winner and winner["id"] == player2["id"]:
        await update_user_coins(10 if player2_role == 'player' else 20, winner["id"])
        # обновляем статистику каждому игроку
        await update_user_statistics(
                user_id=player2["id"],
                game_id=3,
                win=1,
                draw=0,
                loss=0,
                win_streak= p2_win_streak+1,
                best_win_streak= pl2_best_win_streak if pl2_best_win_streak>p2_win_streak+1 else p2_win_streak+1,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=10
            )
        await update_user_statistics(
            user_id=player1["id"],
            game_id=3,
            win=0,
            draw=0,
            loss=1,
            win_streak=0,
            best_win_streak= pl1_best_win_streak,
            choice_1=0,
            choice_2=0,
            choice_3=0,
            match_points=0 if await get_player_match_points(user_id=losser["id"], game_id=3) < 10 else -10
        )
    # иначе ничья
    else:
        await update_user_statistics(
                user_id=player1["id"],
                game_id=3,
                win=0,
                draw=1,
                loss=0,
                win_streak= 0,
                best_win_streak= pl1_best_win_streak,
                choice_1=0,
                choice_2=0,
                choice_3=0,
                match_points=3
            )
        await update_user_statistics(
            user_id=player2["id"],
            game_id=3,
            win=0,
            draw=1,
            loss=0,
            win_streak=0,
            best_win_streak= pl2_best_win_streak,
            choice_1=0,
            choice_2=0,
            choice_3=0,
            match_points=3
        ) 
    del active_games[game_message_id]


@ochko_router.callback_query(lambda c: c.data in ["ochko_remove_big_values", "ochko_remove_small_values"])
async def handle_defense_bonus(callback_query: types.CallbackQuery):
    global help_history
    global remove_big_values
    global remove_small_values
    user_id = callback_query.from_user.id
    user_el = await check_user_el_in_game(user_id=user_id)
    choice = callback_query.data
    if user_id not in help_history:
        if choice =="ochko_remove_big_values":
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
        elif choice =="ochko_remove_small_values":
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