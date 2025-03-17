import os
import time
import asyncio
from aiogram import Router, types, Bot
from aiogram.filters import Command
from hendlers.ls.player import cached_photo_path21
from keyboards import group_simbols_for_KMN, CMN_accept_keyboard
from db import get_db_connection
from db_moves.add_db import add_shop, add_user, init_player_statistics, update_user_coins, update_user_statistics, add_matches, use_el_in_game
from db_moves.get_db import check_player_design, check_user_el_in_game, check_user_role, get_player_match_points, get_player_win_streak, get_player_best_win_streak
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Фотографии
cached_photo_path3 = types.FSInputFile(os.path.join("img", "КМН.jpg"))
cached_photo_path4 = types.FSInputFile(os.path.join("img", "kmn_play.jpg"))
cached_photo_path5 = types.FSInputFile(os.path.join("img", "5711954.jpg"))
cached_photo_path6 = types.FSInputFile(os.path.join("img", "tours2.jpg"))
cached_photo_path7 = types.FSInputFile(os.path.join("img", "11698.jpg"))
help_history = []
help_penalty_text = []
supershot_plus = 0
pl1_choice = []
pl2_choice = []
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
KMN_router = Router()
# функция для фонового добавления пользователя(если он в личку не зайдёт)
async def add_user_in_background(user_id: int, username: str, join_date: datetime):
    await add_user(user_id, username, join_date)


async def delete_message_after_timer(bot: Bot, chat_id: int, message_id: int, timer: int):
    await asyncio.sleep(timer)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")

def is_player_in_game(user_id):
    for game in active_games.values():
        if (
            game["player1"]["id"] == user_id or 
            game["player2"]["id"] == user_id
        ):
            return True
    return False


@KMN_router.message(Command(commands=["start_CMN"]))
async def start_game_command(message: types.Message):
    
    user_id = message.from_user.id
    request_role = await check_user_role(user_id)
    player_role = [role["role"] for role in request_role][0]

    player_design = await check_player_design(user_id)
    username = message.from_user.username
    join_date = datetime.now()

    # Запуск добавления пользователя в фоновом режиме
    asyncio.create_task(add_user_in_background(user_id, username, join_date))

    # Иницивлизация статистики пользователя если не запустил бота
    await init_player_statistics(user_id)

    if message.chat.type not in ["group", "supergroup"]:
        await message.reply("Эта команда доступна только в группе!")
        return

    if is_player_in_game(message.from_user.id):
        await message.reply("Вы уже участвуете в игре! Завершите текущую игру, прежде чем начинать новую.")
        return

    sent_message = await message.reply_photo(
        photo=cached_photo_path3 if not player_design else cached_photo_path21,
        caption=f"<b>Игрок @{message.from_user.username}</b> вызывает на дуэль в <i>Цуефа!🪨✂️📃</i>\n"
        "Нажмите <b>Принять вызов</b>, чтобы присоединиться!",
        parse_mode='HTML',
        reply_markup=CMN_accept_keyboard
    )
    await delete_message_after_timer(
        bot=bot,
        chat_id=sent_message.chat.id,
        message_id=sent_message.message_id,
        timer=30
    )

active_games = {}
emojis = {"kamen": "🪨", "bumaga": "📃", "nognichi": "✂️", "none": "❌"}
choices = {
    "kamen": {"bumaga": "проиграл", "nognichi": "победил", "none": "победил"},
    "bumaga": {"nognichi": "проиграл", "kamen": "победил", "none": "победил"},
    "nognichi": {"kamen": "проиграл", "bumaga": "победил", "none": "победил"},
    "none": {"kamen": "проиграл", "bumaga": "проиграл", "nognichi": "проиграл"}
}

@KMN_router.callback_query(lambda c: c.data == "CMN_accept")
async def handle_CMN_accept(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username
    global help_history
    help_history = []
    message = callback_query.message
    author_id = message.reply_to_message.from_user.id
    author_username = message.reply_to_message.from_user.username
    await add_shop(user_id = user_id)
    # player_kb = []
    # check_player_el = await check_user_el_in_game(user_id = user_id)
    # for i in check_player_el:
    #     el_data = ''
    #     if i == 'Подсказка': el_data = 'help_in_game'
    #     elif i == "Суперудар": el_data = 'supershot_in_game'
    #     else: el_data = 'supersave_in_game'
    #     new_btn = InlineKeyboardButton(text=f"{i}", callback_data=el_data)
    #     player_kb.append(new_btn)
    # print(check_player_el)

    join_date = datetime.now()

    # Запуск добавления пользователя в фоновом режиме
    asyncio.create_task(add_user_in_background(user_id, username, join_date))

    # Иницивлизация статистики пользователя если не запустил бота
    await init_player_statistics(user_id)

    if is_player_in_game(user_id):
        await callback_query.answer("Вы уже участвуете в игре! Завершите текущую игру, чтобы присоединиться.", show_alert=True)
        return

    # if user_id == author_id:
    #     await callback_query.answer("Вы не можете играть против себя!", show_alert=True)
    #     return


    game_message = await callback_query.message.answer_photo(
        photo=cached_photo_path4,
        caption = f"Игра началась!\n{author_username} VS {username}\n\n"
        f" • <i>Раунд 1</i>: Ожидаем ходы игроков.\n",  # Текст для отображения начала раунда
        parse_mode = "HTML",
        reply_markup=group_simbols_for_KMN
    )

    active_games[game_message.message_id] = {
        "player1": {"id": author_id, "username": author_username, "choice": None, "score": 0, "start_time": time.time()},
        "player2": {"id": user_id, "username": username, "choice": None, "score": 0, "start_time": time.time()},
        "round": 1,
        "history": [],
        "consecutive_draws": 0,
        "message": game_message
    }

    await callback_query.answer()
    await start_round_timer(game_message.message_id)


async def start_round_timer(message_id):
    game = active_games[message_id]

    pl_win_streak = await get_player_win_streak(user_id=game["player1"]["id"], game_id=1)
    p2_win_streak = await get_player_win_streak(user_id=game["player2"]["id"], game_id=1)
    pl1_best_win_streak = await get_player_best_win_streak(user_id=game["player1"]["id"], game_id=1)
    pl2_best_win_streak = await get_player_best_win_streak(user_id=game["player2"]["id"], game_id=1)
    request1_role = await check_user_role(game["player1"]["id"])
    player1_role = [role["role"] for role in request1_role][0]

    request2_role = await check_user_role(game["player2"]["id"])
    player2_role = [role["role"] for role in request2_role][0]
   
    if "start_time" not in game:
        game["start_time"] = datetime.now()

    while True:
        # Проверяем выбор первого игрока за 10 сек не успел тогда крестик
        if game["player1"]["choice"] is None:
            time_elapsed_player1 = time.time() - game["player1"].get("start_time", time.time())
            if time_elapsed_player1 >= 5:
                game["player1"]["choice"] = "none"

        # Проверяем выбор второго игрока за 10 сек 
        if game["player2"]["choice"] is None:
            time_elapsed_player2 = time.time() - game["player2"].get("start_time", time.time())
            if time_elapsed_player2 >= 5:
                game["player2"]["choice"] = "none"

        # Когда оба игрока сделали выбор
        if game["player1"]["choice"] and game["player2"]["choice"]:
            result_text = resolve_round(game)

            # Обработка победы первого игрока
            if game["player1"]["score"] == 3:
                result = f"{game['player1']['username']} 3:{game['player2']['score']} {game['player2']['username']}"
                # тут можно конечную фразу поменять о победе 1 игрока 
                await game["message"].edit_media(
                    media = types.InputMediaPhoto(
                        media= cached_photo_path6,
                        caption = f"Игра завершена! •Цуефа\n\n <b>{game['player1']['username']} победил!</b> \n {game['player1']['score']} : {game['player2']['score']}\n\n{result_text}\n",
                        parse_mode = "HTML"
                    )       
                )
                # Сохраняем выбор первого и второго игрока в игре
                often_choice_pl1 = {
                    "kamen" : pl1_choice.count('kamen'),
                    "nognichi" : pl1_choice.count('nognichi'),
                    "bumaga" : pl1_choice.count('bumaga')
                }
                often_choice_pl2 = {
                    "kamen" : pl2_choice.count('kamen'),
                    "nognichi" : pl2_choice.count('nognichi'),
                    "bumaga" : pl2_choice.count('bumaga')
                }
                await update_user_coins(10 if player1_role == 'player' else 20, game["player1"]["id"])
                print(often_choice_pl1, often_choice_pl2, pl1_choice)
                # pl_win_streak = await get_player_win_streak(user_id=game["player1"]["id"], game_id=1)
                # p2_win_streak = await get_player_win_streak(user_id=game["player2"]["id"], game_id=1)
                # pl1_best_win_streak = await get_player_best_win_streak(user_id=game["player1"]["id"], game_id=1)
                # pl2_best_win_streak = await get_player_best_win_streak(user_id=game["player2"]["id"], game_id=1)
                await add_matches(
                    game_id=1, 
                    player1_id=game["player1"]["id"], 
                    player2_id=game["player2"]["id"], 
                    result=result, 
                    start_time=game["start_time"]
                )
                await update_user_statistics(
                    user_id=game["player1"]["id"],
                    game_id=1,
                    win = 1,
                    draw = 0,
                    loss = 0,
                    win_streak = pl_win_streak+1,
                    best_win_streak= pl1_best_win_streak if pl1_best_win_streak>pl_win_streak+1 else pl_win_streak+1,
                    choice_1=often_choice_pl1['kamen'],
                    choice_2=often_choice_pl1['nognichi'],
                    choice_3=often_choice_pl1['bumaga'],
                    match_points=10
                )
                await update_user_statistics(
                    user_id=game["player2"]["id"],
                    game_id=1,
                    win = 0,
                    draw = 0,
                    loss = 1,
                    win_streak=0,
                    best_win_streak= pl2_best_win_streak,
                    choice_1=often_choice_pl2['kamen'],
                    choice_2=often_choice_pl2['nognichi'],
                    choice_3=often_choice_pl2['bumaga'],
                    match_points= 0 if await get_player_match_points(user_id=game["player2"]["id"], game_id=1) < 10 else -10
                )
                pl1_choice.clear()
                pl2_choice.clear()
                del active_games[message_id]
                break

            # Обработка победы второго игрока
            elif game["player2"]["score"] == 3:
                result = f"{game['player1']['username']} {game['player1']['score']}:3 {game['player2']['username']}"
                # тут можно конечную фразу поменять о победе 2 игрока 
                await game["message"].edit_media(
                    media = types.InputMediaPhoto(
                        media= cached_photo_path6,
                        caption = f"Игра завершена! •Цуефа\n\n <b>{game['player2']['username']} победил! </b>\n {game['player1']['score']} : {game['player2']['score']} \n\n{result_text}\n",
                        parse_mode = "HTML"
                    )
                )
                often_choice_pl1 = {
                    "kamen" : pl1_choice.count('kamen'),
                    "nognichi" : pl1_choice.count('nognichi'),
                    "bumaga" : pl1_choice.count('bumaga')
                }
                often_choice_pl2 = {
                    "kamen" : pl2_choice.count('kamen'),
                    "nognichi" : pl2_choice.count('nognichi'),
                    "bumaga" : pl2_choice.count('bumaga')
                }
                await update_user_coins(10 if player2_role == 'player' else 20, game["player2"]["id"])
                await add_matches(
                    game_id=1, 
                    player1_id=game["player1"]["id"], 
                    player2_id=game["player2"]["id"], 
                    result=result, 
                    start_time=game["start_time"]
                )
                await update_user_statistics(
                    user_id=game["player1"]["id"],
                    game_id=1,
                    win = 0,
                    draw = 0,
                    loss = 1,
                    win_streak=0,
                    best_win_streak=pl1_best_win_streak,
                    choice_1=often_choice_pl1['kamen'],
                    choice_2=often_choice_pl1['nognichi'],
                    choice_3=often_choice_pl1['bumaga'],
                    match_points= 0 if await get_player_match_points(user_id=game["player1"]["id"], game_id=1) < 10 else -10
                )
                await update_user_statistics(
                    user_id=game["player2"]["id"],
                    game_id=1,
                    win = 1,
                    draw = 0,
                    loss = 0,
                    win_streak = p2_win_streak+1,
                    best_win_streak= pl2_best_win_streak if pl2_best_win_streak>p2_win_streak+1 else p2_win_streak+1,
                    choice_1=often_choice_pl2['kamen'],
                    choice_2=often_choice_pl2['nognichi'],
                    choice_3=often_choice_pl2['bumaga'],
                    match_points=10
                )
                pl1_choice.clear()
                pl2_choice.clear()
                del active_games[message_id]
                break

            # для злодеев которые на ничьих
            elif game["consecutive_draws"] >= 8:
                result = f"{game['player1']['username']} {game['player1']['score']}:{game['player2']['score']} {game['player2']['username']}"
                # если ничья то тут можно фразу поменять 
                await game["message"].edit_media(
                    media = types.InputMediaPhoto(
                        media= cached_photo_path6,
                        caption = f"Игра завершена! •Цуефа\n\n<b> Ничья </b> — 8 ничьих подряд.\n{game['player1']['score']} : {game['player2']['score']} \n\n{result_text}\n",
                        parse_mode = "HTML"
                    )
                )
                often_choice_pl1 = {
                    "kamen" : pl1_choice.count('kamen'),
                    "nognichi" : pl1_choice.count('nognichi'),
                    "bumaga" : pl1_choice.count('bumaga')
                }
                often_choice_pl2 = {
                    "kamen" : pl2_choice.count('kamen'),
                    "nognichi" : pl2_choice.count('nognichi'),
                    "bumaga" : pl2_choice.count('bumaga')
                }
                await add_matches(
                    game_id=1, 
                    player1_id=game["player1"]["id"], 
                    player2_id=game["player2"]["id"], 
                    result=result, 
                    start_time=game["start_time"]
                )
                await update_user_statistics(
                    user_id=game["player1"]["id"],
                    game_id=1,
                    win = 0,
                    draw = 1,
                    loss = 0,
                    win_streak = 0,
                    best_win_streak= pl1_best_win_streak,
                    choice_1=often_choice_pl1['kamen'],
                    choice_2=often_choice_pl1['nognichi'],
                    choice_3=often_choice_pl1['bumaga'],
                    match_points=3
                )
                await update_user_statistics(
                    user_id=game["player2"]["id"],
                    game_id=1,
                    win = 0,
                    draw = 1,
                    loss = 0,
                    win_streak = 0,
                    best_win_streak= pl2_best_win_streak,
                    choice_1=often_choice_pl2['kamen'],
                    choice_2=often_choice_pl2['nognichi'],
                    choice_3=often_choice_pl2['bumaga'],
                    match_points=3
                )
                pl1_choice.clear()
                pl2_choice.clear()
                del active_games[message_id]
                break

            # Если ничего из этого 
            else:
                game["round"] += 1
                reset_round(game)
                # текст для следущего раунда 
                await game["message"].edit_caption(
                    caption = result_text,
                    parse_mode = "HTML",
                    reply_markup=group_simbols_for_KMN,  # кнопки показать
                )
                
                await start_round_timer(message_id)
            break

        # Задержка для цикла гпт говорит задержка чуть ослабляет нагрузку я даже поверил 
        await asyncio.sleep(1)



@KMN_router.callback_query(lambda c: c.data in ["kamen", "bumaga", "nognichi"])
async def handle_choice(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    choice = callback_query.data
    game = active_games.get(message_id)

    if not game:
        await callback_query.answer("Эта игра больше недоступна.", show_alert=True)
        return

    
    if user_id not in [game["player1"]["id"], game["player2"]["id"]]:
        await callback_query.answer("Вы не можете сделать выбор в этой игре.", show_alert=True)
        return

    current_player = "player1" if game["player1"]["id"] == user_id else "player2"

    if game[current_player]["choice"] is not None:
        await callback_query.answer(f"Вы уже выбрали {game[current_player]['choice']}.")
        return

    game[current_player]["choice"] = choice
    await callback_query.answer("Ваш выбор сохранён.")


def resolve_round(game):
    player1_choice = game["player1"]["choice"]
    player2_choice = game["player2"]["choice"]
    global supershot_plus

    if player1_choice == player2_choice:
        # Ничья
        game["consecutive_draws"] += 1
        result = (
            f" • <i>Раунд {game['round']}</i>:\n {game['player1']['username']} {emojis[player1_choice]} \n"
            f"{game['player2']['username']} {emojis[player2_choice]} \n<b>Ничья!</b>\n"
        )
    else:
        game["consecutive_draws"] = 0
        # Проверяем кто раунд забрал 
        if player2_choice in choices[player1_choice]:
            outcome = choices[player1_choice][player2_choice]
        else:
            outcome = "проиграл"

        if outcome == "победил":
            winner, loser = "player1", "player2"
        else:
            winner, loser = "player2", "player1"

        # Счёт в серии 
        game[winner]["score"] = game[winner]["score"] + supershot_plus + 1
        result = (
            f" • <i>Раунд {game['round']}</i>:\n{game[winner]['username']} {emojis[player1_choice if winner == 'player1' else player2_choice]} \n"
            f"{game[loser]['username']} {emojis[player2_choice if winner == 'player1' else player1_choice]} \n<b>🏅{game[winner]['username']} победил!</b>\n"
        )

    # Обновление предыдущих раундов 
    game["history"].append(result)

    # Проверка, если игра завершена
    if game["player1"]["score"] >= 3 or game["player2"]["score"] >= 3 or game["consecutive_draws"] >= 8:
        # Игра завершена
        # текст когда закончилась катка:
        result_text = f"{game['player1']['username']} vs {game['player2']['username']}\n" + "\n".join(game["history"])
        return result_text

    # Текст если игра не завершена
    game_state = (
        f"{game['player1']['username']} vs {game['player2']['username']}\n"
        f"Счёт: {game['player1']['score']}:{game['player2']['score']}\n\n"
        f"История игры:\n" + "\n".join(game["history"]) + "\n\n"
        f" • <i>Раунд {game['round'] + 1}</i>: Ожидаем ходы игроков.\n"
    )

    return game_state

def reset_round(game):
    game["player1"]["choice"] = None
    game["player2"]["choice"] = None
    game["player1"]["start_time"] = time.time()
    game["player2"]["start_time"] = time.time()
    global supershot_plus
    supershot_plus = 0



@KMN_router.callback_query(lambda c: c.data in ["supershot_in_kmn"])
async def handle_defense_kmn(callback_query: types.CallbackQuery):
    global help_history
    user_id = callback_query.from_user.id
    user_el = await check_user_el_in_game(user_id=user_id)
    choice = callback_query.data
    if user_id not in help_history:
        if choice =="supershot_in_kmn":
            if 'Суперудар' in user_el:
                global supershot_plus
                supershot_plus+=1
    
                await callback_query.answer(
                            text=f"Суперудар использован, бейте!",
                            show_alert=True
                        )
                await use_el_in_game(user_id = user_id, sale_name='Суперудар')
                help_history.append(user_id)
            elif 'Суперудар' not in user_el:
                await callback_query.answer(
                        text=f"У вас нет этого бонуса",
                        show_alert=True
                    )
    else:
        await callback_query.answer(
                        text=f"Усиление можно использовать только один раз за игру",
                        show_alert=True
                    )