import os
from datetime import time

from dotenv import load_dotenv
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from src.handlers import start, record, summary, reply_to_mentions, periodic_message, daily_summary, record_anecdote, \
    random_anecdote_job


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
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply_to_mentions))

    application.job_queue.run_repeating(periodic_message, interval=10800, first=5)
    application.job_queue.run_repeating(random_anecdote_job, interval=3600, first=60)
    print("Bot started!")
    application.run_polling()

