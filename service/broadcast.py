from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import json
from service.seleniumService import SeleniumService
from entity.user import carica_utente

async def invia_messaggio_utenti(context: ContextTypes.DEFAULT_TYPE):
    with open("user.json", "r") as f:
        utenti = json.load(f)
    
    for user_id, dati in utenti.items():
        chat_id = dati["chat_id"]
        wishlist = dati["wishlist"]
        dizionari = []

        carte_recap = []

        user = carica_utente(dati["id_utente"])
        wishList = user.get_wishList()
        selenium = SeleniumService()

        try:
            for carta in wishList["carte"]:
                url = carta["url_card"]
                print(carta['nome_personalizzato'])
                data = selenium.update_prize(url)
                dizionari.append(data)
                user.aggiorna_carta_prezzo(carta["id_carta"], data["prezzo_attuale"])

                flags = ['🇬🇧', '🇫🇷', '🇩🇪', '🇪🇸', '🇮🇹', '🇨🇳', '🇯🇵', '🇵🇹', '🏳️', '🇰🇷', '🇹🇼']
                
                percentuale_di_variazione = round(((data["prezzo_attuale"] - carta["prezzo_attuale"]) / carta["prezzo_attuale"]) * 100,2)
                if percentuale_di_variazione < 0:
                    stringa_di_variazione = f"[{percentuale_di_variazione}%🔽]"
                elif percentuale_di_variazione > 0:
                    stringa_di_variazione = f"[+{percentuale_di_variazione}%🔼]"
                else:
                    stringa_di_variazione = ""

                percentuale_di_variazione_tendenza = round(((data["prezzo_di_tendenza"] - data["prezzo_attuale"]) / data["prezzo_attuale"]) * 100,2)
                if percentuale_di_variazione_tendenza < 0:
                    stringa_di_variazione_tendenza = f"[{percentuale_di_variazione_tendenza}%🔽]"
                elif percentuale_di_variazione_tendenza > 0:
                    stringa_di_variazione_tendenza = f"[+{percentuale_di_variazione_tendenza}%🔼]"
                else:
                    stringa_di_variazione_tendenza = ""

                prezzo_settimanale = carta["prezzo_settimanale"]
                percentuale_di_variazione_settimanale = round(((data["prezzo_attuale"] - prezzo_settimanale) / prezzo_settimanale) * 100, 2)
                if percentuale_di_variazione_settimanale < 0:
                    stringa_di_variazione_settimanale = f"[{percentuale_di_variazione_settimanale}%🔽 Settimanale]"
                elif percentuale_di_variazione_settimanale > 0:
                    stringa_di_variazione_settimanale = f"[+{percentuale_di_variazione_settimanale}%🔼 Settimanale]"
                else:
                    stringa_di_variazione_settimanale = f"[0% Settimanale]"

                prezzo_mensile = carta["prezzi_mensili"][-1] 
                percentuale_di_variazione_mensile = round(((data["prezzo_attuale"] - prezzo_mensile) / prezzo_mensile) * 100, 2)
                if percentuale_di_variazione_mensile < 0:
                    stringa_di_variazione_mensile = f"[{percentuale_di_variazione_mensile}%🔽 Mensile]"
                elif percentuale_di_variazione_mensile > 0:
                    stringa_di_variazione_mensile = f"[+{percentuale_di_variazione_mensile}%🔼 Mensile]"
                else:
                    stringa_di_variazione_mensile = f"[0% Mensile]"

                
                nota = ""
                if percentuale_di_variazione_settimanale > 10:
                    nota += "⚡️ Il prezzo settimanale è aumentato notevolmente! "
                if percentuale_di_variazione_settimanale < -10:
                    nota += "📉 Il prezzo settimanale è diminuito drasticamente. Potrebbe essere il momento giusto per acquistare. "
                if data["prezzo_attuale"] > data["prezzo_di_tendenza"] * 1.5:
                    nota += "⚠️ <b>Attenzione!</b> Il prezzo attuale è molto più alto della tendenza, potrebbe essere manipolato. "
                if data["prezzo_attuale"] < data["prezzo_di_tendenza"] * 0.5:
                    nota += "⚠️ <b>Attenzione!</b> Il prezzo attuale è molto più basso della tendenza, potrebbe esserci una svalutazione artificiale. "
                if nota == "":
                    nota = "⏳ Il prezzo è stabile, nessun cambiamento significativo."

                stringa = f"🗂️<a href='{carta['url_card']}'>{carta['nome_personalizzato']}</a> <b>({carta['codice_espansione']} {carta['numero_carta']})</b> {flags[int(carta['lingua_carta'])-1]} [{carta['prezzo_iniziale']}€]\n"
                stringa += f"<b>Prezzo attuale</b>: {carta['prezzo_attuale']}€ {stringa_di_variazione} | <b>Prezzo di tendenza</b>: {data['prezzo_di_tendenza']}€ {stringa_di_variazione_tendenza}\n"
                stringa += f"<b>Variazione Settimanale</b>: {stringa_di_variazione_settimanale} | <b>Variazione Mensile</b>: {stringa_di_variazione_mensile}\n"
                stringa += f"{nota}\n"
                carte_recap.append(stringa)

        finally:
            selenium.quit()

        try:
            messaggio_completo = "📢 Aggiornamento periodico: ecco le ultime novità! 🔄\n\n" + "\n".join(carte_recap)
            await context.bot.send_message(
                chat_id=chat_id,
                text=messaggio_completo,
                parse_mode=ParseMode.HTML 
            )
        except Exception as e:
            print(f"invia_messaggio_utenti | Errore nell'invio del messaggio a {chat_id}: {e}")