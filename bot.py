import os
import logging
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from database import init_db, subscribe_user, unsubscribe_user, get_all_subscribers, is_news_new
from news import fetch_football_news

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

async def broadcast_news(context: ContextTypes.DEFAULT_TYPE):
    news_list = await fetch_football_news()
    subs = get_all_subscribers()
    
    for news in news_list:
        if is_news_new(news['hash']):
            message = (
                f"⚽️ **Breaking Football News**\n\n"
                f"📣 **{news['title']}**\n\n"
                f"📝 {news['description']}\n\n"
                f"🔗 [Read more]({news['url']})"
            )
            for user_id in subs:
                try:
                    await context.bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
                except Exception:
                    continue # Skip users who blocked the bot

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to **GoalSphereBot**! 🏟️\n\nI deliver the latest football news twice daily.\n"
        "Use /subscribe to get automatic updates or /news for instant news.",
        parse_mode='Markdown'
    )

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news_list = await fetch_football_news()
    if not news_list:
        await update.message.reply_text("Unable to fetch news right now. Try again later.")
        return
    
    news = news_list[0]
    message = f"⚽️ **Latest Update**\n\n**{news['title']}**\n\n{news['description']}\n\n🔗 [Read more]({news['url']})"
    await update.message.reply_text(message, parse_mode='Markdown')

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if subscribe_user(update.effective_user.id):
        await update.message.reply_text("✅ Subscribed! You'll receive updates every morning and evening.")
    else:
        await update.message.reply_text("You are already subscribed.")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if unsubscribe_user(update.effective_user.id):
        await update.message.reply_text("❌ Unsubscribed. You will no longer receive daily updates.")
    else:
        await update.message.reply_text("You are not currently subscribed.")

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))

    # Scheduling: 08:00 and 20:00
    job_queue = app.job_queue
    job_queue.run_daily(broadcast_news, time=datetime.time(hour=8, minute=0))
    job_queue.run_daily(broadcast_news, time=datetime.time(hour=20, minute=0))

    app.run_polling()

if __name__ == "__main__":
    main()
