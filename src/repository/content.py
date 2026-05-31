from datetime import date, timedelta
from sqlite3 import IntegrityError
from sqlalchemy import func, or_
from ..db import SessionLocal
from ..models import AnecdotesTable, MotivationalPhrases


class ContentRepository:
    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def add_anecdote(self, anecdote: str) -> AnecdotesTable:
        record = AnecdotesTable(anecdote=anecdote)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_random_anecdote(self) -> AnecdotesTable | None:
        seven_days_ago = date.today() - timedelta(days=7)
        return (
            self.db.query(AnecdotesTable)
            .filter(or_(
                AnecdotesTable.last_sent == date(9999, 12, 31),
                AnecdotesTable.last_sent <= seven_days_ago,
            ))
            .order_by(func.random())
            .limit(1)
            .one_or_none()
        )

    def update_anecdote_date(self, anecdote_id: int, new_date: date) -> bool:
        try:
            self.db.query(AnecdotesTable)\
                .filter(AnecdotesTable.id == anecdote_id)\
                .update({"last_sent": new_date}, synchronize_session=False)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            return False

    def add_phrase(self, phrase: str) -> MotivationalPhrases:
        record = MotivationalPhrases(phrase=phrase)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_random_phrase(self) -> MotivationalPhrases | None:
        return (
            self.db.query(MotivationalPhrases)
            .order_by(func.random())
            .limit(1)
            .one_or_none()
        )

    def get_all_phrases(self) -> list[MotivationalPhrases]:
        return self.db.query(MotivationalPhrases).all()
