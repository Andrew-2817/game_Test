from hendlers.ls.player  import player_router, cached_photo_path10, cached_photo_path5, cached_photo_path3
from aiogram.types import CallbackQuery, InputMediaPhoto, UserProfilePhotos
from db_moves.get_db import  display_penalty_cuefa_leaderboard, display_main_leaderboard
from keyboards import  leadboards_season_back_keyboards, leadboards_keyboard, leadboards_season_3_back_keyboards
from db import get_db_connection
import time


#ЗДЕСЬ ФОТО НЕ НУЖНО
@player_router.callback_query(lambda c: c.data=="leadboards_season")
async def start_reg_on_tour(callback_query: CallbackQuery):

    await callback_query.message.delete()
    # Отправляем ответ
    new_message = await callback_query.message.answer(
        text="🏆 Здесь ты можешь посмотреть лучших игроков по каждой категории ",
        parse_mode="HTML",
        reply_markup=leadboards_season_back_keyboards
    )


@player_router.callback_query(lambda c: c.data=="start_leadboards")
async def start_reg_on_tour(callback_query: CallbackQuery):

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path10,
            caption="Каждый месяц таблица лидеров обновляется\n\n"
            "1 место в Сезонной ТЛ: 500₽\n"
            "1 место в Турнирной ТЛ: 1000₽\n\n"
            "Для продвижения бота:89261233000, будем очень благодарны вашей поддержке!"
        ), 
        reply_markup=leadboards_keyboard
    )
# СЕЗОННАЯ ТАБЛИЦА ЛИДЕРОВ, РАЗБИВАЕТСЯ НА 1)ЦУЕФА 2)ПЕНАЛЬТИ 3)ОБЩАЯ
@player_router.callback_query(lambda c: c.data=="leadboards_season_penalty")
async def start_reg_on_tour(callback_query: CallbackQuery):
    username = callback_query.from_user.username

    leadeк_resp = await display_penalty_cuefa_leaderboard(game_id=2)
    leaderboard =  [[leader["username"], leader["match_points"]] for leader in leadeк_resp]
    current_player = [leader for leader in leaderboard if leader[0] == username]
    current_player_place = leaderboard.index(*current_player)+1

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path5,
            caption="<b>Список лидеров : Пенальти⚽</b>\n\n"
            f"🥇 @{leaderboard[0][0]} - {leaderboard[0][1]}\n"
            f"🥈 @{leaderboard[1][0]} - {leaderboard[1][1]}\n"
            f"🥉 @{leaderboard[2][0]} - {leaderboard[2][1]}\n"
            f" 4. @{leaderboard[3][0]} - {leaderboard[3][1]}\n"
            f" 5. @{leaderboard[4][0]} - {leaderboard[4][1]}\n"
            f" 6. @{leaderboard[5][0]} - {leaderboard[5][1]}\n"
            f" 7. @{leaderboard[6][0]} - {leaderboard[6][1]}\n"
            f" 8. @{leaderboard[7][0]} - {leaderboard[7][1]}\n"
            f" 9. @{leaderboard[8][0]} - {leaderboard[8][1]}\n"
            f" 10. @{leaderboard[9][0]} - {leaderboard[9][1]}\n\n"
            f" {current_player_place}. @{current_player[0][0]} - {current_player[0][1]}",
            parse_mode="HTML"
        ), 
        reply_markup=leadboards_season_3_back_keyboards
    )

@player_router.callback_query(lambda c: c.data=="leadboards_season_cuefa")
async def start_reg_on_tour(callback_query: CallbackQuery):
    username = callback_query.from_user.username

    leadeк_resp = await display_penalty_cuefa_leaderboard(game_id=1)
    leaderboard =  [[leader["username"], leader["match_points"]] for leader in leadeк_resp]
    current_player = [leader for leader in leaderboard if leader[0] == username]
    current_player_place = leaderboard.index(*current_player)+1

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path3,
            caption="<b>Список лидеров : Цуефа 🪨✂️📃</b>\n\n"
            f"🥇 @{leaderboard[0][0]} - {leaderboard[0][1]}\n"
            f"🥈 @{leaderboard[1][0]} - {leaderboard[1][1]}\n"
            f"🥉 @{leaderboard[2][0]} - {leaderboard[2][1]}\n"
            f" 4. @{leaderboard[3][0]} - {leaderboard[3][1]}\n"
            f" 5. @{leaderboard[4][0]} - {leaderboard[4][1]}\n"
            f" 6. @{leaderboard[5][0]} - {leaderboard[5][1]}\n"
            f" 7. @{leaderboard[6][0]} - {leaderboard[6][1]}\n"
            f" 8. @{leaderboard[7][0]} - {leaderboard[7][1]}\n"
            f" 9. @{leaderboard[8][0]} - {leaderboard[8][1]}\n"
            f" 10. @{leaderboard[9][0]} - {leaderboard[9][1]}\n\n"
            f" {current_player_place}. @{current_player[0][0]} - {current_player[0][1]}",
            parse_mode="HTML"
        ), 
        reply_markup=leadboards_season_3_back_keyboards
    )

@player_router.callback_query(lambda c: c.data=="leadboards_season_stakanchiki")
async def start_reg_on_tour(callback_query: CallbackQuery):
    username = callback_query.from_user.username

    leadeк_resp = await display_penalty_cuefa_leaderboard(game_id=4)
    leaderboard =  [[leader["username"], leader["match_points"]] for leader in leadeк_resp]
    current_player = [leader for leader in leaderboard if leader[0] == username]
    current_player_place = leaderboard.index(*current_player)+1

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path3,
            caption="<b>Список лидеров : Сокровища</b>\n\n"
            f"🥇 @{leaderboard[0][0]} - {leaderboard[0][1]}\n"
            f"🥈 @{leaderboard[1][0]} - {leaderboard[1][1]}\n"
            f"🥉 @{leaderboard[2][0]} - {leaderboard[2][1]}\n"
            f" 4. @{leaderboard[3][0]} - {leaderboard[3][1]}\n"
            f" 5. @{leaderboard[4][0]} - {leaderboard[4][1]}\n"
            f" 6. @{leaderboard[5][0]} - {leaderboard[5][1]}\n"
            f" 7. @{leaderboard[6][0]} - {leaderboard[6][1]}\n"
            f" 8. @{leaderboard[7][0]} - {leaderboard[7][1]}\n"
            f" 9. @{leaderboard[8][0]} - {leaderboard[8][1]}\n"
            f" 10. @{leaderboard[9][0]} - {leaderboard[9][1]}\n\n"
            f" {current_player_place}. @{current_player[0][0]} - {current_player[0][1]}",
            parse_mode="HTML"
        ), 
        reply_markup=leadboards_season_3_back_keyboards
    )

@player_router.callback_query(lambda c: c.data=="leadboards_season_21")
async def start_reg_on_tour(callback_query: CallbackQuery):
    username = callback_query.from_user.username

    leadeк_resp = await display_penalty_cuefa_leaderboard(game_id=3)
    leaderboard =  [[leader["username"], leader["match_points"]] for leader in leadeк_resp]
    current_player = [leader for leader in leaderboard if leader[0] == username]
    current_player_place = leaderboard.index(*current_player)+1

    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path3,
            caption="<b>Список лидеров : 21♠♥</b>\n\n"
            f"🥇 @{leaderboard[0][0]} - {leaderboard[0][1]}\n"
            f"🥈 @{leaderboard[1][0]} - {leaderboard[1][1]}\n"
            f"🥉 @{leaderboard[2][0]} - {leaderboard[2][1]}\n"
            f" 4. @{leaderboard[3][0]} - {leaderboard[3][1]}\n"
            f" 5. @{leaderboard[4][0]} - {leaderboard[4][1]}\n"
            f" 6. @{leaderboard[5][0]} - {leaderboard[5][1]}\n"
            f" 7. @{leaderboard[6][0]} - {leaderboard[6][1]}\n"
            f" 8. @{leaderboard[7][0]} - {leaderboard[7][1]}\n"
            f" 9. @{leaderboard[8][0]} - {leaderboard[8][1]}\n"
            f" 10. @{leaderboard[9][0]} - {leaderboard[9][1]}\n\n"
            f" {current_player_place}. @{current_player[0][0]} - {current_player[0][1]}",
            parse_mode="HTML"
        ), 
        reply_markup=leadboards_season_3_back_keyboards
    )

@player_router.callback_query(lambda c: c.data=="leaderboards_season_main")
async def start_reg_on_tour(callback_query: CallbackQuery):
    username = callback_query.from_user.username

    stat_leader = await display_main_leaderboard()
    print([[leader["username"], leader["total_score"]] for leader in stat_leader])
    leaderboard = [[leader["username"], leader["total_score"]] for leader in stat_leader]
    current_player = [leader for leader in leaderboard if leader[0] == username]
    current_player_place = leaderboard.index(*current_player)+1
    print(current_player, current_player_place)
    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path10,
            caption="<b>Общая таблица лидеров</b>\n\n"
            f"🥇 @{leaderboard[0][0]} - {leaderboard[0][1]}\n"
            f"🥈 @{leaderboard[1][0]} - {leaderboard[1][1]}\n"
            f"🥉 @{leaderboard[2][0]} - {leaderboard[2][1]}\n"
            f" 4. @{leaderboard[3][0]} - {leaderboard[3][1]}\n"
            f" 5. @{leaderboard[4][0]} - {leaderboard[4][1]}\n"
            f" 6. @{leaderboard[5][0]} - {leaderboard[5][1]}\n"
            f" 7. @{leaderboard[6][0]} - {leaderboard[6][1]}\n"
            f" 8. @{leaderboard[7][0]} - {leaderboard[7][1]}\n"
            f" 9. @{leaderboard[8][0]} - {leaderboard[8][1]}\n"
            f" 10. @{leaderboard[9][0]} - {leaderboard[9][1]}\n\n"
            f" {current_player_place}. @{current_player[0][0]} - {current_player[0][1]}",
            parse_mode="HTML"
        ), 
        reply_markup=leadboards_season_3_back_keyboards
    )