from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

#ПАК ИЗ КНОПОК ДЛЯ КОМАНДЫ "СТАРТ" (как команда)
#кнопка информации 
info_button = InlineKeyboardButton(text="О боте 🔎", callback_data="info")
#кнопка страт
start_button = InlineKeyboardButton(text="Старт 🚀", callback_data="start")
#кнопка с ссылкой на какую-нибудь  группу 
link_button = InlineKeyboardButton(text="Перейти в сообщество 🔗", url="https://t.me/+MRNHKNqkKZk5YWUy")

main_keyboard = InlineKeyboardMarkup(inline_keyboard=[[info_button, start_button], [link_button]])


#ПАК ИЗ КНОПОК ДЛЯ ИНФО О БОТЕ
# Кнопка "Назад"
info_back_button = InlineKeyboardButton(text="Назад 🔙", callback_data="info_back")
# Кнопка "Футбол"
info_football = InlineKeyboardButton(text="Футбол ⚽", callback_data="info_footbal")
# Кнопка "Цуефа"
info_RPS = InlineKeyboardButton(text="Цуефа 🪨✂️📃", callback_data="info_RPS" )
# Кнопка "Турниры"
info_tour = InlineKeyboardButton(text="Турниры🏆", callback_data="info_tournaments" )
# Кнопка "Матчи"
info_match = InlineKeyboardButton(text="Матчи 🚥", callback_data="info_match")

info_keyboard = InlineKeyboardMarkup(inline_keyboard=[[info_RPS, info_football,],[info_tour, info_match], [info_back_button]])


#ПАК ИЗ КНОПОК ДЛЯ "СТАРТ"(как кнопка)
# Кнопка "Назад"
start_back_button = InlineKeyboardButton(text="Назад 🔙", callback_data="info_back") #аккуратно не запутаться (назад тут = назад в паке "о боте" )
# Кнопка ""
start_leadboards = InlineKeyboardButton(text="Таблица лидеров 📊", callback_data="start_leadboards")
# Кнопка "Цуефа"
start_profile = InlineKeyboardButton(text="Профиль 👤", callback_data="start_profile" )
# Кнопка "Турниры"
start_tour = InlineKeyboardButton(text="Турниры 🏆", callback_data="start_tournaments" )
# Кнопка "Матчи"
start_match = InlineKeyboardButton(text="Играть 🎮", callback_data="start_match")
# Кнопка "Магазин"
start_shop = InlineKeyboardButton(text="Магазин 🛍️", callback_data="start_shop")
become_premium = InlineKeyboardButton(text = 'Преобрести премиум ✨', callback_data='become_premium')

premium_design = InlineKeyboardButton(text='Эксклюзивный дизайн', callback_data='premium_design')
standart_design = InlineKeyboardButton(text='Стандартный дизайн', callback_data='premium_design')

start_keyboard = InlineKeyboardMarkup(inline_keyboard=[[start_match ,start_profile],[start_leadboards], [start_tour, start_shop], [become_premium],[start_back_button]])
start_keyboard_premium = InlineKeyboardMarkup(inline_keyboard=[[start_match ,start_profile],[start_leadboards], [start_tour, start_shop], [become_premium],[premium_design],[start_back_button]])
start_keyboard_standart = InlineKeyboardMarkup(inline_keyboard=[[start_match ,start_profile],[start_leadboards], [start_tour, start_shop], [become_premium],[standart_design],[start_back_button]])


#ПАК ИЗ КНОПОК ДЛЯ "ПРОФИЛЬ"(кнопка)
#кнопка "Назад"
profile_back = InlineKeyboardButton(text="Назад 🔙", callback_data="profile_back") #будет привязан ко всем кнопкам на меню
#кнопка "Полная статистика"
profile_statistic = InlineKeyboardButton(text="Полная статистика", callback_data="extended_static")

#кнопка "История матчей"
history_of_matches = InlineKeyboardButton(text="История матчей 📒", callback_data="history_of_matches") 

profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[[profile_statistic],[history_of_matches],[profile_back]])


# ПАК ИЗ КНОПОК РАСШИРЕННАЯ СТАТИСТИКА
#кнопка "Назад"
extended_static = InlineKeyboardButton(text="Назад 🔙", callback_data="start_profile")
extended_static_remove_loss = InlineKeyboardButton(text="Отменить поражение ⛔", callback_data="remove_loss")
extended_static_keyboard = InlineKeyboardMarkup(inline_keyboard=[[extended_static_remove_loss],[extended_static]])

# ПАК КНОПОК ОТМЕНИТЬ ПОРАЖЕНИЕ И ВЫБРАТЬ ИГРУ ГДЕ ОТМЕНА

remove_loss_back = InlineKeyboardButton(text="Назад 🔙", callback_data="extended_static") 
#кнопка "Пенальти"
remove_loss_penality  = InlineKeyboardButton(text="Пенальти ⚽", callback_data="remove_loss_penality")
#кнопка "Цуефа"
remove_loss_RPS = InlineKeyboardButton(text="Цуефа 🪨✂️📃", callback_data="remove_loss_RPS")
remove_loss_21 = InlineKeyboardButton(text="21 ♠️♥️", callback_data="remove_loss_21")
remove_loss_treasures = InlineKeyboardButton(text="Сокровища 💰🗝️", callback_data="remove_loss_treasures")
remove_loss_keyboard = InlineKeyboardMarkup(inline_keyboard=[[remove_loss_RPS, remove_loss_penality], [remove_loss_treasures, remove_loss_21], [remove_loss_back]])


#ПАК ИЗ КНОПОК ДЛЯ "ИГРАТЬ"(кнопка)
#кнопка "Назад"
play_back = InlineKeyboardButton(text="Назад 🔙", callback_data="profile_back") 
#кнопка "Пенальти"
play_penality  = InlineKeyboardButton(text="Пенальти ⚽", callback_data="profile_penality")
#кнопка "Цуефа"
play_RPS = InlineKeyboardButton(text="Цуефа 🪨✂️📃", callback_data="profile_RPS")
play_21 = InlineKeyboardButton(text="21 ♠️♥️", callback_data="profile_21")
play_treasures = InlineKeyboardButton(text="Сокровища 💰🗝️", callback_data="profile_treasures")

play_keyboard = InlineKeyboardMarkup(inline_keyboard=[[play_RPS, play_penality], [play_treasures, play_21], [play_back]])

# Кнопка для выхода из игры - Личка

game_ls_back = InlineKeyboardButton(text="Назад 🔙", callback_data="start_match_back")
game_ls_back_keyboard = InlineKeyboardMarkup(inline_keyboard=[[game_ls_back]])

# ПАК ИЗ КНОПОК ДЛЯ "МАГАЗИН"
remove_loss = InlineKeyboardButton(text="Отмена поражения ⛔", callback_data="remove_loss")
help_cuefa = InlineKeyboardButton(text="Подсказка 💡", callback_data="help_cuefa")
super_shoot = InlineKeyboardButton(text="Суперудар ⚽(Супернаходка 💰)", callback_data="super_shoot")
super_save  = InlineKeyboardButton(text="Суперсейв 🧤(Суперпрятка 🔎)", callback_data="super_save")
new_desigh = InlineKeyboardButton(text="Эксклюзивный дизайн 🎨", callback_data="new_desigh")
ticket_private_tour = InlineKeyboardButton(text="Билет на частный турнир 🎟️", callback_data="ticket_private_tour")
gamble_bonus = InlineKeyboardButton(text="Азарт 🎰", callback_data="gamble_bonus")
insurance_bonus = InlineKeyboardButton(text="Страховка 🛡️", callback_data="insurance_bonus")
shop_back = InlineKeyboardButton(text="Назад 🔙", callback_data="start")
shop_keyboard = InlineKeyboardMarkup(inline_keyboard=[[new_desigh],[gamble_bonus],[ticket_private_tour], [help_cuefa],[super_save], [remove_loss],[super_shoot],[insurance_bonus], [shop_back]])

test_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Начать', callback_data='test_state')]])
buy_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Начать', callback_data='buy_state')]])
# ПАК ИЗ КНОПОК ДЛЯ "ИСТОРИЯ МАТЧЕЙ"
# кнопка "История матчей -> Назад"
history_of_matches_back = InlineKeyboardButton(text="Назад 🔙", callback_data="start")
history_of_matches_penalty = InlineKeyboardButton(text="Пенальти ⚽", callback_data="history_penalty")
history_of_matches_cuefa = InlineKeyboardButton(text="Цуефа 🪨✂️📃", callback_data="history_cuefa")
history_of_matches_21 = InlineKeyboardButton(text="21 ♠️♥️", callback_data="history_21")
history_of_matches_stakanchiki = InlineKeyboardButton(text="Сокровища 💰🗝️", callback_data="history_stakanchiki")
history_of_matches_keyboard = InlineKeyboardMarkup(inline_keyboard=[[history_of_matches_cuefa, history_of_matches_penalty] ,[history_of_matches_stakanchiki, history_of_matches_21], [history_of_matches_back]])

# ПАК ИЗ КНОПОКА ДЛЯ "ИСТОРИЯ МАТЧЕЙ" -> ИГРА
history_of_matches_back = InlineKeyboardButton(text="Назад 🔙", callback_data="history_of_matches")
history_of_matches_back_keyboard = InlineKeyboardMarkup(inline_keyboard=[[history_of_matches_back]])

#ПАК ИЗ КНОПОК ДЛЯ "ТУРНИРЫ"(кнопка)
#кнопка "Назад"
tour_back = InlineKeyboardButton(text="Назад 🔙", callback_data="profile_back") 
#кнопка "Регистрация(на турнир)"
tour_reg = InlineKeyboardButton(text="Регистрация 🔥", callback_data="tour_reg")

tour_keyboard = InlineKeyboardMarkup(inline_keyboard=[[tour_reg], [tour_back]])

#ПАК ИЗ КНОПОК ДЛЯ "ТАБЛИЦА ЛИДЕРОВ"(кнопка)
#кнопка "Назад"
leadboards_back = InlineKeyboardButton(text="Назад 🔙", callback_data="profile_back") 
#кнопка "сезоная таблица лидеров"
leadboards_season = InlineKeyboardButton(text="Сезонная таблица лидеров", callback_data="leadboards_season") 
#кнопка "турнрая таблица лидеров"
leadboards_tour = InlineKeyboardButton(text="Турнирная таблица лидеров", callback_data="leadboards_tournaments")
# кнопка "полная таблица лидеров"

leadboards_keyboard = InlineKeyboardMarkup(inline_keyboard=[[leadboards_tour], [leadboards_season], [leadboards_back]])

# ПАК ИЗ КНОПОК ДЛЯ СЕЗОННОЙ ТАБЛИЦЕ ЛИДЕРОВ
# таблица лидеров для игры Цуефа
leadboards_season_penalty = InlineKeyboardButton(text="Таблица лидеров по игре Пенальти", callback_data="leadboards_season_penalty")
# таблица лидеров для игры Пенальти
leadboards_season_cuefa = InlineKeyboardButton(text="Таблица лидеров по игре Цуефа", callback_data="leadboards_season_cuefa")
# таблица лидеров для игры Напёрстки
leadboards_season_21 = InlineKeyboardButton(text="Таблица лидеров по игре 21", callback_data="leadboards_season_21")
# таблица лидеров для игры 21
leadboards_season_stakanchiki = InlineKeyboardButton(text="Таблица лидеров по игре Сокровища", callback_data="leadboards_season_stakanchiki")
# общая таблица лидеров
leaderboards_season_main =  InlineKeyboardButton(text="Общая таблица лидеров", callback_data="leaderboards_season_main")
# кнопка назад
leadboards_season_back = InlineKeyboardButton(text="Назад 🔙", callback_data="start_leadboards")

leadboards_season_back_keyboards = InlineKeyboardMarkup(inline_keyboard=[[leadboards_season_penalty], [leadboards_season_cuefa], [leadboards_season_21], [leadboards_season_stakanchiki], [leaderboards_season_main], [leadboards_season_back]])

#ПАК ИЗ КНОПОК ДЛЯ СЕЗОННОЙ ТАБЛИЦЕ ЛИДЕРОВ -> НАЗАД
# кнопка назад
leadboards_season_3_back = InlineKeyboardButton(text="Назад 🔙", callback_data="start_leadboards")

leadboards_season_3_back_keyboards = InlineKeyboardMarkup(inline_keyboard=[[leadboards_season_3_back]])

#ПАК ИЗ КНОПОК ЧТОБЫ ВЫБРАТЬ ИГРУ "ГРУППА"
#кнопка "Пенальти"
group_game_penality  = InlineKeyboardButton(text="Пенальти ⚽", callback_data="group_game_penality")
#кнопка "Цуефа"
group_game_RPS = InlineKeyboardButton(text="Цуефа 🪨✂️📃", callback_data="group_game_RPS")

group_game_keyboard = InlineKeyboardMarkup(inline_keyboard=[[group_game_RPS], [group_game_penality]])

#ПАК КНОПОК ДЛЯ НАЧАЛА ИГР
# Кнопка "Принять вызов в цуефа"
CMN_accept_button = InlineKeyboardButton(text="🔥 Принять вызов 🔥", callback_data="CMN_accept")
CMN_accept_keyboard = InlineKeyboardMarkup(inline_keyboard=[[CMN_accept_button]])

# Кнопка "Принять вызов в пенки"
penalty_accept_button = InlineKeyboardButton(text="🟢 Принять вызов 🟢", callback_data="penalty_accept")
penalty_accept_keyboard = InlineKeyboardMarkup(inline_keyboard=[[penalty_accept_button]])




# Кнопка "Принять вызов в стаканчики"
stakanchiki_accept_button = InlineKeyboardButton(text="🔶 Принять вызов 🔶", callback_data="stakanchiki_accept")
stakanchiki_accept_keyboard = InlineKeyboardMarkup(inline_keyboard=[[stakanchiki_accept_button]])

# Кнопка "Принять вызов в 21"
ochko_accept_button = InlineKeyboardButton(text="♥️ Принять вызов ♥️", callback_data="ochko_accept")
ochko_accept_keyboard = InlineKeyboardMarkup(inline_keyboard=[[ochko_accept_button]])

#ПАК КНОПОК ДЛЯ ИГРИЩ
#кнопки для игры в пенальти 
# Кнопки для атакующего
attack_left = InlineKeyboardButton(text="⬅️", callback_data="attack_left")
attack_center = InlineKeyboardButton(text="⬆️", callback_data="attack_center")
attack_right = InlineKeyboardButton(text="➡️", callback_data="attack_right")
supershot_in_game_ls = InlineKeyboardButton(text="Суперудар ⚽", callback_data="supershot_in_game_ls")
attack_buttons_penki_ls = InlineKeyboardMarkup(inline_keyboard=[
    [attack_left, attack_center, attack_right], [supershot_in_game_ls]
])
# Кнопки для защитника
defense_left = InlineKeyboardButton(text="⬅️", callback_data="defense_left")
defense_center = InlineKeyboardButton(text="⬆️", callback_data="defense_center")
defense_right = InlineKeyboardButton(text="➡️", callback_data="defense_right")
supersave_in_game_ls = InlineKeyboardButton(text="Суперсейв 🧤", callback_data="supersave_in_game_ls")
help_in_game_ls = InlineKeyboardButton(text="Подсказка 💡", callback_data="help_in_game_ls")
defense_buttons_penki_ls = InlineKeyboardMarkup(inline_keyboard=[
    [defense_left, defense_center, defense_right], [supersave_in_game_ls], [help_in_game_ls]
])


#кнопки для игры в сокорвища 
# Кнопки для атакующего
attack_left_treasures = InlineKeyboardButton(text="💰", callback_data="treasuresA_left")
attack_center_treasures = InlineKeyboardButton(text="💰", callback_data="treasuresA_center")
attack_right_treasures = InlineKeyboardButton(text="💰", callback_data="treasuresA_right")
supersave_in_treasure_ls = InlineKeyboardButton(text="Суперпрятка 🔎", callback_data="supersave_in_treasure_ls")
attack_buttons_treasures_ls = InlineKeyboardMarkup(inline_keyboard=[
    [attack_left_treasures, attack_center_treasures, attack_right_treasures], [supersave_in_treasure_ls]
])
# Кнопки для защитника
defense_left_treasures = InlineKeyboardButton(text="🗝️", callback_data="treasuresD_left")
defense_center_treasures = InlineKeyboardButton(text="🗝️", callback_data="treasuresD_center")
defense_right_treasures = InlineKeyboardButton(text="🗝️", callback_data="treasuresD_right")
supershot_in_treasure_ls = InlineKeyboardButton(text="Супернаходка 💰", callback_data="supershot_in_treasure_ls")
help_in_treasure_ls = InlineKeyboardButton(text="Подсказка 💡", callback_data="help_in_treasure_ls")
defense_buttons_treasures_ls = InlineKeyboardMarkup(inline_keyboard=[
    [defense_left_treasures, defense_center_treasures, defense_right_treasures], [supershot_in_treasure_ls], [help_in_treasure_ls]
])


#кнопки для игры в Цуефа 
# Кнопки для атакующего
attack_left_KMN = InlineKeyboardButton(text="🪨", callback_data="KMNA_kamen")
attack_center_KMN = InlineKeyboardButton(text="📃", callback_data="KMNA_bumaga")
attack_right_KMN = InlineKeyboardButton(text="✂️", callback_data="KMNA_nognichi")
supershot_in_kmn_ls = InlineKeyboardButton(text="Суперудар ⚽", callback_data="supershot_in_kmn_ls")
attack_buttons_KMN_ls = InlineKeyboardMarkup(inline_keyboard=[
    [attack_left_KMN, attack_center_KMN, attack_right_KMN], [supershot_in_kmn_ls]
])
# Кнопки для защитника
defense_left_KMN = InlineKeyboardButton(text="🪨", callback_data="KMND_kamen")
defense_center_KMN = InlineKeyboardButton(text="📃", callback_data="KMND_bumaga")
defense_right_KMN = InlineKeyboardButton(text="✂️", callback_data="KMND_nognichi")
supershot_in_kmn_ls = InlineKeyboardButton(text="Суперудар ⚽", callback_data="supershot_in_kmn_ls")
defense_buttons_KMN_ls = InlineKeyboardMarkup(inline_keyboard=[
    [defense_left_KMN, defense_center_KMN, defense_right_KMN], [supershot_in_kmn_ls]
]) 


#Кнопки для игры КМН
KMN_kamen = InlineKeyboardButton(text="🪨", callback_data="kamen")
KMN_bumaga = InlineKeyboardButton(text="📃", callback_data="bumaga")
KMN_nognichi = InlineKeyboardButton(text="✂️", callback_data="nognichi")
supershot_in_kmn = InlineKeyboardButton(text="Суперудар ⚽", callback_data="supershot_in_kmn")
group_simbols_for_KMN = InlineKeyboardMarkup(inline_keyboard=[[KMN_kamen, KMN_bumaga,KMN_nognichi], [supershot_in_kmn]])

# Кнопки для игры Пенальти
penalty_left = InlineKeyboardButton(text="⬅️", callback_data="att_left")
penalty_center = InlineKeyboardButton(text="⬆️", callback_data="att_center")
penalty_right = InlineKeyboardButton(text="➡️", callback_data="att_right")
supershot_in_game = InlineKeyboardButton(text="Суперудар ⚽", callback_data="supershot_in_game")
group_simbols_for_penalty_att = InlineKeyboardMarkup(inline_keyboard=[[penalty_left, penalty_center, penalty_right], [supershot_in_game]])

penalty_left = InlineKeyboardButton(text="⬅️", callback_data="def_left")
penalty_center = InlineKeyboardButton(text="⬆️", callback_data="def_center")
penalty_right = InlineKeyboardButton(text="➡️", callback_data="def_right")
supersave_in_game = InlineKeyboardButton(text="Суперсейв 🧤", callback_data="supersave_in_game")
help_in_game = InlineKeyboardButton(text="Подсказка 💡", callback_data="help_in_game")
group_simbols_for_penalty_def = InlineKeyboardMarkup(inline_keyboard=[[penalty_left, penalty_center, penalty_right], [supersave_in_game], [help_in_game]])

# Кнопки для игры стаканчики
stakanchiki_left = InlineKeyboardButton(text="💰", callback_data="choose_left")
stakanchiki_center = InlineKeyboardButton(text="💰", callback_data="choose_center")
stakanchiki_right = InlineKeyboardButton(text="💰", callback_data="choose_right")
supersave_in_treasure = InlineKeyboardButton(text="Суперпрятка 🔎", callback_data="supersave_in_treasure")
group_simbols_for_stakanchiki_att = InlineKeyboardMarkup(inline_keyboard=[[stakanchiki_left, stakanchiki_center, stakanchiki_right], [supersave_in_treasure]])

stakanchiki_left = InlineKeyboardButton(text="🗝️", callback_data="find_left")
stakanchiki_center = InlineKeyboardButton(text="🗝️", callback_data="find_center")
stakanchiki_right = InlineKeyboardButton(text="🗝️", callback_data="find_right")
supershot_in_treasure = InlineKeyboardButton(text="Супернаходка 💰", callback_data="supershot_in_treasure")
help_in_treasure = InlineKeyboardButton(text="Подсказка 💡", callback_data="help_in_treasure")
group_simbols_for_stakanchiki_def = InlineKeyboardMarkup(inline_keyboard=[[stakanchiki_left, stakanchiki_center, stakanchiki_right], [help_in_treasure], [supershot_in_treasure]])


# Кнопки для первого игрока
group_simbols_for_ocko_att = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Взять карту", callback_data="ochko_go_ferst")],
        [InlineKeyboardButton(text="⛔ Остановиться", callback_data="ochko_stop_ferst")],
        [InlineKeyboardButton(text="Взять меньшую половину колоды", callback_data="ochko_remove_big_values")],
        [InlineKeyboardButton(text="Взять большую половину колоды", callback_data="ochko_remove_small_values")],
    ]
)
 
# Кнопки для второго игрока
group_simbols_for_ocko_def = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Взять карту", callback_data="ochko_go_second")],
        [InlineKeyboardButton(text="⛔ Остановиться", callback_data="ochko_stop_second")],
        [InlineKeyboardButton(text="Взять меньшую половину колоды", callback_data="ochko_remove_big_values")],
        [InlineKeyboardButton(text="Взять большую половину колоды", callback_data="ochko_remove_small_values")],
    ]
)

ls_simbols_for_ocko_att = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Взять карту", callback_data="ochko_go_ferst_ls")],
        [InlineKeyboardButton(text="⛔ Остановиться", callback_data="ochko_stop_ferst_ls")],
        [InlineKeyboardButton(text="Взять меньшую половину колоды", callback_data="ochko_remove_big_values_ls")],
        [InlineKeyboardButton(text="Взять большую половину колоды", callback_data="ochko_remove_small_values_ls")],
    ]
)
 
# Кнопки для второго игрока
ls_simbols_for_ocko_def = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Взять карту", callback_data="ochko_go_second_ls")],
        [InlineKeyboardButton(text="⛔ Остановиться", callback_data="ochko_stop_second_ls")],
        [InlineKeyboardButton(text="Взять меньшую половину колоды", callback_data="ochko_remove_big_values_ls")],
        [InlineKeyboardButton(text="Взять большую половину колоды", callback_data="ochko_remove_small_values_ls")],
    ]
)

#В ФАЙЛ keyboards  
#ПАК ИЗ КНОПОК ДЛЯ ИНФО О БОТЕ->ЦУЕФА
info_cuefa_back = InlineKeyboardButton(text="Назад 🔙", callback_data="info") 
info_cuefa_keyboard = InlineKeyboardMarkup(inline_keyboard = [[info_cuefa_back]])



# become_premium_keyboard = InlineKeyboardMarkup(inline_keyboard=[[become_premium]])