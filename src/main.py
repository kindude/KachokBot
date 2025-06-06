import os
from datetime import time
from random import randint
from datetime import timedelta
from dotenv import load_dotenv
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from src.handlers import start, record, summary, reply_to_mentions, periodic_message, daily_summary

async def schedule_jobs(application):
    application.job_queue.run_once(periodic_message, when=timedelta(seconds=10))

def main():
    load_dotenv()
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError("Environment variable BOT_TOKEN not found")

    application = (
        Application.builder()
        .token(token)
        .build()
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("record", record))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply_to_mentions))

    # Schedule jobs after application is built
    async def post_init(app: Application):
        await schedule_jobs(app)

    application.post_init = post_init  # correctly assign the coroutine

    print("Bot started!")
    application.run_polling()

