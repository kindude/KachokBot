import os
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from src.service.pushup import DatabaseService
import random
load_dotenv()
phrases_to_use = ["Уважение", "Увлажнение", "Мужчина, мужчинский", "Воу-воу-воу", "Дал-дал, ушел", "Это просто зверь!",
                  "Wagamamу и там и тут", "Тремболон колю в очко, чтобы стать большим-большим качком", "Не забывай поменять масло каждые 100 отжиманий"]

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"

CHAT_ID = os.getenv("CHAT_ID")


def get_nickname(update: Update) -> str:
    user = update.effective_user
    return user.username or f"{user.first_name}_{user.id}"


async def record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            pushups_done = int(context.args[0])
            nickname = get_nickname(update)

            service = DatabaseService()
            service.record_pushups(nickname=nickname, pushups_done=pushups_done)
            service.close()
            _summary = service.get_user_summary(nickname)
            index = random.randrange(0, len(phrases_to_use))
            if _summary['today_pushups'] in [4, 6, 15, 52, 69, 93, 95]:
                image_path = MEDIA_DIR / f"{_summary['today_pushups']}.jpg"
                with open(image_path, "rb") as photo:
                    await update.message.reply_photo(photo=photo, caption=f"{phrases_to_use[index]}\n{_summary['today_pushups']}/100")
            else:
                await update.message.reply_text(f"{phrases_to_use[index]}\n{_summary['today_pushups']}/100")

        except ValueError:
            await update.message.reply_text("Введите число, а не буквы 💀")
    else:
        await update.message.reply_text("Пример: /record 30")


async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nickname = get_nickname(update)

    service = DatabaseService()
    text = service.get_user_summary(nickname=nickname)
    service.close()

    reply_text = (
        f"Качок {text['nickname']}\n"
        f"Сделал всего: {text['total_pushups']}\n"
        f"Сегодня: {text['today_pushups']}\n"
        f"Парень качается {text['days_trained']} дней\n"
        f"В среднем {text['average_per_day']} отжиманий в день\n"
        f"Максимум в день {text['max_pushups_in_a_day']}\n"
        f"Прогресс за месяц: {text['monthly_percentage']}%\n"
        f"{text['motivation']}"
    )

    await update.message.reply_text(reply_text)


async def periodic_message(context: ContextTypes.DEFAULT_TYPE):
    current_hour = datetime.now().hour
    if 9 <= current_hour <= 23:
        await context.bot.send_message(chat_id=CHAT_ID, text="Ребятки качаемся!!!")


async def random_anecdote_job(context: ContextTypes.DEFAULT_TYPE):
    service = DatabaseService()
    if random.random() < 0.7:
        anecdote = service.get_random_anecdote()
        if anecdote:
            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=anecdote
            )


async def daily_leaderboard(context: ContextTypes.DEFAULT_TYPE):
    service = DatabaseService()
    text = service.extract_scores()
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=text
    )


async def record_anecdote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nickname = get_nickname(update)
    anecdote = " ".join(context.args)
    service = DatabaseService()
    response = service.record_anecdote(nickname=nickname, anecdote=anecdote)
    await update.message.reply_text(response)


async def start(update: Update):
    await update.message.reply_text("Го качаться!")
