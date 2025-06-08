from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from datetime import datetime, date, time
from src.service.pushup import DatabaseService
import random
recorded_values = []


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
            summary = service.get_user_summary(nickname)
            if summary['total_pushups'] < 100:
                await update.message.reply_text(f"Ну мужчина, мужчинский! Записал!")
                #await update.message.reply_text(f"Тебя пидором, но пока что карандашом")
            else:
                await update.message.reply_text(f"Вот это мужчина, посмотрите на него")
            # await update.message.reply_text(f"Записал {pushups_done} отжиманий за @{nickname}! ")

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


async def reply_to_mentions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    bot_username = (await context.bot.get_me()).username.lower()

    if bot_username in text:
        parts = text.split()
        if len(parts) > 1:
            command = parts[1]
            args = parts[2:] if len(parts) > 2 else []
            if command == "/Отжал" and args:
                try:
                    value = float(args[0])
                    recorded_values.append(value)
                    await update.message.reply_text(f": {value}")
                except ValueError:
                    await update.message.reply_text("ЭТО")
                    await update.message.reply_text("ОЧЕНЬ")
                    await update.message.reply_text("СМЕШНО")
            else:
                await update.message.reply_text("Unknown command after mention.")
        else:
            await update.message.reply_text("Hi! Use /record <value> or /summary.")


async def periodic_message(context: ContextTypes.DEFAULT_TYPE):
    current_hour = datetime.now().hour
    if 9 <= current_hour <= 23:
        await context.bot.send_message(chat_id="-1002260855576", text="Ребятки качаемся!!!")


async def random_anecdote_job(context: ContextTypes.DEFAULT_TYPE):
    service = DatabaseService()
    if random.random() < 0.7:
        anecdote = service.get_random_anecdote()
        if anecdote:
            await context.bot.send_message(
                chat_id="-1002260855576",
                text=anecdote
            )

# async def random_anecdote_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     service = DatabaseService()
#     if random.random() < 1:
#         anecdote = service.get_random_anecdote()
#         if anecdote:
#             await update.message.reply_text(anecdote)

async def record_anecdote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nickname = get_nickname(update)
    anecdote = " ".join(context.args)
    service = DatabaseService()
    response = service.record_anecdote(nickname=nickname, anecdote=anecdote)
    await update.message.reply_text(response)

async def daily_summary(context: ContextTypes.DEFAULT_TYPE):
    service = DatabaseService()
    today = date.today()

    all_users = service.repo.get_all_users()
    summary_lines = []

    for user in all_users:
        entries = service.repo.get_pushups_for_user_on_day(user.id, today)
        total = sum(e.pushups_done for e in entries)

        summary_lines.append(f"👤 {user.nickname}: {total} отжиманий")

    service.close()

    if not summary_lines:
        summary_text = "Сегодня никто не отжимался 😴"
    else:
        summary_text = "📊 Сводка за сегодня:\n\n" + "\n".join(summary_lines)

    await context.bot.send_message(chat_id="-1002260855576", text=summary_text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Го качаться!")
