import datetime
import os
import pytz
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from src.handlers import start, record, summary, periodic_message, record_anecdote, \
    random_anecdote_job, daily_leaderboard, useful_article


async def setup_jobs(application: Application) -> None:
    application.job_queue.run_repeating(periodic_message, interval=10800, first=5)


def main():
    load_dotenv()
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError("Environment variable BOT_TOKEN not found")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("record", record))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(CommandHandler("anecdote", record_anecdote))
    application.add_handler(CommandHandler("joke", random_anecdote_job))

    application.job_queue.run_repeating(periodic_message, interval=10800, first=60)
    application.job_queue.run_repeating(random_anecdote_job, interval=1800, first=30)

    application.job_queue.run_daily(
        callback=daily_leaderboard,
        time=datetime.time(hour=23, minute=50, tzinfo=pytz.timezone('Europe/London')),
        name="daily_leaderboard",
        days=(0, 1, 2, 3, 4, 5, 6),
    )
    application.job_queue.run_daily(
        callback=useful_article,
        time=datetime.time(hour=9, minute=30, tzinfo=pytz.timezone('Europe/London')),
        name="useful_article_morning",
        days=(0, 1, 2, 3, 4, 5, 6),
    )

    application.job_queue.run_daily(
        callback=useful_article,
        time=datetime.time(hour=21, minute=30, tzinfo=pytz.timezone('Europe/London')),
        name="useful_article_evening",
        days=(0, 1, 2, 3, 4, 5, 6),
    )

    print("Bot started!")
    application.run_polling()

