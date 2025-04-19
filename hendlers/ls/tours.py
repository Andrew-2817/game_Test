from hendlers.ls.player import player_router, cached_photo_path5, cached_photo_path9, bot
from aiogram.types import CallbackQuery, InputMediaPhoto
from db import get_db_connection
from aiogram import types, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
from hendlers.ls.penalty_ls import ongoing_games, cached_photo_path3, cached_photo_path7, start_turn_timer, reset_timer, cached_photo_path6
import pytz
from datetime import datetime, timedelta
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext 
from aiogram.exceptions import TelegramBadRequest
import os 
import time 
from keyboards import tournament_attack_buttons, tournament_defense_buttons
import asyncio
from asyncio import Lock


# Словарь для хранения зарегистрированных участников (user_id: username)
registered_users = {}
# Блокировка для предотвращения одновременных изменений
edit_lock = Lock()

# Функция для получения клавиатуры с количеством участников
def get_tour_keyboard():
    count = len(registered_users)
    tour_reg = InlineKeyboardButton(text=f"Регистрация 🔥 ({count})", callback_data="tour_reg")
    tour_back = InlineKeyboardButton(text="Назад 🔙", callback_data="profile_back")
    return InlineKeyboardMarkup(inline_keyboard=[[tour_reg], [tour_back]])


confirm_button = InlineKeyboardButton(text="Подтвердить участие ✅", callback_data="confirm_participation")
keyboard = InlineKeyboardMarkup(inline_keyboard=[[confirm_button]])

async def create_and_send_participants_list():
    if not registered_users:
        message_text = "Турнира не будет"
    else:
        participants = "\n".join([f"@{username}" for username in registered_users.values()])
        message_text = f"Регистрация продолжается! Участники на данный момент:\n\n{participants}\n\nНажмите кнопку ниже, чтобы подтвердить участие."
    # раскидываем сообщения 
    for user_id in registered_users.keys():
        try:
            await bot.send_message(user_id, message_text, reply_markup=keyboard)
        except TelegramBadRequest as e:
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

    print("Список участников отправлен с кнопкой 'Подтвердить участие'.")


# задаем время турика 
async def schedule_tournament_start():
    moscow_tz = pytz.timezone('Europe/Moscow')
    
    while True:
        now = datetime.now(moscow_tz)
        print(f"Текущее время в Москве: {now}", flush=True)
        target_time = now.replace(hour=10, minute=12, second=0, microsecond=0)

        if now > target_time:
            target_time += timedelta(days=1)

        wait_time = (target_time - now).total_seconds()
        print(f"Ожидание : {wait_time} секунд", flush=True)

        await asyncio.sleep(wait_time)

        await create_and_send_participants_list()

# Запуск таймера для турнира
async def start_tournament_timer():
    await schedule_tournament_start()


confirmed_users = {}
sent_users = set()
sent_matches = set()
tournament_matches = []  # Глобальная переменная для хранения матчей
admin_start_messages = {}# Глобальная переменная для хранения матчей
matches_sent = False  # Флаг для контроля отправки матчей
admin_id = 7459734786  # ID админа

@player_router.callback_query(lambda c: c.data == "confirm_participation")
async def confirm_participation(callback_query: CallbackQuery):
    global matches_sent
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username

    if user_id in confirmed_users:
        await callback_query.answer("Вы уже подтвердили участие!", show_alert=True)
        return  

    confirmed_users[user_id] = username
    await callback_query.answer("Вы подтвердили участие!")
    print(f"Игрок @{username} ({user_id}) подтвердил участие, всего подтверждено: {len(confirmed_users)}")

    try:
        await callback_query.message.edit_text(
            text="✅ Вы подтвердили участие!", reply_markup=None
        )
    except TelegramBadRequest:
        print("Не удалось изменить сообщение, возможно, оно уже удалено.")

    await asyncio.sleep(15)
    try:
        await callback_query.message.delete()
    except TelegramBadRequest:
        print("Не удалось удалить сообщение, возможно, оно уже удалено.")

    # Проверяем, достаточно ли игроков и не отправлены ли матчи
    if len(confirmed_users) >= 2 and not matches_sent:
        print("Достаточно игроков, пытаемся отправить матчи")
        async with edit_lock:  # Используем блокировку для предотвращения гонок
            if not matches_sent:  # Двойная проверка
                await send_matchups(callback_query.bot)


def generate_fixed_bracket(players):
    total = 2 ** ((len(players) - 1).bit_length())  # Приводим количество игроков к степени 2
    players = players + ['bot'] * (total - len(players))  # Заполняем пустые места ботами
    print(f"generate_fixed_bracket: Игроки: {players}, всего: {total}")

    matches = []
    match_index = 1

    # Формируем пары для первого раунда
    for i in range(0, len(players), 2):
        player1 = players[i]
        player2 = players[i + 1]
        matches.append((player1, player2, match_index))
        match_index += 1

    print(f"generate_fixed_bracket: Сформированы матчи: {matches}")
    return matches

async def send_matchups(bot: Bot):
    global tournament_matches, sent_matches, matches_sent, sent_users, admin_start_messages

    if matches_sent:
        print("send_matchups: Повторная отправка предотвращена")
        return  # Предотвращаем повторную отправку

    user_ids = list(confirmed_users.keys())
    print(f"send_matchups: Формируем матчи для игроков: {user_ids}")
    matchups = generate_fixed_bracket(user_ids)
    tournament_matches = matchups
    sent_matches.clear()
    admin_start_messages.clear()  # Очищаем старые сообщения админа

    # Уведомление о начале турнира (одно на всех)
    if not sent_users:  # Отправляем только если ещё не отправляли
        tournament_start_message = "🎉 Турнир начался! Ожидайте свои матчи."
        for player_id in confirmed_users.keys():
            try:
                await bot.send_message(player_id, tournament_start_message)
                sent_users.add(player_id)
                print(f"send_matchups: Отправлено уведомление о начале турнира игроку {player_id}")
            except TelegramBadRequest as e:
                print(f"send_matchups: Ошибка отправки уведомления игроку {player_id}: {e}")
    else:
        print("send_matchups: Уведомление о начале турнира уже отправлено ранее")

    # Отправка матчей
    for match in matchups:
        try:
            player1, player2, match_idx = match
            # Проверяем корректность типов
            if not isinstance(player1, (int, str)) or not isinstance(player2, (int, str)):
                print(f"send_matchups: Некорректный матч {match_idx}: {match}, пропускаем")
                continue

            if (player1, player2) in sent_matches or (player2, player1) in sent_matches:
                print(f"send_matchups: Матч {match_idx} уже отправлен, пропускаем")
                continue

            sent_matches.add((player1, player2))

            if player2 == "bot":
                try:
                    await bot.send_message(player1, "🎉 Вам не нашлось соперника, вы автоматически проходите в следующий раунд!")
                    await advance_winner_in_bracket(bot, player1)
                    print(f"send_matchups: Игрок {player1} прошёл дальше из-за бота в матче {match_idx}")
                except TelegramBadRequest as e:
                    print(f"send_matchups: Ошибка отправки сообщения игроку {player1}: {e}")
                continue

            username1 = confirmed_users.get(player1, f"Игрок {player1}")
            username2 = confirmed_users.get(player2, f"Игрок {player2}")

            message_text = f"Матч {match_idx}: @{username1} vs @{username2}\nОжидайте начала!"

            try:
                await bot.send_message(player1, message_text)
                await bot.send_message(player2, message_text)
                print(f"send_matchups: Отправлено уведомление о матче {match_idx}: @{username1} vs @{username2}")
            except TelegramBadRequest as e:
                print(f"send_matchups: Ошибка отправки уведомления о матче {match_idx}: {e}")

            match_text = f"Матч {match_idx}: @{username1} vs @{username2}"
            await send_admin_start_button(bot, admin_id, match_idx, match_text)

        except ValueError as e:
            print(f"send_matchups: Ошибка распаковки матча {match}: {e}, пропускаем")
            continue

    matches_sent = True
    print(f"send_matchups: Все матчи отправлены, tournament_matches: {tournament_matches}")



async def send_admin_start_button(bot: Bot, admin_id: int, match_idx: int, match_text: str):
    if match_idx in admin_start_messages:
        return  

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Запустить матч", callback_data=f"start_tournament_game_{match_idx}")]
    ])
    message = await bot.send_message(chat_id=admin_id, text=f"{match_text} \nЗапустить матч {match_idx}", reply_markup=keyboard)
    admin_start_messages[match_idx] = message.message_id

    print(f"Создана кнопка для матча {match_idx}, admin_start_messages: {admin_start_messages}")  


async def check_and_start_next_round(bot: Bot):
    global confirmed_users, tournament_matches, sent_matches, matches_sent, admin_start_messages

    remaining_players = list(confirmed_users.keys())
    print(f"check_and_start_next_round: Осталось игроков: {remaining_players}")

    # Если остался один игрок — он победитель
    if len(remaining_players) == 1:
        winner_id = remaining_players[0]
        winner_username = confirmed_users[winner_id]
        tournament_message = f"🎉 Турнир завершён!\n🏆 Победитель: @{winner_username}\n\nСпасибо всем за участие!"
        
        for player_id in confirmed_users.keys():
            try:
                await bot.send_message(player_id, tournament_message)
                print(f"check_and_start_next_round: Отправлено сообщение о победе игроку {player_id}")
            except TelegramBadRequest as e:
                print(f"check_and_start_next_round: Ошибка отправки сообщения игроку {player_id}: {e}")
        try:
            await bot.send_message(7459734786, tournament_message)
            print("check_and_start_next_round: Отправлено сообщение о победе админу")
        except TelegramBadRequest as e:
            print(f"check_and_start_next_round: Ошибка отправки сообщения админу: {e}")

        # Сброс состояния
        confirmed_users.clear()
        sent_users.clear()
        sent_matches.clear()
        tournament_matches.clear()
        admin_start_messages.clear()
        matches_sent = False
        print("check_and_start_next_round: Турнир завершён, состояние сброшено")
        return

    # Если игроков больше одного, отправляем админу кнопку для запуска следующего раунда
    if len(remaining_players) > 1:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Запустить следующий раунд", callback_data="start_next_round")]
        ])
        try:
            await bot.send_message(
                7459734786,
                f"🛠 Все матчи текущего раунда завершены! Осталось игроков: {len(remaining_players)}. Нажмите, чтобы запустить следующий раунд.",
                reply_markup=keyboard
            )
            print("check_and_start_next_round: Отправлено сообщение админу для запуска следующего раунда")
        except TelegramBadRequest as e:
            print(f"check_and_start_next_round: Ошибка отправки сообщения админу: {e}")


async def advance_winner_in_bracket(bot: Bot, winner_id: int):
    """Продвигает победителя в следующий раунд"""
    global confirmed_users

    if winner_id not in confirmed_users:
        print(f"advance_winner_in_bracket: Ошибка: Победитель {winner_id} не найден в confirmed_users")
        return

    print(f"advance_winner_in_bracket: Игрок {winner_id} (@{confirmed_users[winner_id]}) продвинут в следующий раунд")

    # Проверяем, остались ли другие игроки
    if len(confirmed_users) <= 1:
        winner_username = confirmed_users[winner_id]
        try:
            await bot.send_message(winner_id, f"🏆 Поздравляем! Вы победитель турнира!")
            await bot.send_message(7459734786, f"🏆 Победитель: @{winner_username}")
            print(f"advance_winner_in_bracket: Объявлен победитель @{winner_username}")
        except TelegramBadRequest as e:
            print(f"advance_winner_in_bracket: Ошибка отправки сообщения о победе: {e}")
        # Сброс состояния
        confirmed_users.clear()
        sent_users.clear()
        sent_matches.clear()
        tournament_matches.clear()
        admin_start_messages.clear()
        matches_sent = False
        print("advance_winner_in_bracket: Турнир завершён, состояние сброшено")
        return


# Генерация кнопки запуска
def generate_start_game_button(match_idx: int):
    return InlineKeyboardButton(
        text=f"Запустить матч {match_idx}",
        callback_data=f"start_tournament_game_{match_idx}"
    )

@player_router.callback_query(lambda c: c.data.startswith("start_tournament_game_"))
async def start_tournament_game(callback_query: CallbackQuery):
    global tournament_matches

    try:
        match_index = int(callback_query.data.split("_")[3])
    except (IndexError, ValueError):
        await callback_query.answer("Неверный формат данных!")
        return

    admin_id = callback_query.from_user.id
    if admin_id != 7459734786:
        await callback_query.answer("Только администратор может запускать игру!", show_alert=True)
        return

    print(f"Текущий список матчей: {tournament_matches}")

    # Ищем матч по индексу
    match = next((m for m in tournament_matches if m[2] == match_index), None)

    if not match:
        await callback_query.answer("Матч не найден или уже запущен.")
        return

    player_one, player_two, _ = match
    tournament_matches = [m for m in tournament_matches if m[2] != match_index]  # Удаляем запущенный матч

    if player_two == "bot":
        await advance_winner_in_bracket(bot=callback_query.bot, winner_id=player_one)
        return

    await callback_query.answer("Матч запущен!")

    game = ongoing_games.setdefault(player_one, {
        "attacker": player_one,
        "defender": player_two,
        "round": 1,
        "scores": {player_one: 0, player_two: 0},
        "state": "waiting_for_attack",
        "current_attacker": player_one,
        "current_defender": player_two,
        "history": {player_one: '', player_two: ''},
        "messages": {},
        "usernames": {
            player_one: (await callback_query.bot.get_chat(player_one)).username or f"Игрок {player_one}",
            player_two: (await callback_query.bot.get_chat(player_two)).username or f"Игрок {player_two}"
        }
    })

    attack_message = await callback_query.bot.send_photo(
        chat_id=player_one,
        photo=cached_photo_path3,
        caption=f"Вы бьёте первым!\n Счёт: \n<b>{game['usernames'][player_one]}</b> {game['scores'][player_one]} - {game['scores'][player_two]} <b>{game['usernames'][player_two]}</b>\n"
                "Выберите направление удара ⚽",
        parse_mode='HTML',
        reply_markup=tournament_attack_buttons,
    )

    wait_message = await callback_query.bot.send_photo(
        chat_id=player_two,
        photo=cached_photo_path7,
        parse_mode='HTML',
        caption=f"Счёт: \n<b>{game['usernames'][game['attacker']]}</b> {game['scores'][game['attacker']]} - {game['scores'][game['defender']]} <b>{game['usernames'][game['defender']]}</b>\n"
                "Ожидайте, пока противник выполнит удар ⚽",
    )

    game["messages"][player_one] = attack_message.message_id
    game["messages"][player_two] = wait_message.message_id

    await start_turn_timer(game, callback_query, player_one)



# Обработчик атаки в турнире
@player_router.callback_query(lambda c: c.data.startswith("tournament_attack_"))
async def handle_tournament_attack(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    game = next((g for g in ongoing_games.values() if g.get("current_attacker") == user_id), None)

    if not game or game["state"] != "waiting_for_attack":
        await callback_query.answer("Это не ваш ход!")
        return

    # Сброс таймера перед атакой
    await reset_timer(user_id)

    # Защита от повторного выбора удара
    if game.get("attack_locked"):
        await callback_query.answer("Вы уже выбрали направление удара!")
        return

    game["attack_locked"] = True
    attack_direction = callback_query.data.split("_")[-1]
    game["attack"] = attack_direction
    game["state"] = "waiting_for_defense"

    # Обновляем сообщение атакующего
    await callback_query.bot.edit_message_media(
        chat_id=user_id,
        message_id=game["messages"][user_id],
        media=types.InputMediaPhoto(
            media=cached_photo_path3,
            caption="Вы выбрали направление удара. Ожидайте, пока противник защитится ⚽",
        ),
    )

    # Обновляем сообщение защитника
    await callback_query.bot.edit_message_media(
        chat_id=game["current_defender"],
        message_id=game["messages"][game["current_defender"]],
        media=types.InputMediaPhoto(
            media=cached_photo_path7,
            caption=(
                f"Противник бьёт! \nСчёт:\n"
                f"<b>{game['usernames'][game['attacker']]}</b> {game['scores'][game['attacker']]} - "
                f"{game['scores'][game['defender']]} <b>{game['usernames'][game['defender']]}</b>\n\n"
                f"История ударов\n"
                f"<b>{game['usernames'][game['attacker']]}</b>: {game['history'][game['attacker']]}\n"
                f"<b>{game['usernames'][game['defender']]}</b>: {game['history'][game['defender']]}\n"
                "Выберите направление для защиты 🧤"
            ),
            parse_mode='HTML',
        ),
        reply_markup=tournament_defense_buttons,
    )

    # Запускаем таймер для защитника
    await start_turn_timer(game, callback_query, game["current_defender"])




@player_router.callback_query(lambda c: c.data.startswith("tournament_defense_"))
async def handle_tournament_defense(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    game = next((g for g in ongoing_games.values() if g.get("current_defender") == user_id), None)

    if not game or game["state"] != "waiting_for_defense":
        await callback_query.answer("Это не ваш ход!")
        return

    # Сброс таймера перед защитой
    await reset_timer(user_id)

    # Блокировка повторных нажатий
    if game.get("defense_locked"):
        await callback_query.answer("Вы уже выбрали направление защиты!")
        return

    game["defense_locked"] = True
    defense_direction = callback_query.data.split("_")[-1]
    attack_direction = game["attack"]
    attacker_id = game["current_attacker"]
    defender_id = game["current_defender"]

    # Определяем результат удара
    if attack_direction == defense_direction:
        result = "Удар отбит! Отличная защита! 🧤"
        game['history'][attacker_id] += '🧤'
    else:
        result = "Вы не смогли защититься! ⚽"
        game['history'][attacker_id] += '⚽'
        game["scores"][attacker_id] += 1

    # Сообщения для игроков
    result_message = (
        f"{result}\n\nСчёт: {game['usernames'][attacker_id]} {game['scores'][attacker_id]} - "
        f"{game['usernames'][defender_id]} {game['scores'][defender_id]}\n\n"
    )

    # Удаляем сообщения игроков
    try:
        await callback_query.bot.delete_message(chat_id=attacker_id, message_id=game["messages"][attacker_id])
        await callback_query.bot.delete_message(chat_id=defender_id, message_id=game["messages"][defender_id])
    except TelegramBadRequest as e:
        print(f"Ошибка удаления сообщений игроков: {e}")

    # Проверка на завершение игры
    if game["round"] < 6 or (game["round"] < 10 and game["scores"][game["attacker"]] == game["scores"][game["defender"]]):
        # Переключение ролей
        game["round"] += 1
        game["current_attacker"], game["current_defender"] = game["current_defender"], game["current_attacker"]
        game["state"] = "waiting_for_attack"
        game.pop("attack_locked", None)
        game.pop("defense_locked", None)

        # Новое сообщение для следующего атакующего
        next_attacker_id = game["current_attacker"]
        try:
            attack_message = await callback_query.bot.send_photo(
                chat_id=next_attacker_id,
                photo=cached_photo_path3,
                caption=(f"Теперь ваша очередь бить! \n\nСчёт:\n"
                         f"<b>{game['usernames'][game['attacker']]}</b> {game['scores'][game['attacker']]} - "
                         f"{game['scores'][game['defender']]} <b>{game['usernames'][game['defender']]}</b>\n\n"
                         f"История ударов\n"
                         f"<b>{game['usernames'][game['attacker']]}</b>: {game['history'][game['attacker']]}\n"
                         f"<b>{game['usernames'][game['defender']]}</b>: {game['history'][game['defender']]}\n\n"
                         "Выберите направление удара ⚽"),
                parse_mode='HTML',
                reply_markup=tournament_attack_buttons,
            )
            game["messages"][next_attacker_id] = attack_message.message_id
        except TelegramBadRequest as e:
            print(f"Ошибка отправки сообщения атакующему {next_attacker_id}: {e}")

        # Уведомляем защитника ожидать
        try:
            defender_wait_message = await callback_query.bot.send_photo(
                chat_id=game["current_defender"],
                photo=cached_photo_path7,
                caption="Ожидайте, пока противник выполнит удар ⚽\n",
            )
            game["messages"][game["current_defender"]] = defender_wait_message.message_id
        except TelegramBadRequest as e:
            print(f"Ошибка отправки сообщения защитнику {game['current_defender']}: {e}")

        # Запускаем таймер для атакующего
        await start_turn_timer(game, callback_query, next_attacker_id)
    else:
        # Завершение игры
        final_message = "Игра завершена!\n"

        if game["scores"][game["attacker"]] > game["scores"][game["defender"]]:
            final_message += f"🎉 Победил <b>{game['usernames'][game['attacker']]}</b>!\n\n"
            winner_id = game["attacker"]
            loser_id = game["defender"]
        elif game["scores"][game["attacker"]] < game["scores"][game["defender"]]:
            final_message += f"🎉 Победил <b>{game['usernames'][game['defender']]}</b>!\n"
            winner_id = game["defender"]
            loser_id = game["attacker"]
        else:
            final_message += "🤝 Ничья!\n"
            winner_id = None
            loser_id = None

        final_message += (
            f"Счёт:\n"
            f"<b>{game['usernames'][game['attacker']]}</b>: {game['scores'][game['attacker']]}\n"
            f"<b>{game['usernames'][game['defender']]}</b>: {game['scores'][game['defender']]}\n\n"
            f"История ударов\n"
            f"<b>{game['usernames'][game['attacker']]}</b>: {game['history'][game['attacker']]}\n"
            f"<b>{game['usernames'][game['defender']]}</b>: {game['history'][game['defender']]}\n"
        )

        for player_id in [game["attacker"], game["defender"]]:
            try:
                await callback_query.bot.send_photo(
                    chat_id=player_id,
                    photo=cached_photo_path6,
                    caption=final_message,
                    parse_mode='HTML',
                )
                print(f"Отправлено сообщение о завершении игры игроку {player_id}")
            except TelegramBadRequest as e:
                print(f"Ошибка отправки сообщения игроку {player_id}: {e}")

        # Удаляем проигравшего из турнира, если есть
        if loser_id:
            del confirmed_users[loser_id]
            try:
                await callback_query.bot.send_message(
                    7459734786,
                    f"Игрок @{game['usernames'][loser_id]} удалён из турнира."
                )
                print(f"Игрок @{game['usernames'][loser_id]} удалён из турнира")
            except TelegramBadRequest as e:
                print(f"Ошибка отправки сообщения админу: {e}")

        # Удаляем игру из списка
        ongoing_games.pop(game["attacker"], None)
        ongoing_games.pop(game["defender"], None)

        # Проверяем, остались ли активные матчи
        if not any(g for g in ongoing_games.values() if g.get("state") in ["waiting_for_attack", "waiting_for_defense"]):
            await check_and_start_next_round(callback_query.bot)
            print("Все матчи раунда завершены, вызвана check_and_start_next_round")


@player_router.callback_query(lambda c: c.data == "start_next_round")
async def start_next_round(callback_query: CallbackQuery):
    global confirmed_users, tournament_matches, sent_matches, matches_sent

    admin_id = callback_query.from_user.id
    if admin_id != 7459734786:
        await callback_query.answer("Только администратор может запускать раунд!", show_alert=True)
        return

    remaining_players = list(confirmed_users.keys())
    print(f"start_next_round: Запуск раунда, игроков: {remaining_players}")

    if len(remaining_players) < 2:
        await callback_query.answer("Недостаточно игроков для нового раунда!", show_alert=True)
        print("start_next_round: Ошибка: Недостаточно игроков для нового раунда")
        return

    # Формируем новый раунд с помощью generate_fixed_bracket
    random.shuffle(remaining_players)
    new_matches = generate_fixed_bracket(remaining_players)

    tournament_matches = new_matches
    matches_sent = False  # Сбрасываем флаг перед отправкой новых матчей

    await send_matchups(callback_query.bot)
    await callback_query.answer("Следующий раунд запущен!")
    
    # Удаляем сообщение с кнопкой
    try:
        await callback_query.message.delete()
        print("start_next_round: Сообщение с кнопкой запуска раунда удалено")
    except TelegramBadRequest:
        print("start_next_round: Не удалось удалить сообщение с кнопкой запуска раунда")
    
    print(f"start_next_round: Запущен следующий раунд, новые матчи: {new_matches}")