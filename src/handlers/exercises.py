import asyncio
import random
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from . import get_nickname
from ..service.exercises import ExerciseService, format_duration
from ..service.content import ContentService

_MILESTONE_PHOTOS = {4, 6, 15, 52, 69, 93, 95}
_MEDIA_DIR = Path(__file__).resolve().parent.parent.parent / "media"
_FALLBACK_PHRASES = [
    "Уважение", "Увлажнение", "Мужчина, мужчинский", "Воу-воу-воу",
    "Дал-дал, ушел", "Это просто зверь!", "Wagamamу и там и тут",
    "Тремболон колю в очко, чтобы стать большим-большим качком",
    "Не забывай поменять масло каждые 100 отжиманий",
]


def _parse_plank(value: str) -> int:
    """Parse '1:30' or '90' into total seconds."""
    if ":" in value:
        parts = value.split(":", 1)
        return int(parts[0]) * 60 + int(parts[1])
    return int(value)


async def _get_phrase(content_svc: ContentService, exercise_context: str) -> str:
    phrase = await asyncio.to_thread(content_svc.get_motivational_phrase, exercise_context)
    return phrase or random.choice(_FALLBACK_PHRASES)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Го качаться! 💪")


async def record_pushups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _record_reps(update, context, exercise_type="pushups")


async def record_abs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _record_reps(update, context, exercise_type="abs")


async def record_pullups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _record_reps(update, context, exercise_type="pullups")


async def record_plank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Введи время планки после команды.\n"
            "Пример: /plank 1:30 (1 минута 30 секунд) или /plank 90 (секунды)"
        )
        return

    try:
        seconds = _parse_plank(context.args[0])
    except (ValueError, IndexError):
        await update.message.reply_text("Неверный формат. Используй /plank 1:30 или /plank 90")
        return

    if seconds <= 0:
        await update.message.reply_text("Время должно быть больше нуля.")
        return

    nickname = get_nickname(update)
    exercise_svc = ExerciseService()
    content_svc = ContentService()
    try:
        exercise_svc.record_plank(nickname=nickname, duration_seconds=seconds)
        stats = exercise_svc.get_user_summary(nickname)
        today_plank = stats["today_plank"]
        exercise_context = f"планку суммарно {today_plank} за сегодня"
        phrase = await _get_phrase(content_svc, exercise_context)
    finally:
        exercise_svc.close()
        content_svc.close()

    await update.message.reply_text(f"{phrase}\n⏱ Планка сегодня: {today_plank}")


async def _record_reps(update: Update, context: ContextTypes.DEFAULT_TYPE, exercise_type: str):
    if not context.args:
        await update.message.reply_text("Введи количество после команды. Пример: /p 50")
        return

    try:
        reps = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Введи целое число после команды.")
        return

    if reps <= 0:
        await update.message.reply_text("Количество должно быть больше нуля.")
        return

    nickname = get_nickname(update)
    exercise_svc = ExerciseService()
    content_svc = ContentService()
    try:
        if exercise_type == "pushups":
            exercise_svc.record_pushups(nickname=nickname, pushups_done=reps)
            stats = exercise_svc.get_user_summary(nickname)
            progress = stats["today_pushups"]
            label = "💪 Отжиманий сегодня"
            exercise_context = f"{progress} отжиманий за сегодня"
        elif exercise_type == "abs":
            exercise_svc.record_abs(nickname=nickname, abs_done=reps)
            stats = exercise_svc.get_user_summary(nickname)
            progress = stats["today_abs"]
            label = "🧱 Пресс сегодня"
            exercise_context = f"{progress} повторений на пресс за сегодня"
        else:
            exercise_svc.record_pullups(nickname=nickname, pullups_done=reps)
            stats = exercise_svc.get_user_summary(nickname)
            progress = stats["today_pullups"]
            label = "🏋️ Подтягиваний сегодня"
            exercise_context = f"{progress} подтягиваний за сегодня"

        phrase = await _get_phrase(content_svc, exercise_context)
    finally:
        exercise_svc.close()
        content_svc.close()

    if exercise_type == "pushups" and progress in _MILESTONE_PHOTOS:
        image_path = _MEDIA_DIR / f"{progress}.jpg"
        if image_path.exists():
            with open(image_path, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=f"{phrase}\n{label}: {progress}/100"
                )
            return

    await update.message.reply_text(f"{phrase}\n{label}: {progress}/100")


async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nickname = get_nickname(update)
    service = ExerciseService()
    try:
        s = service.get_user_summary(nickname=nickname)
    finally:
        service.close()

    text = (
        f"💪 Качок {s['nickname']}\n"
        f"📅 Тренировочных дней: {s['days_trained']}\n\n"

        f"📊 За всё время:\n"
        f"  💪 Отжимания — {s['total_pushups']} (макс/день: {s['max_pushups_in_a_day']})\n"
        f"  🧱 Пресс — {s['total_abs']} (макс/день: {s['max_abs_in_a_day']})\n"
        f"  🏋️ Подтягивания — {s['total_pullups']} (макс/день: {s['max_pullups_in_a_day']})\n"
        f"  ⏱ Планка — {s['total_plank']} (макс/день: {s['max_plank']})\n\n"

        f"🗓 Сегодня:\n"
        f"  💪 Отжимания — {s['today_pushups']}/100\n"
        f"  🧱 Пресс — {s['today_abs']}/100\n"
        f"  🏋️ Подтягивания — {s['today_pullups']}/100\n"
        f"  ⏱ Планка — {s['today_plank']}\n\n"

        f"📆 Прогресс за месяц (цель 100/день):\n"
        f"  💪 Отжимания — {s['monthly_percentage_pushups']}%\n"
        f"  🧱 Пресс — {s['monthly_percentage_abs']}%\n"
        f"  🏋️ Подтягивания — {s['monthly_percentage_pullups']}%\n\n"

        f"🧠 {s['motivation']}"
    )
    await update.message.reply_text(text)
