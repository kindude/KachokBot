import datetime
import os
import pytz
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from src.handlers.exercises import start, record_pushups, record_abs, record_pullups, record_plank, summary
from src.handlers.content import record_anecdote, record_phrase
from src.handlers.scheduled import periodic_message, random_anecdote_job, daily_leaderboard


def main():
    app_env = os.getenv("APP_ENV", "prod")
    load_dotenv(f".env.{app_env}")
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("Environment variable BOT_TOKEN not found")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("p", record_pushups))
    application.add_handler(CommandHandler("a", record_abs))
    application.add_handler(CommandHandler("pu", record_pullups))
    application.add_handler(CommandHandler("plank", record_plank))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(CommandHandler("anecdote", record_anecdote))
    application.add_handler(CommandHandler("phrase", record_phrase))

    london = pytz.timezone("Europe/London")
    application.job_queue.run_repeating(periodic_message, interval=10800, first=60)
    application.job_queue.run_repeating(random_anecdote_job, interval=1800, first=30)
    application.job_queue.run_daily(
        callback=daily_leaderboard,
        time=datetime.time(hour=20, minute=50, tzinfo=london),
        name="daily_leaderboard",
        days=(0, 1, 2, 3, 4, 5, 6),
    )

    print("Bot started!")
    application.run_polling()
