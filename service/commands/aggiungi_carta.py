from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, CallbackContext

from entity.card import Versione, LinguaOccidentale, LinguaOrientale, Condizione, TipoVenditore, CardPokemon
from entity.brand import Brand, GenerazionePokemon, BrandPokemon
from entity.user import carica_utente

import asyncio

NOME_PERSONALIZZATO, BRAND, GENERAZIONE_POKEMON, IS_ASIATICA, CARD_ESPANSIONE, CARD_NAME, CARD_NUMBER, CARD_VERSION, CARD_LANGUAGE, CARD_CONDITION, CARD_SALE = range(11)

async def start_conversation(update: Update, context: CallbackContext)-> int:
    user = update.message.from_user
    context.user_data["user_id"] = user.id
    await update.message.reply_text(
        "Dimmi un po’ più su questa carta che vuoi aggiungere! 😊 \n1️⃣ Come vuoi chiamare la tua carta?"
        )
    return NOME_PERSONALIZZATO

async def nome_personalizzato(update: Update, context: CallbackContext)-> int:
    nome_personalizzato = update.message.text
    context.user_data["nome_personalizzato"] = nome_personalizzato

    keyboard = [[InlineKeyboardButton(brand.name, callback_data = brand.value)]for brand in Brand]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("2️⃣ A quale brand appartiene questa carta? 🔘",reply_markup=reply_markup)
    return BRAND

async def brand(update: Update, context: CallbackContext)-> int:
    query = update.callback_query
    await query.answer()

    brand = query.data
    context.user_data["brand"] = brand

    match brand:
        case Brand.POKEMON.value:
            return await generation(update, context)
        case Brand.ONEPIECE.value:
            await query.message.reply_text(f"😢 Purtroppo il brand {brand} non è al momento supportato")
            return ConversationHandler.END
        
async def generation(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    gen_list = list(GenerazionePokemon)

    keyboard = [
        [
            InlineKeyboardButton(gen_list[i].name, callback_data=gen_list[i].value),
            InlineKeyboardButton(gen_list[i + 1].name, callback_data=gen_list[i + 1].value),
            InlineKeyboardButton(gen_list[i + 2].name, callback_data=gen_list[i + 2].value)
        ] if i + 2 < len(gen_list) else
        [
            InlineKeyboardButton(gen_list[i].name, callback_data=gen_list[i].value),
            InlineKeyboardButton(gen_list[i + 1].name, callback_data=gen_list[i + 1].value)
        ] if i + 1 < len(gen_list) else
        [InlineKeyboardButton(gen_list[i].name, callback_data=gen_list[i].value)]
        for i in range(0, len(gen_list), 3)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text("3️⃣ Scegli la generazione del brand Pokémon ⚡", reply_markup=reply_markup)
    return GENERAZIONE_POKEMON

async def is_asiatica(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    gen = query.data
    context.user_data["generazione"] = gen

    keyboard = [
        [
            InlineKeyboardButton("Occidentale", callback_data="False"),
            InlineKeyboardButton("Orientale", callback_data="True")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        "4️⃣ Inserisci l’area geografica dell’espansione 🌍", reply_markup=reply_markup
    )
    return IS_ASIATICA

async def espansione(update: Update, context: CallbackContext)-> int:
    query = update.callback_query
    await query.answer()

    is_asia = query.data
    context.user_data["is_asia"] = is_asia

    brand_data = BrandPokemon().get_brand_json()
    brand_key = Brand.POKEMON.value
    gen = context.user_data["generazione"]
    loc = "Orientale" if is_asia == "True" else "occidentale"

    espansioni = brand_data[brand_key][gen][loc]

    if len(espansioni) > 0 or espansioni is None:
        keyboard = [
                [InlineKeyboardButton(brand["nome_espansione"], callback_data=f"{brand['nome_espansione']}|{brand['codice_espansione']}")]
                for brand in espansioni
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text("5️⃣ In quale espansione si trova la carta? 📦", reply_markup = reply_markup)
        return CARD_ESPANSIONE
    else:
        await query.message.reply_text(
            "⁉️ Attualmente non sono state registrate Espansioni per questa generazione\n"
            " - /AddE ➡️ Usa il seguente comando per aggiungere una nuova espansione\n"
            )
        return ConversationHandler.END

async def nome_card(update: Update, context: CallbackContext)-> int:
    query = update.callback_query
    await query.answer()

    nome_espansione, codice_espansione = query.data.split('|')

    context.user_data["nome_espansione"] = nome_espansione
    context.user_data["codice_espansione"] = codice_espansione

    await query.message.reply_text("6️⃣ Qual è il nome della carta? (es. Miraidon Ex) \n⚠️ le carte allenatore e strumento richiedono il loro nome in lingua inglese! ")
    return CARD_NAME


async def card_num(update: Update, context= CallbackContext)-> int:
    card_name = "-".join(update.message.text.split()).title()
    context.user_data["card_name"] = card_name

    await update.message.reply_text("7️⃣ Codice identificativo della carta: (il codice unico presente sulla carta) 🔑")
    return CARD_NUMBER

async def card_versione(update: Update, context: CallbackContext)-> int:
    num_card = update.message.text
    context.user_data["card_number"] = num_card

    version_list = list(Versione)
    keyboard = [
        [InlineKeyboardButton(version_list[i].name,callback_data=version_list[i].value),
         InlineKeyboardButton(version_list[i+1].name,callback_data=version_list[i+1].value),
         InlineKeyboardButton(version_list[i+2].name,callback_data=version_list[i+2].value)]
        if i + 2 < len(version_list) else 
        [InlineKeyboardButton(version_list[i].name, callback_data = version_list[i].value),
         InlineKeyboardButton(version_list[i+1].name, callback_data = version_list[i+1].value)]
         if i +1 < len(version_list) else
        [InlineKeyboardButton(version_list[i].name, callback_data = version_list[i].value)]
        for i in range(0, len(version_list),3)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("8️⃣ Indica la versione della carta 📄", reply_markup = reply_markup)
    return CARD_VERSION

async def card_language(update: Update, context: CallbackContext)-> int:
    query = update.callback_query
    await query.answer()

    version = query.data
    context.user_data["version"] = version

    is_orientale = True if context.user_data["is_asia"] == "True" else False

    asia_list = list(LinguaOrientale)
    occ_list = list(LinguaOccidentale)
    if is_orientale:
        keyboard = [
            [InlineKeyboardButton(asia_list[i].name, callback_data = asia_list[i].value),
             InlineKeyboardButton(asia_list[i +1].name, callback_data = asia_list[i+1].value)]
            if i +1 < len(asia_list) else
            [InlineKeyboardButton(asia_list[i].name, callback_data = asia_list[i].value)]
            for i in range(0, len(asia_list),2)
        ]
    else:
        keyboard = [
            [InlineKeyboardButton(occ_list[i].name, callback_data = occ_list[i].value),
             InlineKeyboardButton(occ_list[i +1].name, callback_data = occ_list[i+1].value)]
            if i +1 < len(occ_list) else
            [InlineKeyboardButton(occ_list[i].name, callback_data = occ_list[i].value)]
            for i in range(0, len(occ_list),2)
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("9️⃣ Lingua della carta 🌐", reply_markup = reply_markup)
    return CARD_LANGUAGE

async def card_condiction(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    lingua = query.data
    context.user_data["lingua"] = lingua

    condizioni_list = list(Condizione)
    keyboard = [
        [
            InlineKeyboardButton(condizioni_list[i].name, callback_data=condizioni_list[i].value),
            InlineKeyboardButton(condizioni_list[i + 1].name, callback_data=condizioni_list[i + 1].value),
            InlineKeyboardButton(condizioni_list[i + 2].name, callback_data=condizioni_list[i + 2].value)
        ] if i + 2 < len(condizioni_list) else
        [
            InlineKeyboardButton(condizioni_list[i].name, callback_data=condizioni_list[i].value),
            InlineKeyboardButton(condizioni_list[i + 1].name, callback_data=condizioni_list[i + 1].value)
        ] if i + 1 < len(condizioni_list) else
        [
            InlineKeyboardButton(condizioni_list[i].name, callback_data=condizioni_list[i].value)
        ]
        for i in range(0, len(condizioni_list), 3)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("1️⃣0️⃣ Seleziona la condizione della carta 🛠️", reply_markup = reply_markup)
    return CARD_CONDITION

async def card_sale(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    condizione = query.data
    context.user_data["condizione"] = condizione

    sale_list = list(TipoVenditore)
    keyboard = [
        [InlineKeyboardButton(sale_list[i].name, callback_data = sale_list[i].value),
         InlineKeyboardButton(sale_list[i + 1].name, callback_data=sale_list[i + 1].value)]
         if i + 1 < len(sale_list) else
        [InlineKeyboardButton(sale_list[i].name, callback_data = sale_list[i].value)]
        for i in range(0, len(sale_list),2)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("1️⃣1️⃣ Seleziona il tipo di venditore 💼", reply_markup = reply_markup)
    return CARD_SALE

async def end_conversation(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    venditore = query.data
    context.user_data["venditore"] = venditore
    
    user = carica_utente(context.user_data["user_id"])

    loc = True if context.user_data['is_asia'] == "True" else False


    sticker_id = "CAACAgIAAxkBAAENZ-dncG3d01MicXCk8oKW2D7aILl4UAACSgMAArVx2gbCfgb6m0gexDYE"
    sent_message = await context.bot.send_sticker(
        chat_id=update.effective_chat.id,
        sticker=sticker_id
    )


    carta = CardPokemon(
        context.user_data['nome_personalizzato'],
        context.user_data['card_name'],
        context.user_data['nome_espansione'],
        context.user_data['codice_espansione'],
        context.user_data['version'],
        context.user_data['card_number'],
        loc,
        context.user_data['lingua'],
        context.user_data['condizione'],
        context.user_data['venditore']
    )

    timeout = 10
    interval = 0.5
    start_time = asyncio.get_event_loop().time()

    while asyncio.get_event_loop().time() - start_time < timeout:
        if carta.url_card:  # Controlla se l'URL è stato generato
            if sent_message:
                await context.bot.delete_message(
                    chat_id=sent_message.chat_id,
                    message_id=sent_message.message_id
                )
            await query.message.reply_text("✅ Carta aggiunta con successo! 🎉")
            user.aggiungi_carta(carta)
            return ConversationHandler.END

        await asyncio.sleep(interval)

    # Timeout raggiunto
    if sent_message:
        await context.bot.delete_message(
            chat_id=sent_message.chat_id,
            message_id=sent_message.message_id
        )
    await query.message.reply_text("‼️ Errore: Impossibile aggiungere la carta (timeout).")
    return ConversationHandler.END

aggiungi_carta_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("add_carta", start_conversation)],
    states={
        NOME_PERSONALIZZATO: [MessageHandler(filters.TEXT & ~filters.COMMAND, nome_personalizzato)],
        BRAND: [CallbackQueryHandler(brand)],
        GENERAZIONE_POKEMON: [CallbackQueryHandler(is_asiatica)],
        IS_ASIATICA: [CallbackQueryHandler(espansione)],
        CARD_ESPANSIONE: [CallbackQueryHandler(nome_card)],
        CARD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, card_num)],
        CARD_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, card_versione)],
        CARD_VERSION: [CallbackQueryHandler(card_language)],
        CARD_LANGUAGE: [CallbackQueryHandler(card_condiction)],
        CARD_CONDITION: [CallbackQueryHandler(card_sale)],
        CARD_SALE: [CallbackQueryHandler(end_conversation)],
    },
    fallbacks=[],
)