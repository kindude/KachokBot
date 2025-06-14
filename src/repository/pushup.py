import random
from datetime import date, timedelta
from sqlite3 import IntegrityError

from ..db import SessionLocal
from sqlalchemy import func, or_
from ..models import UserTable, PushUpsTable, DayTable, AnecdotesTable, ArticlesSent
from sqlalchemy import func, desc, and_
from datetime import date

class DatabaseRepository:
    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def add_user(self, nickname: str):
        user = UserTable(nickname=nickname)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_id(self, user_id: int):
        return self.db.query(UserTable).filter(UserTable.id == user_id).first()

    def get_user_by_nickname(self, nickname: str):
        return self.db.query(UserTable).filter(UserTable.nickname == nickname).first()

    def get_random_anecdote(self):
        seven_days_ago = date.today() - timedelta(days=7)
        return (
            self.db.query(AnecdotesTable)
            .filter(or_(
                AnecdotesTable.last_sent == date(9999, 12, 31),
                AnecdotesTable.last_sent <= seven_days_ago
            ))
            .order_by(func.random())
            .limit(1)
            .one_or_none()
        )

    def get_users_w_scores(self, yesterday):
        data = (
            self.db.query(UserTable, PushUpsTable)
            .join(PushUpsTable, UserTable.id == PushUpsTable.user_id)
            .join(DayTable, DayTable.id == PushUpsTable.day_id)
            .filter(DayTable.date == yesterday)
            .order_by(desc(PushUpsTable.pushups_done))
            .all()
        )
        return data

    def add_day(self, day: date) -> DayTable:
        day_record = self.db.query(DayTable).filter(DayTable.date == day).first()
        if not day_record:
            day_record = DayTable(date=day)
            self.db.add(day_record)
            self.db.commit()
            self.db.refresh(day_record)
        return day_record

    def record_pushups(self, user_id: int, day: date, pushups_done: int):
        day_record = self.add_day(day)

        pushup_entry = self.db.query(PushUpsTable).filter_by(
            user_id=user_id,
            day_id=day_record.id
        ).first()

        if pushup_entry:
            pushup_entry.pushups_done += pushups_done
            self.db.commit()
            self.db.refresh(pushup_entry)
            return pushup_entry
        else:
            new_entry = PushUpsTable(
                user_id=user_id,
                day_id=day_record.id,
                pushups_done=pushups_done
            )
            self.db.add(new_entry)
            self.db.commit()
            self.db.refresh(new_entry)
            return new_entry

    def record_anecdote(self, anecdote: str):
        new_anecdote = AnecdotesTable(anecdote=anecdote)
        self.db.add(new_anecdote)
        self.db.commit()
        self.db.refresh(new_anecdote)
        return new_anecdote

    def get_all_pushups(self):
        return self.db.query(PushUpsTable).all()

    def get_pushups_for_user(self, user_id: int):
        return self.db.query(PushUpsTable).filter_by(user_id=user_id).all()

    def get_all_users(self):
        return self.db.query(UserTable).all()

    def get_pushups_for_user_on_day(self, user_id: int, day: date):
        day_record = self.db.query(DayTable).filter(DayTable.date == day).first()
        if not day_record:
            return []
        return self.db.query(PushUpsTable).filter_by(user_id=user_id, day_id=day_record.id).all()

    def get_article_by_url(self, url: str) -> ArticlesSent | None:
        return self.db.query(ArticlesSent).filter_by(url=url).first()

    def save_article(self, title: str, url: str) -> bool:
        try:
            article = ArticlesSent(title=title, url=url)
            self.db.add(article)
            self.db.commit()
            self.db.refresh(article)
            return True
        except IntegrityError:
            self.db.rollback()
            return False

    def update_anecdote(self, id: int, new_date):
        try:
            self.db.query(AnecdotesTable) \
                .filter(AnecdotesTable.id == id) \
                .update({"last_sent": new_date}, synchronize_session=False)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            return False
