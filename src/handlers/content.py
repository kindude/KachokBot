from telegram import Update
from telegram.ext import ContextTypes
from . import get_nickname
from ..service.content import ContentService


async def record_anecdote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nickname = get_nickname(update)
    anecdote = " ".join(context.args).strip()

    if not anecdote:
        await update.message.reply_text("Введи анекдот после команды. Пример: /anecdote Текст анекдота")
        return

    service = ContentService()
    try:
        response = service.record_anecdote(nickname=nickname, anecdote=anecdote)
    finally:
        service.close()

    await update.message.reply_text(response)


async def record_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phrase = " ".join(context.args).strip()

    if not phrase:
        await update.message.reply_text("Введи фразу после команды. Пример: /phrase Уважение 💪")
        return

    service = ContentService()
    try:
        response = service.record_phrase(phrase)
    finally:
        service.close()

    await update.message.reply_text(response)
