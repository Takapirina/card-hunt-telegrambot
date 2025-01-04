from telegram import Update
from telegram.ext import ContextTypes

from entity.user import Utente

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_id = user.id
    username = user.username if user.username else "Utente senza nome"
    chat_id = update.effective_chat.id

    utente = Utente(user_id, username, chat_id)

    await update.message.reply_text(
        f"🎉 Benvenuto, {username}! Grazie per aver scelto di utilizzare il bot! 😊\n\n💬 Per maggiori informazioni, usa il comando /help"
    )