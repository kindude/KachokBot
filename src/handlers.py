import os
import re
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from src.parser import Parser
from src.service.pushup import DatabaseService
import random

# from src.speech_recognize import Transcriber

load_dotenv()
phrases_to_use = ["Уважение", "Увлажнение", "Мужчина, мужчинский", "Воу-воу-воу", "Дал-дал, ушел", "Это просто зверь!",
                  "Wagamamу и там и тут", "Тремболон колю в очко, чтобы стать большим-большим качком", "Не забывай поменять масло каждые 100 отжиманий"]

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"

CHAT_ID = os.getenv("CHAT_ID")


def get_nickname(update: Update) -> str:
    user = update.effective_user
    return user.username or f"{user.first_name}_{user.id}"


async def record_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phrase = " ".join(context.args).strip()

    if not phrase:
        await update.message.reply_text("Введите фразу после команды. Пример: /phrase Уважение 💪")
        return

    service = DatabaseService()
    response = service.record_phrase(phrase)
    service.close()

    await update.message.reply_text(response or "Записано")


# async def handle_motivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     generator = BloomGenerator()
#     service = DatabaseService()
#     phrases = service.all_phrases()
#
#     if not phrases:
#         await update.message.reply_text("Нет сохранённых мотивационных фраз 😢")
#         return
#
#     # Get 5 random phrases
#     import random
#
#     prompt = (
#         "Give me a short motivational phrase:\n"
#         "Phrase:"
#     )
#     response = generator.generate(prompt, max_length=50)
#
#     return response


async def record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            message_text = update.message.text
            reps_done = int(context.args[0])
            print(reps_done)
            nickname = get_nickname(update)
            service = DatabaseService()

            if "/p" in message_text:
                service.record_pushups(nickname=nickname, pushups_done=reps_done)
                _summary = service.get_user_summary(nickname)
                progress = _summary['today_pushups']
            elif "/a" in message_text:
                service.record_abs(nickname=nickname, abs_done=reps_done)
                _summary = service.get_user_summary(nickname)
                progress = _summary['today_abs']
            else:
                await update.message.reply_text("Please use /p for pushups or /a for abs.")
                service.close()
                return

            motivational_phrase = service.get_random_motivational_phrase()
            service.close()


            if not motivational_phrase:
                motivational_phrase = random.choice(phrases_to_use)
            # motivational_phrase = await handle_motivate(update, context)

            # Show photo if applicable
            if progress in [4, 6, 15, 52, 69, 93, 95]:
                image_path = MEDIA_DIR / f"{progress}.jpg"
                if image_path.exists():
                    with open(image_path, "rb") as photo:
                        await update.message.reply_photo(photo=photo, caption=f"{motivational_phrase}\n{progress}/100")
                    return

            await update.message.reply_text(f"{motivational_phrase}\n{progress}/100")

        except ValueError:
            await update.message.reply_text("Please enter a valid number after the command.")
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {e}")


async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nickname = get_nickname(update)

    service = DatabaseService()
    text = service.get_user_summary(nickname=nickname)
    service.close()

    reply_text = (
        f"💪 Качок {text['nickname']}\n\n"
        f"📊 Общая статистика:\n"
        f"– Отжиманий всего: {text['total_pushups']}\n"
        f"– Пресс всего: {text['total_abs']}\n"
        f"– Тренировочных дней: {text['days_trained']}\n"
        f"– Среднее отжиманий в день: {text['average_per_day']}\n"
        f"– Максимум отжиманий за день: {text['max_pushups_in_a_day']}\n"
        f"– Среднее количество пресса в день: {text['average_abs_per_day']}\n"
        f"– Максимум пресса за день: {text['max_abs_in_a_day']}\n\n"
        f"📅 Сегодня:\n"
        f"– Отжиманий: {text['today_pushups']}\n"
        f"– Пресс: {text['today_abs']}\n\n"
        f"📆 Прогресс за месяц:\n"
        f"– Отжимания: {text['monthly_percentage_pushups']}%\n"
        f"– Пресс: {text['monthly_percentage_abs']}%\n\n"
        f"🧠 {text['motivation']}"
    )

    await update.message.reply_text(reply_text)



async def periodic_message(context: ContextTypes.DEFAULT_TYPE):
    current_hour = datetime.now().hour
    if 9 <= current_hour <= 23:
        await context.bot.send_message(chat_id=CHAT_ID, text="Ребятки качаемся!!!")


async def random_anecdote_job(context: ContextTypes.DEFAULT_TYPE):
    current_hour = datetime.now().hour
    if 9 <= current_hour <= 23:
        service = DatabaseService()
        try:
            if random.random() < 0.5:
                anecdote = service.get_random_anecdote()
                if anecdote:
                    await context.bot.send_message(chat_id=CHAT_ID, text=anecdote)
        finally:
            service.close()


# async def recognize_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print("Hello world")
#     transcriber = Transcriber()
#     print(transcriber.transcribe("D:\\Practice\\KachokBot\\voices\\audio_2025-06-10_12-04-06.ogg"))


async def daily_leaderboard(context: ContextTypes.DEFAULT_TYPE):
    service = DatabaseService()
    text = service.extract_scores()
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=text
    )


async def useful_article(context: ContextTypes.DEFAULT_TYPE):
    parser = Parser()
    service = DatabaseService()

    articles = parser.parse_all()
    random.shuffle(articles)
    title, url = articles[0]
    if not service.find_article_if_exists_by_url(url):
        service.save_article(title, url)
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"{title}\n{url}"
        )
    return None


# async def track_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print("Tets")
#     message = update.message
#
#     if message is None:
#         return
#
#     user = message.from_user.full_name if message.from_user else "Unknown user"
#
#     if message.voice:
#         print(f"[VOICE] From {user} - duration: {message.voice.duration} sec")
#         file = await context.bot.get_file(message.voice.file_id)
#         file_path = f"voices/{message.voice.file_id}.ogg"
#         await file.download_to_drive(file_path)
#
#         transcriber = Transcriber(language="ru-RU")
#         transcribed_text = transcriber.transcribe(file_path)
#
#         # Reply with transcription (or a fallback message)
#         reply = transcribed_text if transcribed_text else ""
#         await update.message.reply_text(reply)
#
#         # Clean up the saved file
#         try:
#             os.remove(file_path)
#             print(f"Deleted file: {file_path}")
#         except Exception as e:
#             print(f"Error deleting file: {e}")
#     # elif message.text:
#     #     print(f"[TEXT] From {user}: {message.text}")


async def record_anecdote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nickname = get_nickname(update)
    anecdote = " ".join(context.args)
    service = DatabaseService()
    response = service.record_anecdote(nickname=nickname, anecdote=anecdote)
    await update.message.reply_text(response)


async def record_number_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    match = re.match(r'^/(\d+)$', message_text)
    if match:
        number = match.group(1)
        context.args = [number]
        await record(update, context)
    else:
        await update.message.reply_text("Invalid command format. Use /<number>.")


async def start(update: Update):
    await update.message.reply_text("Го качаться!")
