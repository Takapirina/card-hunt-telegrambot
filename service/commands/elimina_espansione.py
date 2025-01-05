from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, CallbackContext

from entity.brand import Brand, GenerazionePokemon, BrandPokemon

BRAND, GENERAZIONE_POKEMON, IS_ASIATICA, ESPANIONE = range(4)

async def start_conversation(update: Update, context: CallbackContext)-> int:
    keyboard = [[InlineKeyboardButton(brand.name, callback_data= brand.value)] for brand in Brand]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔍 Seleziona il brand dell’espansione che vuoi rimuovere!", reply_markup=reply_markup)
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
            await query.message.reply_text(f"⚠️ Ops! Il brand “{brand}” non è ancora disponibile. Prova un altro!")
            return ConversationHandler.END
        
async def generation(update: Update, context: CallbackContext)-> int:
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
        "🎮 Scegli la generazione di Pokémon in cui si trova l’espansione che vuoi eliminare!", reply_markup=reply_markup
    )
    return GENERAZIONE_POKEMON

async def is_asiatica(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Occidentale", callback_data="occidentale"),
        InlineKeyboardButton("Orientale", callback_data="Orientale")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query
    await query.answer()

    gen = query.data
    context.user_data["gen"] = gen
    await query.message.reply_text("🌍 Seleziona l’area geografica dell’espansione per eliminarla!", reply_markup=reply_markup)
    return IS_ASIATICA

async def espansione(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    is_asia = query.data
    context.user_data["is_asia"] = is_asia

    brand_data = BrandPokemon().get_brand_json()
    brand_key = Brand.POKEMON.value

    gen = context.user_data["gen"]

    expansions = brand_data[brand_key][gen][is_asia]

    if len(expansions) > 0:
        keyboard = [
            [InlineKeyboardButton(esp["nome_espansione"], callback_data=esp["id_espansione"])]
            for esp in expansions
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text("🗑️ Scegli l’espansione che desideri eliminare!", reply_markup=reply_markup)
        return ESPANIONE
    else:
        await query.message.reply_text("❌ Niente espansioni trovate per la generazione che hai scelto. Prova un’altra!")
        return ConversationHandler.END

async def elimina_espansione(update: Update, context: CallbackContext)-> int:
    query = update.callback_query
    await query.answer()

    id_esp = query.data
    context.user_data["id_espansione"] = id_esp

    sezione = True if context.user_data["is_asia"] == "Orientale" else False

    brandPokemon = BrandPokemon()
    brandPokemon.remove_espansione(id_esp, context.user_data["gen"], sezione)

    await query.message.reply_text(f"✅ Espansione eliminata con successo! 🎉")
    return ConversationHandler.END

async def exit_conversation(update, context):
    await update.message.reply_text("🚶‍♂️ Conversazione terminata.")
    return ConversationHandler.END

delete_conversationHandler = ConversationHandler(
    entry_points=[CommandHandler('del_espansione',start_conversation)],
    states = {
        BRAND: [CallbackQueryHandler(brand)],
        GENERAZIONE_POKEMON: [CallbackQueryHandler(is_asiatica)],
        IS_ASIATICA: [CallbackQueryHandler(espansione)],
        ESPANIONE: [CallbackQueryHandler(elimina_espansione)]
    },
    fallbacks=[
        CommandHandler('exit', exit_conversation),
    ]
)