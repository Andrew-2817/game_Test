from datetime import datetime, timedelta
from db import get_db_connection


async def add_user(user_id: int, username: str, join_date: datetime = None, total_days_in_game: int = 0):
    if join_date is None:
        join_date = datetime.now() - timedelta(days=1)
    conn = await get_db_connection()
    try:
        await conn.execute("""
            INSERT INTO users (user_id, username, join_date, total_days_in_game)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id) DO NOTHING;
        """, user_id, username, join_date, total_days_in_game)
    finally:
        await conn.close()


async def update_days_for_user(user_id: int):
    conn = await get_db_connection()
    try:
        await conn.execute("""
            UPDATE users
            SET total_days_in_game = DATE_PART('day', NOW() - join_date)
            WHERE user_id = $1;
        """, user_id) 
    finally:
        await conn.close()

async def add_matches(game_id: int, player1_id: int, player2_id: int, result: str, start_time: datetime, match_points: int = 10):
    conn = await get_db_connection()
    try:
        await conn.execute("""
            INSERT INTO matches (game_id, player1_id, player2_id, result, start_time, match_points)
            VALUES ($1, $2, $3, $4, $5, $6);
        """, game_id, player1_id, player2_id, result, start_time, match_points)
    finally:
        await conn.close()

#не юзаем но пусть будет 
async def add_statistics(user_id: int, game_id: int, wins: int, draws: int, losses: int, win_streak: int, tournament_wins: int, match_points: int, tournament_points: int):
    conn = await get_db_connection()
    try:
        await conn.execute("""
            INSERT INTO statistics (user_id, game_id, wins, draws, losses, win_streak, tournament_wins, match_points, tournament_points)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (user_id, game_id) DO NOTHING;
        """, user_id, game_id, wins, draws, losses, win_streak, tournament_wins, match_points, tournament_points)
    finally:
        await conn.close()


async def init_player_statistics(user_id: int):
    # conn = await get_db_connection()
    # try:
    #     player_statistics = await conn.fetch("""
    #         SELECT user_id, game_id
    #         FROM statistics
    #         WHERE user_id = $1;
    #     """, user_id)
    # finally:
    #     await conn.close()

    # if len(player_statistics) == 0:
    #     await add_statistics(user_id, 1, 0, 0, 0, 0, 0, 0, 0)
    #     await add_statistics(user_id, 2, 0, 0, 0, 0, 0, 0, 0)
    # elif len(player_statistics) == 1 and player_statistics[0]['game_id'] == 1:
    #     await add_statistics(user_id, 2, 0, 0, 0, 0, 0, 0, 0)
    # elif len(player_statistics) == 1 and player_statistics[0]['game_id'] == 2:
    #     await add_statistics(user_id, 1, 0, 0, 0, 0, 0, 0, 0)
    await add_statistics(user_id, 1, 0, 0, 0, 0, 0, 0, 0)
    await add_statistics(user_id, 2, 0, 0, 0, 0, 0, 0, 0)
    await add_statistics(user_id, 3, 0, 0, 0, 0, 0, 0, 0)
    await add_statistics(user_id, 4, 0, 0, 0, 0, 0, 0, 0)


async def update_user_statistics(
        user_id: int, 
        game_id: int, 
        win: int, 
        draw: int, 
        loss: int, 
        win_streak: int,
        best_win_streak: int,
        choice_1:int,
        choice_2:int,
        choice_3:int,
        match_points: int
        ):
    conn = await get_db_connection()
    try:
        await conn.execute("""
            UPDATE statistics
            SET wins = wins + $1,
                draws = draws + $2,
                losses = losses + $3,
                win_streak = $4,
                best_win_streak = $5,
                choice_1 = choice_1 +$6,
                choice_2 = choice_2 +$7,
                choice_3 = choice_3 +$8,
                match_points = match_points + $9
            WHERE user_id = $10 AND game_id = $11;
        """, win, draw, loss, win_streak, best_win_streak, choice_1, choice_2, choice_3, match_points, user_id, game_id)
    finally:
        await conn.close()

async def add_shop(user_id:int):
    conn = await get_db_connection()
    try:
        sales = [
        ('Отмена поражения', 2000, 8),
        ('Подсказка', 1500, 10),
        ('Суперудар', 1500, 10),
        ('Суперсейв', 1500, 10),
        ('Эксклюзивный дизайн', 3000, 1),
        ('Билет на частный турнир', 5000, 1),
        ]

        values = ', '.join(f"($1, '{sale[0]}', {sale[1]}, {sale[2]})" for sale in sales)

        await conn.execute(f"""
            INSERT INTO shop (user_id, sale_name, sale_cost, sale_count) 
            VALUES 
                {values} 
            ON CONFLICT (user_id, sale_name) DO NOTHING; 
        """, user_id)
    finally:
        await conn.close()

async def update_user_coins(coins:int, user_id:int):
    conn = await get_db_connection()
    try:
        await conn.fetch("""
            UPDATE users
            SET coins = coins + $1
            WHERE user_id = $2
        """, coins, user_id)
    finally:
        await conn.close()

async def make_buy(user_id:int, sale_name:str):
    conn = await get_db_connection()
    try:
        await conn.fetch("""
            UPDATE shop
            SET sale_count = sale_count - 1,
                user_count = user_count + 1
            WHERE user_id = $1 and sale_name = $2
        """, user_id, sale_name)
    finally:
        await conn.close()

async def use_el_in_game(user_id:int, sale_name: str):
    conn = await get_db_connection()
    try:
        await conn.fetch("""
            UPDATE shop
            SET user_count = user_count - 1
            WHERE user_id = $1 and sale_name = $2
        """, user_id, sale_name)
    finally:
        await conn.close()

async def buy_premium_or_check_end_date(user_id: int, type_change:str):
    conn = await get_db_connection()
    # Если только что купили подписку, то устанавливаем время окончания действия подписки
    if type_change == 'buy':
        date_now = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=20)
        try:
            await conn.fetch("""
                UPDATE users
                SET end_date_of_premium = $1,
                    role = $2
                WHERE user_id = $3
            """, date_now, 'premium', user_id)
        finally:
            await conn.close()
    
    # если нажали на кнопку купить подписку, но у нас уже роль премиум
    # тогда если подписка истекла то меняем роль на player
    # если еще не истекла то в алерте выводим сколько еще действует подписка
    elif type_change == 'update':
        date_now = datetime.now().replace(second=0, microsecond=0)
        try:
            await conn.fetch("""
                UPDATE users
                SET end_date_of_premium = NULL,
                    role = $1
                WHERE (user_id = $2) and (end_date_of_premium <= $3) and role = 'premium'
            """, 'player', user_id, date_now)
        finally:
            await conn.close()

async def shop_bonus_for_premium(user_id: int):
    conn = await get_db_connection()
    try:
        await conn.fetch("""
        UPDATE shop
        SET user_count = CASE 
            WHEN sale_name = 'Суперудар' THEN user_count + 5
            WHEN sale_name = 'Суперсейв' THEN user_count + 5
            WHEN sale_name = 'Подсказка' THEN user_count + 10
            WHEN sale_name = 'Отмена поражения' THEN user_count + 3
            WHEN sale_name = 'Билет на частный турнир' THEN user_count + 1
            ELSE user_count
        END
        WHERE user_id = $1 AND sale_name IN ('Суперудар', 'Суперсейв', 'Подсказка', 'Отмена поражения', 'Билет на частный турнир'); 
        """, user_id)
    finally:
        await conn.close()

async def change_user_design(user_id: int):
    conn = await get_db_connection()
    try:
        await conn.fetch("""
        UPDATE users
        SET premium_design = NOT premium_design
        WHERE user_id = $1
        """, user_id)
    finally:
        await conn.close()

