from db import get_db_connection


async def get_player_win_streak(user_id: int, game_id: int):
    conn = await get_db_connection()
    try:
        player_ws = await conn.fetch("""
            SELECT win_streak
            FROM statistics
            WHERE user_id = $1 AND game_id = $2;
        """, user_id, game_id)
    finally:
        await conn.close()

    return player_ws[0]["win_streak"] if player_ws else 0

async def get_player_best_win_streak(user_id: int, game_id: int):
    conn = await get_db_connection()
    try:
        player_ws = await conn.fetch("""
            SELECT best_win_streak
            FROM statistics
            WHERE user_id = $1 AND game_id = $2;
        """, user_id, game_id)
    finally:
        await conn.close()

    return player_ws[0]["best_win_streak"] if player_ws else 0

async def get_player_match_points(user_id:int, game_id: int):
    conn = await get_db_connection()
    try:
        player_mp = await conn.fetch("""
            SELECT match_points
            FROM statistics
            WHERE user_id = $1 AND game_id = $2;
        """, user_id, game_id)
        print(player_mp, user_id, game_id)
    finally:
        await conn.close()
    return player_mp[0]["match_points"]

async def display_total_days(user_id: int):
    conn = await get_db_connection()
    try:
        days = await conn.fetch("""
            SELECT total_days_in_game
            FROM users
            WHERE user_id = $1;
        """, user_id)
        return days
    except Exception as e:
        print(f"Ошибка при получении данных по дням: {e}")
        return []
    finally:
        await conn.close()


async def display_main_statistics(user_id: int):
    conn = await get_db_connection()
    try:
        statistics = await conn.fetch("""
            SELECT wins, draws, losses, win_streak, best_win_streak, choice_1, choice_2, choice_3
            FROM statistics
            WHERE user_id = $1
            ORDER BY game_id
        """, user_id)
    finally:
        await conn.close()

    return statistics

async def display_main_leaderboard():
    conn = await get_db_connection()
    try:
        # statistics = await conn.fetch("""      
        #     SELECT user_id, SUM(match_points) AS total_score
        #     FROM statistics
        #     GROUP BY user_id
        #     ORDER BY total_score DESC;
        # """)
        statistics = await conn.fetch("""                
            SELECT  u.username, SUM(s.match_points) AS total_score
            FROM users u
            JOIN statistics s ON u.user_id = s.user_id
            GROUP BY u.username
            ORDER BY total_score DESC;
        """)
    finally:
        await conn.close()

    return statistics

async def display_penalty_cuefa_leaderboard(game_id):
    conn = await get_db_connection()
    try:
        statistics = await conn.fetch("""                
            
            SELECT  
                u.username, 
                s.match_points  
            FROM 
                users u 
            JOIN 
                statistics s ON u.user_id = s.user_id 
            WHERE 
                s.game_id = $1
            GROUP BY 
                u.username, s.match_points 
            ORDER BY  
                s.match_points DESC;


        """, game_id)
    finally:
        await conn.close()

    return statistics

async def get_player_shop(user_id:int):
    conn = await get_db_connection()
    try:
        player_shop = await conn.fetch("""
            SELECT * FROM shop
            where user_id = $1
        """, user_id)
    finally:
        await conn.close()
    
    return player_shop

async def get_user_coins(user_id:int):
    conn = await get_db_connection()
    try:
        player_shop = await conn.fetch("""
            SELECT coins
            FROM users
            where user_id = $1
        """, user_id)
    finally:
        await conn.close()
    
    return int(player_shop[0]["coins"])

async def check_chop_el(user_id, sale_name):
    conn = await get_db_connection()
    try:
        player_shop = await conn.fetch("""
            SELECT sale_cost, sale_count
            FROM shop
            where user_id = $1 and sale_name = $2
        """, user_id, sale_name)
    finally:
        await conn.close()
    
    return [player_shop[0]["sale_cost"], player_shop[0]["sale_count"]]

async def check_user_el_in_game(user_id:int):
    conn = await get_db_connection()
    try:
        player = await conn.fetch("""
            SELECT sale_name
            FROM shop
            where user_id = $1 and (sale_name = 'Подсказка' or sale_name = 'Суперудар' or sale_name = 'Суперсейв') and user_count >0
        """, user_id)
    finally:
        await conn.close()
    
    return [player[i]["sale_name"] for i in range(len(player))]