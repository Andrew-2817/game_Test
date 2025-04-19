from datetime import datetime
from aiogram import types
import os
from hendlers.ls.player  import player_router, bot, man, cached_photo_path17, cached_photo_path5, cached_photo_path3, cached_photo_path15, cached_photo_path16, cached_photo_path20, cached_photo_path21, cached_photo_path22, cached_photo_path23, cached_photo_path25, cached_photo_path27
from aiogram.types import CallbackQuery, InputMediaPhoto, UserProfilePhotos
from db_moves.add_db import  change_user_design, remove_loss_in_game, update_days_for_user, buy_premium_or_check_end_date, shop_bonus_for_premium, update_user_statistics
from db_moves.get_db import  check_player_design, check_user_el_in_game, check_user_role, display_main_statistics, display_total_days, time_difference_premium
from keyboards import profile_keyboard, history_of_matches_keyboard, history_of_matches_back_keyboard, extended_static_keyboard, remove_loss_keyboard
from db import get_db_connection
import time


@player_router.callback_query(lambda c: c.data == "start_profile")
async def bot_profile(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username

    await update_days_for_user(user_id)
    user_data = {
        "total_days_in_game": (await display_total_days(user_id=user_id))[0]["total_days_in_game"],
        "main_statistic": await display_main_statistics(user_id=user_id)
    }
    request_role = await check_user_role(user_id)
    player_role = [role["role"] for role in request_role][0]

    premium_smile = '👑' if player_role == 'premium' else ''

    total_days_in_game = user_data["total_days_in_game"]
    main_statistic = user_data["main_statistic"]
    cuefa_win = main_statistic[0]["wins"]
    penalty_win = main_statistic[1]["wins"]
    win_21 = main_statistic[2]['wins']
    stakanchiki_win = main_statistic[3]['wins']

    # Получение фото профиля
    user_profile_photo: UserProfilePhotos = await bot.get_user_profile_photos(user_id)
    if user_profile_photo.total_count > 0 and len(user_profile_photo.photos[0]) > 0:
        file_id = user_profile_photo.photos[0][0].file_id
    else:
        print('У пользователя нет фото в профиле.')
        file_id = man 
    
    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=file_id,
            caption=f"<b>{username} {premium_smile}</b>\n\n"
                    "Общая статистика:\n\n"
                    f"Количество дней в игре: {total_days_in_game}\n"
                    f"Побед в <b>Цуефа 🪨✂️🧻</b>: {cuefa_win}\n"
                    f"Побед в <b>Пенальти ⚽</b>: {penalty_win}\n"
                    f"Побед в <b>21 ♠️♥️</b>: {win_21}\n"
                    f"Побед в <b>Сокровища 💰🗝️</b>: {stakanchiki_win}\n",
            parse_mode='HTML'
        ),
        reply_markup=profile_keyboard
    )

#Меню просмотра истории матчей 
@player_router.callback_query(lambda c: c.data == "history_of_matches")
async def bot_info_tournaments(callback_query: CallbackQuery):
    start_time = time.time()

    await callback_query.message.delete()
   
    new_message = await callback_query.message.answer(
        text=f"Здесь ты можешь посмотреть историю последних 10 матчей по каждой игре",
        parse_mode="HTML",
        reply_markup=history_of_matches_keyboard
    )

    end_time = time.time()
    print(f"Время срабатывания кнопки История матчей: {end_time - start_time:.2f} секунд")



@player_router.callback_query(lambda c: c.data == "history_penalty")
async def bot_info_tournaments(callback_query: CallbackQuery):
    start_time = time.time()
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username

    player_role = await check_player_design(user_id)

   
    conn = await get_db_connection()
    results = await conn.fetch("""
        SELECT result
        FROM matches 
        WHERE (player1_id = $1 OR player2_id = $1) and game_id = 2
        ORDER BY match_id DESC LIMIT 10
    """, user_id)
    await conn.close()

    last_10_matches = [row["result"] for row in results]

   
    last_mas = []
    for i in last_10_matches:
        loc_el = i.split(" ")
        result_str = ""
        for j in loc_el:
            if j == username:
                j = f"<b>{j}</b>"
            result_str += j + " "
        last_mas.append(result_str.strip())

    rez = f"Последние 10 матчей:\n" + "\n".join(str(result) for result in last_mas)

    

    # Отправляем ответ
    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path5 if not player_role else cached_photo_path20,
            caption=f"История матчей <b>Пенальти ⚽</b>\n\n {rez}",
            parse_mode="HTML",
        ),
        reply_markup=history_of_matches_back_keyboard
    )

    end_time = time.time()
    print(f"Время срабатывания кнопки История матчей: {end_time - start_time:.2f} секунд")

@player_router.callback_query(lambda c: c.data == "history_cuefa")
async def bot_info_tournaments(callback_query: CallbackQuery):
    start_time = time.time()
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username

    player_role = await check_player_design(user_id)

   
    conn = await get_db_connection()
    results = await conn.fetch("""
        SELECT result
        FROM matches 
        WHERE (player1_id = $1 OR player2_id = $1) and game_id = 1
        ORDER BY match_id DESC LIMIT 10
    """, user_id)
    await conn.close()

    last_10_matches = [row["result"] for row in results]

    
    last_mas = []
    for i in last_10_matches:
        loc_el = i.split(" ")
        result_str = ""
        for j in loc_el:
            if j == username:
                j = f"<b>{j}</b>"
            result_str += j + " "
        last_mas.append(result_str.strip())

    rez = f"Последние 10 матчей:\n" + "\n".join(str(result) for result in last_mas)

   
    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path3 if not player_role else cached_photo_path21,
            caption=f"История матчей <b>Цуефа 🪨✂️📃</b>\n\n {rez}",
            parse_mode="HTML",
        ),
        reply_markup=history_of_matches_back_keyboard
    )

    end_time = time.time()
    print(f"Время срабатывания кнопки История матчей: {end_time - start_time:.2f} секунд")

@player_router.callback_query(lambda c: c.data == "history_stakanchiki")
async def bot_info_tournaments(callback_query: CallbackQuery):
    start_time = time.time()
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username

    player_role = await check_player_design(user_id)

   
    conn = await get_db_connection()
    results = await conn.fetch("""
        SELECT result
        FROM matches 
        WHERE (player1_id = $1 OR player2_id = $1) and game_id = 4
        ORDER BY match_id DESC LIMIT 10
    """, user_id)
    await conn.close()

    last_10_matches = [row["result"] for row in results]

    
    last_mas = []
    for i in last_10_matches:
        loc_el = i.split(" ")
        result_str = ""
        for j in loc_el:
            if j == username:
                j = f"<b>{j}</b>"
            result_str += j + " "
        last_mas.append(result_str.strip())

    rez = f"Последние 10 матчей:\n" + "\n".join(str(result) for result in last_mas)

    
    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path15 if not player_role else cached_photo_path23,
            caption=f"История матчей <b>Сокровища 💰🗝️</b>\n\n {rez}",
            parse_mode="HTML",
        ),
        reply_markup=history_of_matches_back_keyboard
    )

    end_time = time.time()
    print(f"Время срабатывания кнопки История матчей: {end_time - start_time:.2f} секунд")

@player_router.callback_query(lambda c: c.data == "history_21")
async def bot_info_tournaments(callback_query: CallbackQuery):
    start_time = time.time()
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username

    player_role = await check_player_design(user_id)

    conn = await get_db_connection()
    results = await conn.fetch("""
        SELECT result
        FROM matches 
        WHERE (player1_id = $1 OR player2_id = $1) and game_id = 3
        ORDER BY match_id DESC LIMIT 10
    """, user_id)
    await conn.close()

    last_10_matches = [row["result"] for row in results]

    # Формироваcние текста
    last_mas = []
    for i in last_10_matches:
        loc_el = i.split(" ")
        result_str = ""
        for j in loc_el:
            if j == username:
                j = f"<b>{j}</b>"
            result_str += j + " "
        last_mas.append(result_str.strip())

    rez = f"Последние 10 матчей:\n" + "\n".join(str(result) for result in last_mas)

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path17 if player_role else cached_photo_path22,
            caption=f"История матчей <b>21 ♠️♥️</b>\n\n {rez}",
            parse_mode="HTML",
        ),
        reply_markup=history_of_matches_back_keyboard
    )

    end_time = time.time()
    print(f"Время срабатывания кнопки История матчей: {end_time - start_time:.2f} секунд")

#Полная стата
@player_router.callback_query(lambda c: c.data == "extended_static")
async def bot_info_tournaments(callback_query: CallbackQuery):
    start_time = time.time()
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username
    
    conn = await get_db_connection()
    all_statistic = await display_main_statistics(user_id=user_id)
    results_21 = await conn.fetch("""
        SELECT result
        FROM matches 
        WHERE (player1_id = $1 OR player2_id = $1) and game_id = 3
    """, user_id)
    all_21_matches = [row["result"].split(" ") for row in results_21]
    all_21_matches_score = [row[1].split(":") for row in all_21_matches]

    request_role = await check_user_role(user_id)
    player_role = [role["role"] for role in request_role][0]

    player_design = await check_player_design(user_id)

    bj_count = 0
    opponent_list = []
    for i in range(len(all_21_matches)):
        if all_21_matches_score[i][0] == '21':
            if all_21_matches[i][0] == username:
                bj_count+=1
        if all_21_matches_score[i][1] == '21':
            if all_21_matches[i][2] == username:
                bj_count+=1
        if all_21_matches[i][0] != username:
            opponent_list.append(all_21_matches[i][0])
        if all_21_matches[i][2] != username:
            opponent_list.append(all_21_matches[i][2])
    opponent_set_list = set(opponent_list)
    op_name_21 = ''
    op_count_21 = 0
    for i in opponent_set_list:
        if opponent_list.count(i) >= op_count_21:
            op_name_21 = i
            op_count_21 = opponent_list.count(i)
    print(op_name_21, op_count_21)

    async def often_opponent(user_id, game_id, username):
        results = await conn.fetch("""
        SELECT result
        FROM matches 
        WHERE (player1_id = $1 OR player2_id = $1) and game_id = $2
        """, user_id, game_id)
        all_matches = [row["result"].split(" ") for row in results]
        print(all_matches)
        opponent_list = []
        for i in range(len(all_matches)):
            if all_matches[i][0] != username:
                opponent_list.append(all_matches[i][0])
            if all_matches[i][2] != username:
                opponent_list.append(all_matches[i][2])
        opponent_set_list = set(opponent_list)
        print(opponent_list)
        op_name = ''
        op_count = 0
        for i in opponent_set_list:
            if opponent_list.count(i) >= op_count:
                op_name = i
                op_count = opponent_list.count(i)
        return [op_name, op_count]
    
    op_cuefa = await often_opponent(user_id=user_id, game_id=1, username=username)
    op_penalty = await often_opponent(user_id=user_id, game_id=2, username=username)
    op_21 = [op_name_21, op_count_21]
    op_gold = await often_opponent(user_id=user_id, game_id=4, username=username)
    await conn.close()
    if not all_statistic or len(all_statistic) < 4:
        
        all_statistic = [
            {"wins": 0, "draws": 0, "losses": 0, "win_streak": 0, "best_win_streak": 0, "choice_1": 0, "choice_2": 0, "choice_3": 0},  # Цуефа
            {"wins": 0, "draws": 0, "losses": 0, "win_streak": 0, "best_win_streak": 0, "choice_1": 0, "choice_2": 0, "choice_3": 0},  # Пенальти
            {"wins": 0, "draws": 0, "losses": 0, "win_streak": 0, "best_win_streak": 0, "choice_1": 0, "choice_2": 0, "choice_3": 0},  # 21
            {"wins": 0, "draws": 0, "losses": 0, "win_streak": 0, "best_win_streak": 0, "choice_1": 0, "choice_2": 0, "choice_3": 0}   # Сокровищв
        ]
   
    cuefa_wins = all_statistic[0]["wins"]
    cuefa_draws = all_statistic[0]["draws"]
    cuefa_losses = all_statistic[0]["losses"]
    cuefa_win_streak = all_statistic[0]["win_streak"]
    cuefa_best_win_streak = all_statistic[0]["best_win_streak"]
    cuefa_total_games = cuefa_wins + cuefa_draws + cuefa_losses
    cuefa_percent_wins = round((cuefa_wins / cuefa_total_games) * 100) if cuefa_total_games > 0 else 0
    cuefa_choice1 = all_statistic[0]["choice_1"]
    cuefa_choice2 = all_statistic[0]["choice_2"]
    cuefa_choice3 = all_statistic[0]["choice_3"]

    penalty_wins = all_statistic[1]["wins"]
    penalty_draws = all_statistic[1]["draws"]
    penalty_losses = all_statistic[1]["losses"]
    penalty_win_streak = all_statistic[1]["win_streak"]
    penalty_best_win_streak = all_statistic[1]["best_win_streak"]
    penalty_total_games = penalty_wins + penalty_draws + penalty_losses
    penalty_percent_wins = round((penalty_wins / penalty_total_games) * 100) if penalty_total_games > 0 else 0
    penalty_choice1 = all_statistic[1]["choice_1"]
    penalty_choice2 = all_statistic[1]["choice_2"]
    penalty_choice3 = all_statistic[1]["choice_3"]

    ochko_wins = all_statistic[2]["wins"]
    ochko_draws = all_statistic[2]["draws"]
    ochko_losses = all_statistic[2]["losses"]
    ochko_win_streak = all_statistic[2]["win_streak"]
    ochko_best_win_streak = all_statistic[2]["best_win_streak"]
    ochko_total_games = ochko_wins + ochko_draws + ochko_losses
    ochko_percent_wins = round((ochko_wins / ochko_total_games) * 100) if ochko_total_games > 0 else 0

    stakanchiki_wins = all_statistic[3]["wins"]
    stakanchiki_draws = all_statistic[3]["draws"]
    stakanchiki_losses = all_statistic[3]["losses"]
    stakanchiki_win_streak = all_statistic[3]["win_streak"]
    stakanchiki_best_win_streak = all_statistic[3]["best_win_streak"]
    stakanchiki_total_games = stakanchiki_wins + stakanchiki_draws + stakanchiki_losses
    stakanchiki_percent_wins = round((stakanchiki_wins / stakanchiki_total_games) * 100) if stakanchiki_total_games > 0 else 0
    stakanchiki_choice1 = all_statistic[3]["choice_1"]
    stakanchiki_choice2 = all_statistic[3]["choice_2"]
    stakanchiki_choice3 = all_statistic[3]["choice_3"]

    # Подготовка текста для вывода
    caption_premium = (
        f"<b>Полная статистика</b>\n\n"
        " ▸ Цуефа 🪨✂️📃\n"
        " Победа ∙ Ничья ∙ Поражение\n"
        f"{' ' * (6 - len(str(cuefa_wins)) + 1)}{cuefa_wins}{' ' * (16 - len(str(cuefa_wins)) - len(str(cuefa_draws)) + 1)}{cuefa_draws}{' ' * (19 - len(str(cuefa_draws)) + 1 - len(str(cuefa_losses)) - len(str(cuefa_wins)) + 1)}{cuefa_losses}\n"
        f"История выбора:\n"
        f" ⁃ Камень    🪨:{cuefa_choice1} \n ⁃ Ножницы✂️:{cuefa_choice2} \n ⁃ Бумага     📃:{cuefa_choice3}\n"
        f" Самый частый соперник:\n <b>{op_cuefa[0]}({op_cuefa[1]})</b>\n"
        f" 🎯Процент побед: {cuefa_percent_wins}%\n"
        f" ⭐Серия побед: {cuefa_win_streak} \n"
        f" 🏅Лучшая Серия побед: {cuefa_best_win_streak}\n\n"
        " ▸ Пенальти ⚽\n"
        " Победа ∙ Ничья ∙ Поражение\n"
        f"{' ' * (6 - len(str(penalty_wins)) + 1)}{penalty_wins}{' ' * (16 - len(str(penalty_wins)) - len(str(penalty_draws)) + 1)}{penalty_draws}{' ' * (19 - len(str(penalty_draws)) + 1 - len(str(penalty_losses)) - len(str(penalty_wins)) + 1)}{penalty_losses}\n"
        f"История ударов:\n"
        f" ⁃ Лево  ⬅️:{penalty_choice1} \n ⁃ Центр⬆️:{penalty_choice2} \n ⁃ Право➡️:{penalty_choice3}\n"
        f" Самый частый соперник:\n <b>{op_penalty[0]}({op_penalty[1]})</b>\n"
        f" 🎯Процент побед: {penalty_percent_wins}%\n"
        f" ⭐Серия побед: {penalty_win_streak} \n"
        f" 🏅Лучшая Серия побед: {penalty_best_win_streak}\n\n"
        " ▸ 21 ♠️♥️\n"
        " Победа ∙ Ничья ∙ Поражение\n"
        f"{' ' * (6 - len(str(ochko_wins)) + 1)}{ochko_wins}{' ' * (16 - len(str(ochko_wins)) - len(str(ochko_draws)) + 1)}{ochko_draws}{' ' * (19 - len(str(ochko_draws)) + 1 - len(str(ochko_losses)) - len(str(ochko_wins)) + 1)}{ochko_losses}\n"
        f" Число выпадения <b>Очко</b>:{bj_count}\n"
        f" Самый частый соперник:\n <b>{op_21[0]}({op_21[1]})</b>\n"
        f" 🎯Процент побед: {ochko_percent_wins}%\n"
        f" ⭐Серия побед: {ochko_win_streak}\n"
        f" 🏅Лучшая Серия побед: {ochko_best_win_streak}\n\n"
        " ▸ Сокровища 💰🗝️\n"
        " Победа ∙ Ничья ∙ Поражение\n"
        f"{' ' * (6 - len(str(stakanchiki_wins)) + 1)}{stakanchiki_wins}{' ' * (16 - len(str(stakanchiki_wins)) - len(str(stakanchiki_draws)) + 1)}{stakanchiki_draws}{' ' * (19 - len(str(stakanchiki_draws)) + 1 - len(str(stakanchiki_losses)) - len(str(stakanchiki_wins)) + 1)}{stakanchiki_losses}\n"
        f"История выбора:\n"
        f" ⁃ Лево  🎁:{stakanchiki_choice1} \n ⁃ Центр🎁:{stakanchiki_choice2} \n ⁃ Право🎁:{stakanchiki_choice3}\n"
        f" Самый частый соперник:\n <b>{op_gold[0]}({op_gold[1]})</b>\n"
        f" 🎯Процент побед: {stakanchiki_percent_wins}%\n"
        f" ⭐Серия побед: {stakanchiki_win_streak}\n"
        f" 🏅Лучшая Серия побед: {stakanchiki_best_win_streak}\n\n"
    )
    default_caption = (
        f"<b>Полная статистика</b>\n\n"
        " ▸ Цуефа 🪨✂️📃\n"
        " Победа ∙ Ничья ∙ Поражение\n"
        f"{' ' * (6 - len(str(cuefa_wins)) + 1)}{cuefa_wins}{' ' * (16 - len(str(cuefa_wins)) - len(str(cuefa_draws)) + 1)}{cuefa_draws}{' ' * (19 - len(str(cuefa_draws)) + 1 - len(str(cuefa_losses)) - len(str(cuefa_wins)) + 1)}{cuefa_losses}\n"
        f" 🎯Процент побед: {cuefa_percent_wins}%\n"
        f" ⭐Серия побед: {cuefa_win_streak}\n"
        " ▸ Пенальти ⚽\n"
        " Победа ∙ Ничья ∙ Поражение\n"
        f"{' ' * (6 - len(str(penalty_wins)) + 1)}{penalty_wins}{' ' * (16 - len(str(penalty_wins)) - len(str(penalty_draws)) + 1)}{penalty_draws}{' ' * (19 - len(str(penalty_draws)) + 1 - len(str(penalty_losses)) - len(str(penalty_wins)) + 1)}{penalty_losses}\n"
        f" 🎯Процент побед: {penalty_percent_wins}%\n"
        f" ⭐Серия побед: {penalty_win_streak}\n"
        " ▸ 21 ♠️♥️\n"
        " Победа ∙ Ничья ∙ Поражение\n"
        f"{' ' * (6 - len(str(ochko_wins)) + 1)}{ochko_wins}{' ' * (16 - len(str(ochko_wins)) - len(str(ochko_draws)) + 1)}{ochko_draws}{' ' * (19 - len(str(ochko_draws)) + 1 - len(str(ochko_losses)) - len(str(ochko_wins)) + 1)}{ochko_losses}\n"
        f" 🎯Процент побед: {ochko_percent_wins}%\n"
        f" ⭐Серия побед: {ochko_win_streak}\n"
        " ▸ Сокровища 💰🗝️\n"
        " Победа ∙ Ничья ∙ Поражение\n"
        f"{' ' * (6 - len(str(stakanchiki_wins)) + 1)}{stakanchiki_wins}{' ' * (16 - len(str(stakanchiki_wins)) - len(str(stakanchiki_draws)) + 1)}{stakanchiki_draws}{' ' * (19 - len(str(stakanchiki_draws)) + 1 - len(str(stakanchiki_losses)) - len(str(stakanchiki_wins)) + 1)}{stakanchiki_losses}\n"
        f" 🎯Процент побед: {stakanchiki_percent_wins}%\n"
        f" ⭐Серия побед: {stakanchiki_win_streak}\n"
    )

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path16 if player_design else cached_photo_path25,  
            caption=caption_premium if player_role == 'premium' else default_caption,
            parse_mode='HTML'
        ),
        reply_markup=extended_static_keyboard
    )
    end_time = time.time()
    print(f"Время срабатывания кнопки Инфо->Подробнее: {end_time - start_time:.2f} секунд")

@player_router.callback_query(lambda c: c.data == "remove_loss")
async def remove_loss(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path27,  
            caption="Выберите в какой игре отменить поражение",
            parse_mode='HTML'
        ),
        reply_markup=remove_loss_keyboard
    )
@player_router.callback_query(lambda c: c.data in ["remove_loss_penality","remove_loss_RPS", "remove_loss_21", "remove_loss_treasures"])
async def remove_loss(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_bonuses = await check_user_el_in_game(user_id = user_id)
    game_name = callback_query.data
    if "Отмена поражения" not in user_bonuses:
         await callback_query.answer("У вас нет этого бонуса")
    else:
        if game_name == 'remove_loss_RPS':
            await remove_loss_in_game(user_id=user_id, game_id=1)
            await callback_query.answer("Бонус успешно применен")
        elif game_name == 'remove_loss_penality':
            await remove_loss_in_game(user_id=user_id, game_id=2)
            await callback_query.answer("Бонус успешно применен")
        elif game_name == 'remove_loss_treasures':
            await remove_loss_in_game(user_id=user_id, game_id=4)
            await callback_query.answer("Бонус успешно применен")
        elif game_name == 'remove_loss_penality_21':
            await remove_loss_in_game(user_id=user_id, game_id=3)
            await callback_query.answer("Бонус успешно применен")
    # await callback_query.message.edit_media(
    #     media=InputMediaPhoto(
    #         media=cached_photo_path25,  
    #         caption="Выберите в какой игре отменить поражение",
    #         parse_mode='HTML'
    #     ),
    #     reply_markup=remove_loss_keyboard
    # )

@player_router.callback_query(lambda c: c.data == "become_premium")
async def become_premium(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await buy_premium_or_check_end_date(user_id=user_id, type_change='update')
    request_role = await check_user_role(user_id)
    player_role = [role["role"] for role in request_role][0]
    print(player_role)

    if player_role == 'player':
        await buy_premium_or_check_end_date(user_id=user_id, type_change='buy')
        await shop_bonus_for_premium(user_id=user_id)
        await change_user_design(user_id=user_id)
        await callback_query.answer(
            text="Поздравляем с преобретением премиум подписки!!",
            show_alert=True
        )
    else:
        diffrequest = await time_difference_premium(user_id=user_id)
        str_diffrequest = str(diffrequest).split(':')
        print(diffrequest)
        await callback_query.answer(
            text=f"У вас уже есть подписка\n\n Подписка еще действует {int(str_diffrequest[0])} часов {int(str_diffrequest[1])} минут",
            show_alert=True
        )