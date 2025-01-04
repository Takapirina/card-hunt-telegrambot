from telegram import Update
from telegram.ext import ContextTypes, CallbackContext

async def set_commands(update: Update, context: CallbackContext) -> None:
    """Imposta i comandi personalizzati per il bot"""
    bot = context.bot
    commands = [
        ('help', 'Mostra i comandi disponibili'),
        ('add_espansione', 'aggiungi espansione'),
        ('del_espansione', 'elimina espansione'),
        ('add_carta', 'aggiungi carta'),
        ('del_carta', 'elimina carta'),
        ('lista', 'mostra wishlist'),
    ]
    await bot.set_my_commands(commands)
    await update.message.reply_text("I comandi sono stati aggiornati! ✅")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Risponde con l'ID e il nickname dell'utente che invia il messaggio."""
    user = update.message.from_user
    user_id = user.id
    username = user.username if user.username else "Utente Anonimo"

    await update.message.reply_text(
        f"👋 Ciao {username}! Benvenuto nel bot per monitorare i prezzi delle carte su CardMarket! 📈\n\n"
        f"Ecco cosa puoi fare:\n\n"
        f"📌 Comandi principali:\n"
        f" - /start ➡️ Crea un nuovo profilo.\n"
        f" - /help ➡️ Visualizza la lista completa dei comandi.\n\n"
        f"📦 Gestione Espansioni:\n"
        f" - /add_espansione ➡️ Aggiungi una nuova espansione di un brand.\n"
        f" - /del_espansione ➡️ Rimuovi un'espansione esistente.\n\n"
        f"🃏 Gestione Carte:\n"
        f" - /add_carta ➡️ Aggiungi una carta alla tua lista da monitorare.\n"
        f" - /del_carta ➡️ Elimina una carta dalla tua wishlist.\n"
        f" - /lista ➡️ Visualizza la tua wishlist.\n\n"
        f"✨ Inizia subito!\n"
        f"Usa i comandi qui sopra per configurare il bot e monitorare le tue carte preferite!"
    )