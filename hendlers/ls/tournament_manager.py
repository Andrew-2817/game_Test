from aiogram import Bot, Router, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
import asyncio
from threading import Lock
from datetime import datetime, timedelta
import pytz
import re
import logging
from hendlers.ls.player import player_router, bot
from hendlers.ls.tours import   registered_users, edit_lock, cached_photo_path9, create_and_send_participants_list, get_tour_keyboard

# Настраиваем логирование
logging.basicConfig(filename="tournament.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Маршрутизатор для команд управления турнирами
manager_router = Router()

# ID администратора
admin_id = 7459734786

# Словарь для хранения информации о текущем турнире
tournament_info = {
    "scheduled": False,
    "start_time": None,  # datetime в Moscow TZ
    "task": None,  # asyncio.Task для отмены
}

# Функция ожидания времени турнира
async def schedule_tournament_start():
    moscow_tz = pytz.timezone("Europe/Moscow")
    while tournament_info["scheduled"]:
        now = datetime.now(moscow_tz)
        target_time = tournament_info["start_time"]

        wait_time = (target_time - now).total_seconds()
        if wait_time <= 0:
            await create_and_send_participants_list()
            # Сбрасываем турнир после запуска
            tournament_info["scheduled"] = False
            tournament_info["start_time"] = None
            tournament_info["task"] = None
            logging.info("Турнир запущен, состояние сброшено")
            print("Турнир запущен, состояние сброшено")
            break

        logging.info(f"Ожидание до турнира: {wait_time} секунд")
        print(f"Ожидание до турнира: {wait_time} секунд")
        await asyncio.sleep(min(wait_time, 3600))  # Проверяем каждый час

# Команда /start_tournament
@manager_router.message(Command("start_tournament"))
async def cmd_start_tournament(message: Message):
    if message.from_user.id != admin_id:
        await message.answer("Только администратор может запускать турнир!")
        return

    async with edit_lock:
        if tournament_info["scheduled"]:
            await message.answer("Турнир уже запланирован! Используйте /cancel_tournament, чтобы отменить.")
            return

        # Парсим аргументы команды
        args = message.text.split()[1:]  # Получаем аргументы после команды
        if not args:
            await message.answer(
                "Укажите время и день, например:\n"
                "/start_tournament Sunday 15:00\n"
                "или /start_tournament 2025-04-20 15:00"
            )
            return

        try:
            moscow_tz = pytz.timezone("Europe/Moscow")
            now = datetime.now(moscow_tz)

            # Пробуем разобрать как день недели + время
            if len(args) == 2 and re.match(r"\d{2}:\d{2}", args[1]):
                day_name, time_str = args
                days = {
                    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                    "friday": 4, "saturday": 5, "sunday": 6
                }
                if day_name.lower() not in days:
                    await message.answer("Неверный день недели! Используйте: Monday, Tuesday, ..., Sunday")
                    return

                target_hour, target_minute = map(int, time_str.split(":"))
                target_day = days[day_name.lower()]
                current_day = now.weekday()
                days_ahead = (target_day - current_day) % 7
                if days_ahead == 0 and (now.hour > target_hour or (now.hour == target_hour and now.minute >= target_minute)):
                    days_ahead = 7  # Если время уже прошло, планируем на следующую неделю

                target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
                target_time += timedelta(days=days_ahead)

            # Пробуем разобрать как дата + время
            elif len(args) == 2 and re.match(r"\d{4}-\d{2}-\d{2}", args[0]):
                date_str, time_str = args
                target_hour, target_minute = map(int, time_str.split(":"))
                year, month, day = map(int, date_str.split("-"))
                target_time = moscow_tz.localize(datetime(year, month, day, target_hour, target_minute))

            else:
                await message.answer("Неверный формат! Используйте: /start_tournament Sunday 15:00 или /start_tournament 2025-04-20 15:00")
                return

            # Проверяем, что время в будущем
            if target_time <= now:
                await message.answer("Укажите время в будущем!")
                return

            # Сохраняем информацию о турнире
            tournament_info["scheduled"] = True
            tournament_info["start_time"] = target_time

            # Запускаем задачу для отправки списка участников
            tournament_info["task"] = asyncio.create_task(schedule_tournament_start())

            await message.answer(
                f"Турнир запланирован на {target_time.strftime('%Y-%m-%d %H:%M')} (Москва).\n"
                "Пользователи могут регистрироваться через кнопку 'Турниры'."
            )
            logging.info(f"Турнир запланирован на {target_time}")
            print(f"Турнир запланирован на {target_time}")
        except ValueError as e:
            await message.answer("Ошибка в формате даты/времени. Пример: /start_tournament Sunday 15:00")
            logging.error(f"Ошибка парсинга времени: {e}")
            print(f"Ошибка парсинга времени: {e}")

# Команда /cancel_tournament
@manager_router.message(Command("cancel_tournament"))
async def cmd_cancel_tournament(message: Message):
    if message.from_user.id != admin_id:
        await message.answer("Только администратор может отменять турнир!")
        return

    async with edit_lock:
        if not tournament_info["scheduled"]:
            await message.answer("Нет запланированного турнира!")
            return

        # Отменяем задачу
        if tournament_info["task"]:
            tournament_info["task"].cancel()
            tournament_info["task"] = None

        # Очищаем данные
        tournament_info["scheduled"] = False
        tournament_info["start_time"] = None
        registered_users.clear()

        await message.answer("Турнир отменён, регистрация очищена.")
        logging.info("Турнир отменён")
        print("Турнир отменён")

# Команда /edit_tournament
@manager_router.message(Command("edit_tournament"))
async def cmd_edit_tournament(message: Message):
    if message.from_user.id != admin_id:
        await message.answer("Только администратор может изменять турнир!")
        return

    async with edit_lock:
        if not tournament_info["scheduled"]:
            await message.answer("Нет запланированного турнира!")
            return

        # Парсим новое время
        args = message.text.split()[1:]
        if not args:
            await message.answer(
                "Укажите новое время и день, например:\n"
                "/edit_tournament Sunday 15:00\n"
                "или /edit_tournament 2025-04-20 15:00"
            )
            return

        try:
            moscow_tz = pytz.timezone("Europe/Moscow")
            now = datetime.now(moscow_tz)

            # Пробуем разобрать как день недели + время
            if len(args) == 2 and re.match(r"\d{2}:\d{2}", args[1]):
                day_name, time_str = args
                days = {
                    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                    "friday": 4, "saturday": 5, "sunday": 6
                }
                if day_name.lower() not in days:
                    await message.answer("Неверный день недели! Используйте: Monday, Tuesday, ..., Sunday")
                    return

                target_hour, target_minute = map(int, time_str.split(":"))
                target_day = days[day_name.lower()]
                current_day = now.weekday()
                days_ahead = (target_day - current_day) % 7
                if days_ahead == 0 and (now.hour > target_hour or (now.hour == target_hour and now.minute >= target_minute)):
                    days_ahead = 7

                target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
                target_time += timedelta(days=days_ahead)

            # Пробуем разобрать как дата + время
            elif len(args) == 2 and re.match(r"\d{4}-\d{2}-\d{2}", args[0]):
                date_str, time_str = args
                target_hour, target_minute = map(int, time_str.split(":"))
                year, month, day = map(int, date_str.split("-"))
                target_time = moscow_tz.localize(datetime(year, month, day, target_hour, target_minute))

            else:
                await message.answer("Неверный формат! Используйте: /edit_tournament Sunday 15:00 или /edit_tournament 2025-04-20 15:00")
                return

            # Проверяем, что время в будущем
            if target_time <= now:
                await message.answer("Укажите время в будущем!")
                return

            # Отменяем старую задачу
            if tournament_info["task"]:
                tournament_info["task"].cancel()

            # Обновляем время
            tournament_info["start_time"] = target_time
            tournament_info["task"] = asyncio.create_task(schedule_tournament_start())

            await message.answer(
                f"Время турнира изменено на {target_time.strftime('%Y-%m-%d %H:%M')} (Москва)."
            )
            logging.info(f"Турнир изменён на {target_time}")
            print(f"Турнир изменён на {target_time}")
        except ValueError as e:
            await message.answer("Ошибка в формате даты/времени. Пример: /edit_tournament Sunday 15:00")
            logging.error(f"Ошибка парсинга времени: {e}")
            print(f"Ошибка парсинга времени: {e}")

# Обработчик кнопки "Турниры"
@manager_router.callback_query(lambda c: c.data == "start_tournaments")
async def start_reg_on_tour(callback_query: types.CallbackQuery):
    async with edit_lock:
        if not tournament_info["scheduled"]:
            try:
                await callback_query.message.edit_media(
                    media=InputMediaPhoto(
                        media=cached_photo_path9,
                        caption="Турнир не запланирован администратором."
                    ),
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Назад 🔙", callback_data="profile_back")]
                    ])
                )
            except TelegramBadRequest as e:
                logging.error(f"Ошибка Telegram: {e}")
                print(f"Ошибка Telegram: {e}")
            return

        start_time = tournament_info["start_time"].strftime("%Y-%m-%d %H:%M")
        count = len(registered_users)
        caption = (
            f"Турнир запланирован на {start_time} (Москва)\n"
            f"Регистрация закрывается за час\n\n"
            f"Участников: {count}"
        )

        try:
            await callback_query.message.edit_media(
                media=InputMediaPhoto(
                    media=cached_photo_path9,
                    caption=caption
                ),
                reply_markup=get_tour_keyboard()
            )
        except TelegramBadRequest as e:
            logging.error(f"Ошибка Telegram: {e}")
            print(f"Ошибка Telegram: {e}")

# Обработчик регистрации
@manager_router.callback_query(lambda c: c.data == "tour_reg")
async def toggle_participation(callback_query: types.CallbackQuery):
    if not tournament_info["scheduled"]:
        await callback_query.answer("Турнир не запланирован!", show_alert=True)
        return

    user_id = callback_query.from_user.id
    username = callback_query.from_user.username

    async with edit_lock:
        if user_id in registered_users:
            del registered_users[user_id]
            action = "удалена"
        else:
            registered_users[user_id] = username
            action = "добавлена"

        count = len(registered_users)
        caption = (
            f"Ваша регистрация {action}!\n"
            f"Турнир по Пенкам, участников: {count}"
        )

        try:
            await callback_query.message.edit_media(
                media=InputMediaPhoto(
                    media=cached_photo_path9,
                    caption=caption
                ),
                reply_markup=get_tour_keyboard()
            )
        except TelegramBadRequest as e:
            logging.error(f"Ошибка Telegram: {e}")
            print(f"Ошибка Telegram: {e}")

# Команда /list_participants
@manager_router.message(Command("list_participants"))
async def cmd_list_participants(message: Message):
    if message.from_user.id != admin_id:
        await message.answer("Только администратор может видеть список!")
        return
    if not registered_users:
        await message.answer("Нет зарегистрированных участников.")
        return
    participants = "\n".join([f"@{username}" for username in registered_users.values()])
    await message.answer(f"Участники:\n{participants}")
    logging.info("Админ запросил список участников")
    print("Админ запросил список участников")