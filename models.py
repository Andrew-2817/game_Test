from db import get_db_connection
import time

async def add_games(conn):
    try:
        await conn.execute("""
            INSERT INTO games (game_id, game_name)
            VALUES 
                (1, 'КМН'), 
                (2, 'Пенальти'),
                (3, '21'),
                (4, 'Сокровища')
            ON CONFLICT (game_id) DO NOTHING; 
        """)
        print("Таблица игр успешно заполнена.")
    except Exception as e:
        print(f"Ошибка при заполнении таблицы игр: {e}")

# async def add_shop(conn):
#     try:
#         await conn.execute("""
#             INSERT INTO shop (sale_id, sale_name, sale_cost)
#             VALUES 
#                 (1, 'Отмена поражения', 2000), 
#                 (2, 'Подсказка Цуефа', 1500),
#                 (3, 'Подсказка Пенальти', 1500),
#                 (4, 'Эксклюзивный дизайн', 3000),
#                 (5, 'Билет на частный турнир', 5000)
#             ON CONFLICT (sale_id) DO NOTHING; 
#         """)
#         print("Таблица игр успешно заполнена.")
#     except Exception as e:
#         print(f"Ошибка при заполнении таблицы игр: {e}")

async def create_tables():
    start_time = time.time()
    conn = await get_db_connection()  # Получаем соединение с базой данных

    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_days_in_game INTEGER DEFAULT 0,
                coins INTEGER DEFAULT 0,
                end_date_of_premium TIMESTAMP,
                premium_design BOOLEAN DEFAULT FALSE,
                role TEXT DEFAULT 'player'
            );
        """)

        # Таблица игр
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS games (
                game_id SERIAL PRIMARY KEY,
                game_name TEXT NOT NULL
            );
        """)

        # Добавляем предустановленные игры
        await add_games(conn)

        # Таблица матчей
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                match_id SERIAL PRIMARY KEY,
                game_id INTEGER NOT NULL REFERENCES games(game_id),
                player1_id BIGINT NOT NULL REFERENCES users(user_id),
                player2_id BIGINT,  
                result TEXT DEFAULT '0',  
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
                match_points INTEGER DEFAULT 0  
            );
        """)

        # Таблица турниров
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tournaments (
                tournament_id SERIAL PRIMARY KEY,
                game_id INTEGER NOT NULL REFERENCES games(game_id),
                start_date TIMESTAMP NOT NULL,
                start_time TIME NOT NULL,
                end_date TIMESTAMP,
                status TEXT NOT NULL,  
                participant_count INTEGER DEFAULT 0
            );
        """)

        # Таблица участников турнира
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tournament_participants (
                participant_id SERIAL PRIMARY KEY,
                tournament_id INTEGER NOT NULL REFERENCES tournaments(tournament_id),
                user_id BIGINT NOT NULL REFERENCES users(user_id),
                stage TEXT NOT NULL,  
                result TEXT NOT NULL  
            );
        """)

        # Таблица статистики пользователей по играм
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                user_id BIGINT NOT NULL REFERENCES users(user_id),
                game_id INTEGER NOT NULL REFERENCES games(game_id),
                wins INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                win_streak INTEGER DEFAULT 0,
                best_win_streak INTEGER DEFAULT 0,
                choice_1 INTEGER DEFAULT 0,
                choice_2 INTEGER DEFAULT 0,
                choice_3 INTEGER DEFAULT 0,
                tournament_wins INTEGER DEFAULT 0,
                match_points INTEGER DEFAULT 0,  
                tournament_points INTEGER DEFAULT 0,  
                PRIMARY KEY (user_id, game_id)
            );
        """)

        # Таблица лидеров
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                user_id BIGINT NOT NULL REFERENCES users(user_id),
                game_id INTEGER NOT NULL REFERENCES games(game_id),
                global_rank INTEGER,
                tournament_rank INTEGER,
                PRIMARY KEY (user_id, game_id)
            );
        """)

        # Таблица победителей турниров
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tournament_winners (
                tournament_id INTEGER NOT NULL REFERENCES tournaments(tournament_id),
                user_id BIGINT NOT NULL REFERENCES users(user_id),
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tournament_points_awarded INTEGER DEFAULT 0,  
                PRIMARY KEY (tournament_id, user_id)
            );
        """)
        # Таблица для Магазина
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS shop (
                user_id BIGINT NOT NULL REFERENCES users(user_id),
                sale_name TEXT NOT NULL,
                sale_cost INTEGER NOT NULL,
                sale_count INTEGER DEFAULT 0,
                user_count INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, sale_name)
            );
        """)
        # await add_shop(conn)

    finally:
        await conn.close()  # Закрываем соединение с базой данных

    end_time = time.time()  # Конец отсчета времени создания таблиц
    print(f"create_tables выполнено за {end_time - start_time:.2f} секунд")
