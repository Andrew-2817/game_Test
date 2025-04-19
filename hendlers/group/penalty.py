import os
import asyncio
from aiogram import Router, types, Bot
from aiogram.filters import Command
from hendlers.ls.player import cached_photo_path20
from keyboards import penalty_accept_keyboard, group_simbols_for_penalty_att, group_simbols_for_penalty_def
from db_moves.add_db import add_matches, init_player_statistics, update_user_coins, update_user_statistics, use_el_in_game
from db_moves.get_db import check_player_design, check_user_el_in_game, check_user_role, get_player_best_win_streak, get_player_win_streak, get_player_match_points
from datetime import datetime, time
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

# Фотографии
cached_photo_path3 = types.FSInputFile(os.path.join("img", "Airbrush-penki7.jpg"))
cached_photo_path5 = types.FSInputFile(os.path.join("img", "5711954.jpg"))
cached_photo_path6 = types.FSInputFile(os.path.join("img", "tours2.jpg"))
cached_photo_path7 = types.FSInputFile(os.path.join("img", "Airbrush-penki2 (2).jpg"))

help_history = []
help_penalty_text = []
supershot_plus = 0
supersave_plus = 0
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
penalty_router = Router()
# Функция для удаления сообщений через время
async def delete_message_after_timer(bot: Bot, chat_id: int, message_id: int, timer: int):
    await asyncio.sleep(timer)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")
        

# Управление активными играми
active_games = {}

history_1 = []
history_2 = []

# Функция для проверки, кто сейчас делает ход
def get_current_player(game):
    return game["player1"] if game["round"] % 2 == 1 else game["player2"]

# Проверка если игрок уже в игре
def is_player_in_game(user_id):
    for game in active_games.values():
        if game["player1"]["id"] == user_id or game["player2"]["id"] == user_id:
            return True
    return False

async def player_history_line(player):
    histoy = player["history"]
    history_line = ""
    for i in histoy:
        history_line+=i
    return history_line

@penalty_router.message(Command(commands=["start_penalty"]))
async def start_penalty_game(message: types.Message):

    if message.chat.type not in ["group", "supergroup"]:
        await message.reply("Эта команда доступна только в группе!")
        return 
        
    user_id = message.from_user.id
    username = message.from_user.username

    player_role = await check_player_design(user_id=user_id)

    # group_simbols_for_penalty_att.inline_keyboard.remove(player_kb)
    # group_simbols_for_penalty_att.inline_keyboard.remove(player_kb)

    await init_player_statistics(user_id=user_id)
    
    if is_player_in_game(user_id):
        await message.reply("Вы уже участвуете в игре! Завершите текущую игру, прежде чем начинать новую.")
        return

    
    sent_message = await message.reply_photo(
        photo=cached_photo_path5 if not player_role else cached_photo_path20,
        caption=f"<b>Игрок @{username}</b> вызывает на дуэль в <i>Пенальти!⚽</i>\n\n"
                "Нажмите <b>Принять вызов</b>, чтобы присоединиться!",
        parse_mode='HTML',
        reply_markup=penalty_accept_keyboard
    )

    await delete_message_after_timer(
        bot=bot,
        chat_id=sent_message.chat.id,
        message_id=sent_message.message_id,
        timer=30
    )
    

def has_message_changed(message, new_caption, new_reply_markup):
    """Проверяет, отличается ли новое сообщение или клавиатура от текущих."""
    current_caption = message.caption or ""
    current_reply_markup = message.reply_markup or None

    return (current_caption != new_caption) or (current_reply_markup != new_reply_markup)


async def safe_edit_media(message, media, caption=None, reply_markup=None, **kwargs):
    """Безопасное редактирование медиа, проверяет, изменилось ли содержимое."""
    new_caption = caption or ""
    new_reply_markup = reply_markup or None

    if not has_message_changed(message, new_caption, new_reply_markup):
        print("Сообщение не изменилось, пропускаем редактирование.")
        return

    try:
        await message.edit_media(media=media, caption=new_caption, reply_markup=new_reply_markup, **kwargs)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            print("Сообщение не изменено. Ошибка проигнорирована.")
        else:
            raise



timeouts = {}  

async def start_action_timeout(game_message_id, is_attack_phase):
    
    global timeouts

    game = active_games.get(game_message_id)
    if not game:
        return 

    # Отмена предыдущего таймера если был
    if game_message_id in timeouts:
        timeouts[game_message_id].cancel()

    # таймер
    task = asyncio.create_task(timeout_handler(game_message_id, is_attack_phase))
    timeouts[game_message_id] = task



async def timeout_handler(game_message_id, is_attack_phase):
    try:
        await asyncio.sleep(15)  # Время ожидания
        game = active_games.get(game_message_id)
        if not game:
            return

        player1 = game["player1"]
        player2 = game["player2"]
        is_player1_attacking = game["round"] % 2 == 1
        attacker = player1 if is_player1_attacking else player2
        defender = player2 if is_player1_attacking else player1

        if is_attack_phase:
            if attacker["current_action"] is None:  # Нападающий не сделал выбор    
                attacker["history"].append("🧤")
                result = f"Нападающий ({attacker['username']}) не успел выбрать. Гол не засчитан."
                game["round"] += 1
                await finish_round_or_continue(game, result)
        else:
            if defender["current_action"] is None:  # Защитник не сделал выбор
                if attacker["current_action"] is not None:
                    attacker["score"] += 1
                    attacker["history"].append("⚽")
                    result = f"Защитник ({defender['username']}) не успел выбрать. Гол засчитан!"
                else:
                    attacker["history"].append("🧤")
                    result = "Оба игрока пропустили ход. Гол не засчитан."
                game["round"] += 1

                
                await finish_round_or_continue(game, result)

    except asyncio.CancelledError:
        # Таймер был отменён
        return


async def finish_round_or_continue(game, result):
    player1 = game["player1"]
    player2 = game["player2"]

    pl_win_streak = await get_player_win_streak(user_id=game["player1"]["id"], game_id=2)
    p2_win_streak = await get_player_win_streak(user_id=game["player2"]["id"], game_id=2)
    pl1_best_win_streak = await get_player_best_win_streak(user_id=game["player1"]["id"], game_id=2)
    pl2_best_win_streak = await get_player_best_win_streak(user_id=game["player2"]["id"], game_id=2)

    request1_role = await check_user_role(player1["id"])
    player1_role = [role["role"] for role in request1_role][0]

    request2_role = await check_user_role(player2["id"])
    player2_role = [role["role"] for role in request2_role][0]

    # Условие завершения игры
    if (game["round"] >= 6 and (player1['score'] != player2['score']) and game['round'] % 2 != 0) or (game['round'] > 10):
        final_score = f"{player1['score']} : {player2['score']}\n"
        result_db = f"{player1['username']} {player1['score']}:{player2['score']} {player2['username']}"
        final_history = (
            f"{player1['username']} {''.join(player1['history'])}\n"
            f"{player2['username']} {''.join(player2['history'])}"
        )
        if player1['score'] != player2['score']:
            winner = player1['username'] if player1['score'] > player2['score'] else player2['username']
            await game["group_message"].edit_media(
                media=types.InputMediaPhoto(
                    media=cached_photo_path6,
                    caption=f"Игра окончена! •Пенальти\n\n<b>{winner}</b> победил!\n{final_score}\n{final_history}",
                    parse_mode="HTML"
                )
            )
        else:
            await game["group_message"].edit_media(
                media=types.InputMediaPhoto(
                    media=cached_photo_path6,
                    caption=f"Игра окончена! •Пенальти\n\n Ничья!\n{final_score}\n{final_history}",
                    parse_mode="HTML"
                )
            )

        # Удаление игры из активных
        del active_games[game["group_message"].message_id]
        if game["group_message"].message_id in timeouts:
            timeouts[game["group_message"].message_id].cancel()
            del timeouts[game["group_message"].message_id]

        # Логика обновления базы данных
        start_time = datetime.now()
        end_time = time.time()
        if player1['score'] > player2['score']:
            winner = player1
            loser = player2
        elif player1['score'] < player2['score']:
            winner = player2
            loser = player1
        else:
            winner = None
            loser = None

        await add_matches(
            game_id=2,
            player1_id=player1["id"],
            player2_id=player2["id"],
            result=result_db.strip(),
            start_time=start_time,
        )
        print(history_1, history_2)
        if winner == player1:
            await update_user_coins(10 if player1_role == 'player' else 20, winner["id"])
            await update_user_statistics(
                user_id=player1["id"],
                game_id=2,
                win=1,
                draw=0,
                loss=0,
                win_streak= pl_win_streak + 1,
                best_win_streak= pl1_best_win_streak if pl1_best_win_streak>pl_win_streak + 1 else pl_win_streak + 1,
                choice_1 = history_1.count('left'),
                choice_2 = history_1.count('center'),
                choice_3 = history_1.count('right'),
                match_points=10
            )
            await update_user_statistics(
                user_id=player2["id"],
                game_id=2,
                win=0,
                draw=0,
                loss=1,
                win_streak=0,
                best_win_streak= pl2_best_win_streak,
                choice_1 = history_2.count('left'),
                choice_2 = history_2.count('center'),
                choice_3 = history_2.count('right'),
                match_points=0 if await get_player_match_points(user_id=loser["id"], game_id=2) <10 else -10
            )
            history_1.clear()
            history_2.clear()
        elif winner == player2:
            await update_user_coins(10 if player2_role == 'player' else 20, winner["id"])
            await update_user_statistics(
                user_id=player2["id"],
                game_id=2,
                win=1,
                draw=0,
                loss=0,
                win_streak=p2_win_streak + 1,
                best_win_streak= pl2_best_win_streak if pl2_best_win_streak>p2_win_streak + 1 else p2_win_streak + 1,
                choice_1 = history_2.count('left'),
                choice_2 = history_2.count('center'),
                choice_3 = history_2.count('right'),
                match_points=10
            )
            await update_user_statistics(
                user_id=player1["id"],
                game_id=2,
                win=0,
                draw=0,
                loss=1,
                win_streak=0,
                best_win_streak= pl1_best_win_streak,
                choice_1 = history_1.count('left'),
                choice_2 = history_1.count('center'),
                choice_3 = history_1.count('right'),
                match_points=0 if await get_player_match_points(user_id=loser["id"], game_id=2) < 10 else -10
            )
            history_1.clear()
            history_2.clear()
        else:
            await update_user_statistics(
                user_id=player1["id"],
                game_id=2,
                win=0,
                draw=1,
                loss=0,
                win_streak=0,
                best_win_streak= pl1_best_win_streak,
                choice_1 = history_1.count('left'),
                choice_2 = history_1.count('center'),
                choice_3  =history_1.count('right'),
                match_points=3
            )
            await update_user_statistics(
                user_id=player2["id"],
                game_id=2,
                win=0,
                draw=1,
                loss=0,
                win_streak=0,
                best_win_streak=pl2_best_win_streak,
                choice_1 = history_2.count('left'),
                choice_2 = history_2.count('center'),
                choice_3  =history_2.count('right'),
                match_points=3
            )
            history_1.clear()
            history_2.clear()
    else:
        # Продолжение игры
        next_attacker = player2 if game["round"] % 2 == 0 else player1

        player1["current_action"] = None
        player2["current_action"] = None

        caption = (
            f"{result}\n\n"
            f"Счёт {player1['score']} : {player2['score']}\n\n"
            f"<b>{player1['username']}</b> {await player_history_line(player1)}\n"
            f"<b>{player2['username']}</b> {await player_history_line(player2)}\n\n"
            f"⚽{len(next_attacker['history']) + 1}-й Удар <b>{next_attacker['username']}</b>\n"
            "Выберите направление удара!"
        )
        await game["group_message"].edit_media(
            media=types.InputMediaPhoto(
                media=cached_photo_path3,
                caption=caption,
                parse_mode="HTML"
            ),
            reply_markup=group_simbols_for_penalty_att
        )

        asyncio.create_task(start_action_timeout(game["group_message"].message_id, is_attack_phase=True))


       
       

#ТУТ ПЕРВОЕ СООБЩЕНИЕ ДЛЯ ПЕРВОГО УДАРА НАПА 
@penalty_router.callback_query(lambda c: c.data == "penalty_accept")
async def handle_penalty_accept(callback_query: types.CallbackQuery):
    start_time = time.time()
    global help_history
    help_history = []
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username
    message = callback_query.message
    author_id = message.reply_to_message.from_user.id
    author_username = message.reply_to_message.from_user.username
    game_message_id = message.message_id

    game = active_games.get(game_message_id)
    player1_kb = [author_id]
    player2_kb = [user_id]

    await init_player_statistics(user_id=user_id)
    #ДЛЯ ТЕСТОВ ЭТО КОМЕНТИТЬ
    # if user_id == author_id:
    #     await callback_query.answer("Вы не можете играть против себя!", show_alert=True)
    #     return

    # Инициализация игры
    game_message = await message.answer_photo(
        photo=cached_photo_path3,
        caption=f"Игра началась!\n\n<b>{author_username}</b> VS <b>{username}</b>\n\n"
                f"⚽1-й удар <b>{author_username}</b>\n "
                "Выберите направление удара!",
        parse_mode="HTML",
        reply_markup=group_simbols_for_penalty_att
    )

    active_games[game_message.message_id] = {
        "player1": {"id": author_id, "username": author_username, "current_action": None, "score": 0, "history": []},
        "player2": {"id": user_id, "username": username, "current_action": None, "score": 0, "history": []},
        "group_message": game_message,
        "round": 1
    }

    asyncio.create_task(start_action_timeout(game_message.message_id, is_attack_phase=True))
    print(f"Время выполнения handle_penalty_accept: {time.time() - start_time:.4f} секунд")
    await callback_query.answer()




@penalty_router.callback_query(lambda c: c.data.startswith("att_"))
async def handle_attack_action(callback_query: types.CallbackQuery):
    help_penalty_text.clear()
    start_time = time.time()
    user_id = callback_query.from_user.id
    choice = callback_query.data
    global supersave_plus
    supersave_plus = 0
    game_message_id = callback_query.message.message_id
    game = active_games.get(game_message_id)

    if not game:
        await callback_query.answer("Игра не найдена!", show_alert=True)
        return

    # Проверка блокировки
    if game.get("action_locked", False):
        await callback_query.answer("Подождите, ход уже обрабатывается.", show_alert=True)
        return

    # Заблокировать действия
    game["action_locked"] = True

    try:
        player1 = game["player1"]
        player2 = game["player2"]
        is_player1_attacking = game["round"] % 2 == 1
        attacker = player1 if is_player1_attacking else player2
        defender = player2 if is_player1_attacking else player1

        if attacker["id"] != user_id:
            await callback_query.answer("Сейчас не ваш ход!", show_alert=True)
            return

        attacker["current_action"] = choice.split("_")[1]
        if attacker == player1: history_1.append(attacker["current_action"])
        else: history_2.append(attacker["current_action"])
        await callback_query.answer(f"Вы выбрали направление: {attacker['current_action'].upper()}!")

        # Задержка перед следующим шагом
        await asyncio.sleep(1)
        help_penalty_text.append(attacker["current_action"])
        

        caption = (
            f"Счёт {player1['score']} : {player2['score']}\n\n"
            f"<b>{player1['username']}</b> {await player_history_line(player1)}\n"
            f"<b>{player2['username']}</b> {await player_history_line(player2)}\n\n"
            f"🧤Ловит: <b>{defender['username']}</b>\n"
            "Угадайте направление удара."
        )

        await safe_edit_media(
            message=game["group_message"],
            media=types.InputMediaPhoto(
                media=cached_photo_path7,
                caption=caption,
                parse_mode="HTML"
            ),
            reply_markup=group_simbols_for_penalty_def
        )
        # print(group_simbols_for_penalty_def.inline_keyboard)
        defender["current_action"] = None
        asyncio.create_task(start_action_timeout(game_message_id, is_attack_phase=False))

    finally:
        # Разблокировать действия
        game["action_locked"] = False
    

    print(f"Время выполнения handle_attack_action: {time.time() - start_time:.4f} секунд")


@penalty_router.callback_query(lambda c: c.data.startswith("def_"))
async def handle_defense_action(callback_query: types.CallbackQuery):
    start_time = time.time()
    global supershot_plus
    global supersave_plus
    user_id = callback_query.from_user.id
    choice = callback_query.data
    game_message_id = callback_query.message.message_id
    game = active_games.get(game_message_id)

    if not game:
        await callback_query.answer("Игра не найдена!", show_alert=True)
        return

    # Проверка блокировки
    if game.get("action_locked", False):
        await callback_query.answer("Подождите, ход уже обрабатывается.", show_alert=True)
        return

    # Заблокировать действия
    game["action_locked"] = True

    try:
        player1 = game["player1"]
        player2 = game["player2"]
        is_player1_attacking = game["round"] % 2 == 1
        attacker = player1 if is_player1_attacking else player2
        defender = player2 if is_player1_attacking else player1
        if defender["id"] != user_id:
            await callback_query.answer("Сейчас не ваш ход!", show_alert=True)
            return

        defender["current_action"] = choice.split("_")[1]
        
        # Задержка перед завершением раунда
        await asyncio.sleep(1)

        if attacker["current_action"] == defender["current_action"]:
            attacker["history"].append("🧤")
            attacker["score"]-= supersave_plus
        else:
            attacker["score"] = attacker["score"]+ 1+supershot_plus
            attacker["history"].append("⚽")

        game["round"] += 1
        supershot_plus = 0
        result = (
            f"🏅<b>{attacker['username']}</b> забивает!"
            if attacker["history"][-1] == "⚽"
            else f"<b>{attacker['username']}</b> не забил"
        )
        await finish_round_or_continue(game, result)

    finally:
        # Разблокировать действия
        game["action_locked"] = False


    print(f"Время выполнения handle_defense_action: {time.time() - start_time:.4f} секунд")


@penalty_router.callback_query(lambda c: c.data in ["help_in_game","supershot_in_game","supersave_in_game"])
async def handle_defense_bonus(callback_query: types.CallbackQuery):
    global help_history
    user_id = callback_query.from_user.id
    user_el = await check_user_el_in_game(user_id=user_id)
    choice = callback_query.data
    if user_id not in help_history:
        if choice == "help_in_game":
            if 'Подсказка' in user_el:
                shoot_various = ['left', 'center', 'right']
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

        elif choice =="supershot_in_game":
            if 'Суперудар' in user_el:
                global supershot_plus
                print('1=!!!+!+!')
                if supershot_plus ==0:
                    supershot_plus+=1
                else: 
                    supershot_plus = 1
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
        elif choice == "supersave_in_game":
            if 'Суперсейв' in user_el:
                global supersave_plus
                print("puuuuuuppppupuuuuuuuuuuuuu")
                if supersave_plus ==0:
                    supersave_plus+=1
                else: 
                    supersave_plus = 1
                await callback_query.answer(
                            text=f"Суперсейв использован, выберите угол!",
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