from hendlers.ls.player  import player_router, cached_photo_path18, cached_photo_path6
from aiogram.types import CallbackQuery, InputMediaPhoto
from db_moves.add_db import  update_user_coins, make_buy
from db_moves.get_db import get_player_shop, get_user_coins, check_chop_el
from keyboards import shop_keyboard, start_keyboard
import time



@player_router.callback_query(lambda c: c.data=="start_shop")
async def bot_shop(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    player_el_shop = await get_player_shop(user_id)
    user_coins = await get_user_coins(user_id)
    result = [[record["user_id"], record["sale_name"], record["sale_cost"], record["sale_count"], record["user_count"]] for record in player_el_shop]
    result_name=[
        f"{result[0][1]}🎨",f"{result[1][1]}🎰",f"{result[2][1]}🎟️", f"{result[3][1]}💡",f"{result[4][1]}🧤(Суперпрятка 🔎)",f"{result[5][1]}⛔", f"{result[6][1]}⚽(Супернаходка 💰)", f"{result[7][1]}🛡️"
    ]
    use_caption = [
        f"<b>Доступно в:</b> Цуефа🪨✂️📃, Пенальти⚽, Сокровища💰🗝️\n",
        f"<b>Доступно в:</b> 21♠️♥️\n",
        f"<b>Доступно в:</b> Пенальти⚽, Сокровища💰🗝️\n",
    ]
    output_caption = f""
    for i in range(len(result_name)):
        use_area = ""
        if i in [3, 4]:
            use_area = use_caption[2]
        elif i in [6]:
            use_area = use_caption[0]
        elif i in [1, 7]:
            use_area = use_caption[1]
        local_caption = f"{result_name[i]}\n{use_area}<b>Стоимость: </b>{result[i][2]}💲\n<b>Количество: </b>{result[i][3]}    <b>У вас: </b>{result[i][4]}\n\n"
        output_caption+=local_caption
    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=cached_photo_path18,  
            caption=f"<b>Магазин</b>🛍️\n\n"
            f"Ваша валюта: {user_coins}💲\n\n"
            f"{output_caption}"
            f"Купить👇",
            parse_mode='HTML'
        ),
        reply_markup=shop_keyboard
    )

@player_router.callback_query(lambda c: c.data in ["remove_loss","help_cuefa","super_shoot","super_save","new_desigh","ticket_private_tour", "gamble_bonus", "insurance_bonus"])
async def bot_shop(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_buy = callback_query.data
    user_coins = await get_user_coins(user_id=user_id)
    user_buy_text = ''
    if user_buy == "remove_loss": user_buy_text = "Отмена поражения"
    elif user_buy == "help_cuefa": user_buy_text = "Подсказка"
    elif user_buy == "super_shoot": user_buy_text = "Суперудар"
    elif user_buy == "super_save": user_buy_text = "Суперсейв"
    elif user_buy == "new_desigh": user_buy_text = "Эксклюзивный дизайн"
    elif user_buy == "ticket_private_tour": user_buy_text = "Билет на частный турнир"
    elif user_buy == "gamble_bonus": user_buy_text = "Азарт"
    elif user_buy == "insurance_bonus": user_buy_text = "Страховка"
    check_shop = await check_chop_el(user_id=user_id, sale_name=user_buy_text)
    shop_el_price = check_shop[0]
    if check_shop[1] > 0:
        if (user_coins - shop_el_price)>=0:
            await make_buy(user_id=user_id, sale_name=user_buy_text)
            await update_user_coins(coins = -shop_el_price,user_id=user_id)
            await callback_query.answer(text=f"{user_buy_text} успешно куплено!!!", show_alert=True)
            await callback_query.message.delete()
            await callback_query.message.answer_photo(
                photo=cached_photo_path6,
                caption="\n\n<b>Меню 📌</b>\n\n", 
                parse_mode='HTML',
                reply_markup=start_keyboard
            )
        else:
            await callback_query.answer(text=f"У вас не хватает средств", show_alert=True)
    else:
        await callback_query.answer(text=f"В магазине не осталось этого предмета", show_alert=True)