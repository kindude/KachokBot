from datetime import date
from ..db import SessionLocal

from ..models import UserTable, PushUpsTable, DayTable


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