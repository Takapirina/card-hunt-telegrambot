from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, CallbackContext

from entity.brand import Brand, GenerazionePokemon, BrandPokemon

BRAND, GENERAZIONE_POKEMON, IS_ASIATICA, NOME_ESPANSIONEPOKEMON, CODICE_ESPANSIONEPOKEMON = range(5)

async def start_conversation(update: Update, context: CallbackContext) -> int:
    keyboard = [[InlineKeyboardButton(brand.name, callback_data=brand.value)] for brand in Brand]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Scegli il brand dell'espansione", reply_markup=reply_markup)
    return BRAND

async def brand(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    brand = query.data
    context.user_data["brand"] = brand

    match brand:
        case Brand.POKEMON.value:
            return await generation(update, context)
        case Brand.ONEPIECE.value:
            await query.message.reply_text(f"il seguente brand: {brand} non è al momento implementato")
            return ConversationHandler.END

async def generation(update: Update, context: CallbackContext) -> int:
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
    await update.callback_query.message.reply_text(
        "Scegli la generazione del brand Pokémon da aggiungere:", reply_markup=reply_markup
    )
    return GENERAZIONE_POKEMON

async def is_asiatica(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Occidentale", callback_data="False"),
        InlineKeyboardButton("Orientale", callback_data="True")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query
    await query.answer()

    gen = query.data
    context.user_data["gen"] = gen
    await query.message.reply_text("Inserisci l'area geografica dell'espansione:", reply_markup=reply_markup)
    return IS_ASIATICA

async def name_pokemon_espansion(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    is_asia = query.data
    context.user_data["is_asia"] = is_asia
    await query.message.reply_text("Inserisci il nome dell'espansione completa (es: 'VSTAR Universe'):")
    return NOME_ESPANSIONEPOKEMON

async def cod_espansione(update: Update, context: CallbackContext) -> int:
    nome_espansione = "-".join(update.message.text.split()).title()
    context.user_data["nome_espansione"] = nome_espansione

    await update.message.reply_text("Inserisci il codice dell'espansione completa (es: 's12'):")
    return CODICE_ESPANSIONEPOKEMON

async def add_espansione_pokemon(update: Update, context: CallbackContext) -> int:
    codice_espansione = update.message.text
    context.user_data["codice_espansione"] = codice_espansione

    is_asiatica = True
    if context.user_data["is_asia"] == "False":
        is_asiatica = False

    brandPokemon = BrandPokemon()
    brandPokemon.add_espansione(
        context.user_data["gen"],
        context.user_data["nome_espansione"],
        context.user_data["codice_espansione"],
        is_asiatica
        )

    await update.message.reply_text(
        f"Espansione aggiunta con successo:\n"
    )
    return ConversationHandler.END

conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('add_espansione', start_conversation)],
    states={
        BRAND: [CallbackQueryHandler(brand)],
        GENERAZIONE_POKEMON: [CallbackQueryHandler(is_asiatica)],
        IS_ASIATICA: [CallbackQueryHandler(name_pokemon_espansion)],
        NOME_ESPANSIONEPOKEMON: [MessageHandler(filters.TEXT & ~filters.COMMAND, cod_espansione)],
        CODICE_ESPANSIONEPOKEMON: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_espansione_pokemon)]
    },
    fallbacks=[]
)