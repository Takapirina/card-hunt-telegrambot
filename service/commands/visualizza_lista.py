from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from entity.user import carica_utente

async def get_lista(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = carica_utente(update.message.from_user.id)
    wishList = user.get_wishList()

    if not wishList['carte']:
        await update.message.reply_text("Non ci sono carte da eliminare nella tua wishlist.")
        return

    keyboard = [
        [InlineKeyboardButton(carta['nome_personalizzato'], callback_data=f"info_{carta['id_carta']}")]
        for carta in wishList['carte']
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"{user.nome_utente} ecco la tua lista", reply_markup=reply_markup
    )

async def handle_get_info_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Controlla che sia una callback di informazioni
    if query.data.startswith("info_"):
        user = carica_utente(query.from_user.id)
        carta_id = int(query.data.split("_")[1])  # Estrai l'ID della carta

        carta = user.get_carta(carta_id)
        flags = ['🇬🇧','🇫🇷','🇩🇪','🇪🇸','🇮🇹','🇨🇳','🇯🇵','🇵🇹','🏳️','🇰🇷','🇹🇼']

        prezzo_iniziale = float(carta['prezzo_iniziale'])
        prezzo_corrente = float(carta['prezzo_attuale'])
        percentuale = ((prezzo_corrente - prezzo_iniziale) / prezzo_iniziale) * 100

        await query.message.reply_text(
            f"🗂️<b>{carta['nome_personalizzato']}</b>🗂️\n"
            f"{flags[int(carta['lingua_carta'])-1]} {carta['nome_carta']} "
            f"<i>{carta['espansione_nome']} ({carta['codice_espansione']}-{carta['numero_carta']})</i>\n\n"
            f"💸 <b>Prezzo corrente</b>: {carta['prezzo_attuale']}€ {'🔴' if percentuale < 0 else '🟢'}{percentuale:.2f}%\n"
            f"🔗 <a href='{carta['url_card']}'>Vai a CardMarket</a>",
            parse_mode=ParseMode.HTML
        )