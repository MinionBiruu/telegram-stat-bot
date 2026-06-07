import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import init_db, save_activity, get_stats

BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()

init_db()

async def statistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total, active_today, active_7_days, inactive_30_days = get_stats()

    text = f"""
📊 Statistik Grup

👥 Total Member : {total}
🟢 Aktif Hari Ini : {active_today}
📅 Aktif 7 Hari : {active_7_days}
🔴 Tidak Aktif >30 Hari : {inactive_30_days}
"""
    await update.message.reply_text(text)

async def track_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.from_user:
        save_activity(update.message.from_user)

telegram_app.add_handler(CommandHandler("statistik", statistik))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_message))

@app.route("/")
def home():
    return "Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    asyncio.run(telegram_app.process_update(update))
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
