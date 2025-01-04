from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from entity.user import carica_utente

async def delete_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = carica_utente(update.message.from_user.id)
    wishList = user.get_wishList()

    if not wishList['carte']:
        await update.message.reply_text("❌ Non ci sono carte da eliminare nella tua wishlist.")
        return

    keyboard = [
        [InlineKeyboardButton(carta['nome_personalizzato'], callback_data=f"delete_{carta['id_carta']}")]
        for carta in wishList['carte']
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🗑️ Scegli la carta che desideri eliminare!", reply_markup=reply_markup
    )

async def handle_card_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith("delete_"):
        user = carica_utente(query.from_user.id)
        carta_id = int(query.data.split("_")[1])

        user.rimuovi_carta(carta_id)

        await query.message.reply_text(f"✅ La carta è stata eliminata con successo! 🎉")
