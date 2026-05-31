"""Seed motivational phrases into the database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.db import SessionLocal
from src.models import MotivationalPhrases

PHRASES = [
    "Уважение",
    "Увлажнение",
    "Мужчина, мужчинский",
    "Воу-воу-воу",
    "Дал-дал, ушел",
    "Это просто зверь!",
    "Wagamamу и там и тут",
    "Тремболон колю в очко, чтобы стать большим-большим качком",
    "Не забывай поменять масло каждые 100 отжиманий",
    "Пососемся ?",
    "И раз…ливного полторашку, светлого",
    "Wubba Lubba Dub-Dub !",
    "запомнил - забыл.",
    "я не считал - давай по новой",
    "-20/100",
    "Можете сделать рекламу моего члена ? Или такие большие проекты не рекламируете ?",
    "маловато",
    "не дорабатываешь, уебище",
    "купец",
    "окак",
    "Ты как Брэд Питт",
    "Член Егора",
    "количество твоих сделанных отжиманий это анекдот",
    "а может еще чуть-чуть 🤏?",
    "хвхахахахахахха",
    "поцелуй меня в бипки",
    "У нас гумманитариев только 2 проблемы - мы не умеем считать",
]


def main():
    db = SessionLocal()
    try:
        existing = {row.phrase for row in db.query(MotivationalPhrases).all()}
        new_phrases = [p for p in PHRASES if p not in existing]

        if not new_phrases:
            print("All phrases already in the database.")
            return

        for phrase in new_phrases:
            db.add(MotivationalPhrases(phrase=phrase))
        db.commit()
        print(f"Inserted {len(new_phrases)} new phrases ({len(PHRASES) - len(new_phrases)} already existed).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
