from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackContext, CallbackQueryHandler, Updater
from dotenv import load_dotenv
import os
from datetime import time

from service.commands.start import start
from service.commands.help import help, set_commands
from service.commands.aggiungi_espansione import conversation_handler
from service.commands.elimina_espansione import delete_conversationHandler
from service.commands.aggiungi_carta import aggiungi_carta_conversation_handler

from service.commands.sticker import send_sticker_example
from service.commands.visualizza_lista import get_lista, handle_get_info_card

from service.commands.elimina_carta import delete_card, handle_card_deletion

from service.broadcast import invia_messaggio_utenti

from service.dropBoxService import download_user_json_file, downloads_wishlist_user ,download_brand_json_file

from web2 import refresh_access_token, update_access_token
from apscheduler.schedulers.background import BackgroundScheduler

def refresh_token_periodically():
    refresh_token = os.getenv("DROP_BOX_REFRESH_TOKEN")
    if refresh_token:
        new_access_token = refresh_access_token(refresh_token, os.getenv("APP_KEY"), os.getenv("APP_KEY_SECRET"))
        if new_access_token:
            update_access_token(new_access_token)
            print("Access token aggiornato!")
        else:
            print("Errore nel rinnovare l'access token.")
    else:
        print("Non è stato trovato il refresh token.")
        
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_token_periodically, 'interval', hours=3)  # Esegui ogni 3 ore
    scheduler.start()


def main():
    load_dotenv()
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    if application is None:
        print("Errore: applicazione non creata!")
        return

    download_user_json_file()
    downloads_wishlist_user()
    download_brand_json_file()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("sticker", send_sticker_example))
    application.add_handler(CommandHandler("lista", get_lista))
    application.add_handler(CommandHandler("del_carta", delete_card))
    
    application.add_handler(aggiungi_carta_conversation_handler)
    application.add_handler(conversation_handler)
    application.add_handler(delete_conversationHandler)
    
    application.add_handler(CallbackQueryHandler(handle_callback))

    if application.job_queue:
        application.job_queue.run_daily(
            invia_messaggio_utenti,
            time(hour=16, minute=15, second=0), 
        )
    else:
        print("Errore: job_queue non è stato creato!")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data.startswith("delete_"):
        await handle_card_deletion(update, context)
    elif query.data.startswith("info_"):
        await handle_get_info_card(update, context)

if __name__ == "__main__":
    start_scheduler()
    main()