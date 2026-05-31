import os
import random
from datetime import datetime
from telegram.ext import ContextTypes
from ..service.exercises import ExerciseService
from ..service.content import ContentService

_ACTIVE_HOURS = range(9, 21)


async def periodic_message(context: ContextTypes.DEFAULT_TYPE):
    if datetime.now().hour in _ACTIVE_HOURS:
        await context.bot.send_message(chat_id=os.getenv("CHAT_ID"), text="Ребятки качаемся!!!")


async def random_anecdote_job(context: ContextTypes.DEFAULT_TYPE):
    if datetime.now().hour not in _ACTIVE_HOURS or random.random() >= 0.5:
        return
    service = ContentService()
    try:
        anecdote = service.get_random_anecdote()
        if anecdote:
            await context.bot.send_message(chat_id=os.getenv("CHAT_ID"), text=anecdote)
    finally:
        service.close()


async def daily_leaderboard(context: ContextTypes.DEFAULT_TYPE):
    service = ExerciseService()
    try:
        text = service.build_leaderboard()
    finally:
        service.close()
    await context.bot.send_message(chat_id=os.getenv("CHAT_ID"), text=text)
