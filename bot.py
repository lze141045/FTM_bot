"""
Telegram-Bot: Verkauf von Trading-Signalen (Safe / Riskant)
-------------------------------------------------------------
Ablauf:
1. Kunde tippt in der Willkommens-Gruppe auf einen Deep-Link unter dem
   Video: t.me/deinbot?start=broker  ODER  t.me/deinbot?start=abo
2. Bot öffnet privaten Chat, erkennt den Parameter, schickt sofort die
   passende Zahlungs-Anleitung (Broker-Link ODER Abo-Zahlungsdaten).
3. Bot fragt danach: "Safe oder Riskant?" (zwei Buttons).
4. Sobald der Kunde antwortet, bekommt DER ADMIN (du) automatisch eine
   Nachricht mit der kompletten Auswahl des Kunden.
5. Du prüfst den Zahlungseingang manuell und schickst dem Kunden dann
   von Hand den passenden Gruppen-Invite-Link (Safe oder Riskant).
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)


BOT_TOKEN = os.environ.get("BOT_TOKEN", "DEIN_BOT_TOKEN_HIER")

# Deine eigene numerische Telegram-Nutzer-ID (holst du dir z.B. über
# @userinfobot in Telegram — siehe Anleitung). Hierhin schickt der Bot
# die Benachrichtigungen über neue Kundenauswahl.
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "DEINE_TELEGRAM_ID_HIER")

AFFILIATE_LINK = "https://dein-broker-affiliate-link.com"
MIN_EINZAHLUNG = "250€"

SUBSCRIPTION_PRICE = "49€ / Monat"
PAYMENT_INFO = "PayPal: deine@email.com\noder IBAN: DE00 0000 0000 0000 00"

SUPPORT_CONTACT = "@dein_username"

# ============================================================


OPTION_A_TEXT = (
    "🅰️ *Zahlung über den Broker*\n\n"
    f"1️⃣ Registriere dich über diesen Link:\n{AFFILIATE_LINK}\n\n"
    f"2️⃣ Zahle die Mindesteinzahlung ({MIN_EINZAHLUNG}) beim Broker ein\n\n"
    f"3️⃣ Schick einen Screenshot deiner Einzahlung an {SUPPORT_CONTACT}\n\n"
    "Sag mir jetzt noch kurz, welche Signale du willst 👇"
)

OPTION_B_TEXT = (
    "🅱️ *Monatliches Abo*\n\n"
    f"💶 Preis: {SUBSCRIPTION_PRICE}\n\n"
    f"💳 Zahlungsdetails:\n{PAYMENT_INFO}\n\n"
    f"Schick uns nach der Zahlung einen Beleg an {SUPPORT_CONTACT}.\n\n"
    "Sag mir jetzt noch kurz, welche Signale du willst 👇"
)

GENERIC_START_TEXT = (
    "👋 Willkommen! Schreib mir über die Links in der Gruppe, welche "
    "Zahlungsart du möchtest, dann geht's direkt los. Falls du direkt "
    "hier gelandet bist: schau in der Willkommens-Gruppe unter dem "
    "Video vorbei 🙂"
)

SAFE_REPLY = (
    "✅ Alles notiert! Sobald deine Zahlung bestätigt ist, bekommst du "
    "den Zugangslink zur *Safe-Signal-Gruppe* von uns geschickt."
)

RISK_REPLY = (
    "✅ Alles notiert! Sobald deine Zahlung bestätigt ist, bekommst du "
    "den Zugangslink zur *Riskant-Signal-Gruppe* von uns geschickt."
)


def group_choice_keyboard():
    keyboard = [
        [InlineKeyboardButton("🟢 Safe Signale", callback_data="group_safe")],
        [InlineKeyboardButton("🔴 Riskante Signale", callback_data="group_risk")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Wird ausgelöst, wenn jemand /start (ggf. mit Parameter) sendet."""
    args = context.args  # z.B. ["broker"] oder ["abo"]

    if args and args[0] == "broker":
        context.user_data["payment_choice"] = "Broker (Option A)"
        await update.message.reply_text(
            OPTION_A_TEXT, parse_mode="Markdown", reply_markup=group_choice_keyboard()
        )
    elif args and args[0] == "abo":
        context.user_data["payment_choice"] = "Monatliches Abo (Option B)"
        await update.message.reply_text(
            OPTION_B_TEXT, parse_mode="Markdown", reply_markup=group_choice_keyboard()
        )
    else:
        await update.message.reply_text(GENERIC_START_TEXT)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reagiert auf die Safe/Riskant-Auswahl."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    payment_choice = context.user_data.get("payment_choice", "unbekannt")

    if query.data == "group_safe":
        group_choice = "Safe Signale"
        await query.message.reply_text(SAFE_REPLY, parse_mode="Markdown")
    elif query.data == "group_risk":
        group_choice = "Riskante Signale"
        await query.message.reply_text(RISK_REPLY, parse_mode="Markdown")
    else:
        return

    # Benachrichtigung an den Admin (dich) schicken
    if ADMIN_CHAT_ID and ADMIN_CHAT_ID != "DEINE_TELEGRAM_ID_HIER":
        admin_text = (
            "📩 *Neue Kundenauswahl!*\n\n"
            f"Kunde: {user.full_name} (@{user.username or 'kein Username'})\n"
            f"Zahlungsart: {payment_choice}\n"
            f"Gewünschte Gruppe: {group_choice}\n\n"
            "→ Nach Zahlungseingang den passenden Invite-Link manuell schicken."
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode="Markdown"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Nutz die Links in der Willkommens-Gruppe, um loszulegen 🙂"
    )


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot läuft... (zum Beenden: Strg+C)")
    app.run_polling()


if __name__ == "__main__":
    main()
