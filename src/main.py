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

    application = Application.builder().token(token).post_init(schedule_jobs).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("record", record))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply_to_mentions))

    print("Bot started!")
    application.run_polling()

    #    application.job_queue.run_daily(
#        daily_summary,
#       time=time(23, 0),
#        name="daily_reminder"
#   )

