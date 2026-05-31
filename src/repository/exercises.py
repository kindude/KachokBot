from datetime import date
from sqlalchemy import desc
from ..db import SessionLocal
from ..models import UserTable, PushUpsTable, AbsTable, DayTable, PullUpsTable, PlankTable


class ExerciseRepository:
    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def get_or_create_day(self, day: date) -> DayTable:
        record = self.db.query(DayTable).filter(DayTable.date == day).first()
        if not record:
            record = DayTable(date=day)
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
        return record

    def record_pushups(self, user_id: int, day: date, pushups_done: int) -> PushUpsTable:
        day_record = self.get_or_create_day(day)
        entry = self.db.query(PushUpsTable).filter_by(user_id=user_id, day_id=day_record.id).first()
        if entry:
            entry.pushups_done += pushups_done
            self.db.commit()
            self.db.refresh(entry)
            return entry
        entry = PushUpsTable(user_id=user_id, day_id=day_record.id, pushups_done=pushups_done)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def record_abs(self, user_id: int, day: date, abs_done: int) -> AbsTable:
        day_record = self.get_or_create_day(day)
        entry = self.db.query(AbsTable).filter_by(user_id=user_id, day_id=day_record.id).first()
        if entry:
            entry.abs_done = (entry.abs_done or 0) + abs_done
            self.db.commit()
            self.db.refresh(entry)
            return entry
        entry = AbsTable(user_id=user_id, day_id=day_record.id, abs_done=abs_done)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def record_pullups(self, user_id: int, day: date, pullups_done: int) -> PullUpsTable:
        day_record = self.get_or_create_day(day)
        entry = self.db.query(PullUpsTable).filter_by(user_id=user_id, day_id=day_record.id).first()
        if entry:
            entry.pullups_done += pullups_done
            self.db.commit()
            self.db.refresh(entry)
            return entry
        entry = PullUpsTable(user_id=user_id, day_id=day_record.id, pullups_done=pullups_done)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def record_plank(self, user_id: int, day: date, duration_seconds: int) -> PlankTable:
        day_record = self.get_or_create_day(day)
        entry = self.db.query(PlankTable).filter_by(user_id=user_id, day_id=day_record.id).first()
        if entry:
            entry.duration_seconds += duration_seconds
            self.db.commit()
            self.db.refresh(entry)
            return entry
        entry = PlankTable(user_id=user_id, day_id=day_record.id, duration_seconds=duration_seconds)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_pushups_for_user(self, user_id: int) -> list[PushUpsTable]:
        return self.db.query(PushUpsTable).filter_by(user_id=user_id).all()

    def get_abs_for_user(self, user_id: int) -> list[AbsTable]:
        return self.db.query(AbsTable).filter_by(user_id=user_id).all()

    def get_pullups_for_user(self, user_id: int) -> list[PullUpsTable]:
        return self.db.query(PullUpsTable).filter_by(user_id=user_id).all()

    def get_plank_for_user(self, user_id: int) -> list[PlankTable]:
        return self.db.query(PlankTable).filter_by(user_id=user_id).all()

    def get_pushups_for_user_on_day(self, user_id: int, day: date) -> list[PushUpsTable]:
        day_record = self.db.query(DayTable).filter(DayTable.date == day).first()
        if not day_record:
            return []
        return self.db.query(PushUpsTable).filter_by(user_id=user_id, day_id=day_record.id).all()

    def get_abs_for_user_on_day(self, user_id: int, day: date) -> list[AbsTable]:
        day_record = self.db.query(DayTable).filter(DayTable.date == day).first()
        if not day_record:
            return []
        return self.db.query(AbsTable).filter_by(user_id=user_id, day_id=day_record.id).all()

    def get_pullups_for_user_on_day(self, user_id: int, day: date) -> list[PullUpsTable]:
        day_record = self.db.query(DayTable).filter(DayTable.date == day).first()
        if not day_record:
            return []
        return self.db.query(PullUpsTable).filter_by(user_id=user_id, day_id=day_record.id).all()

    def get_plank_for_user_on_day(self, user_id: int, day: date) -> list[PlankTable]:
        day_record = self.db.query(DayTable).filter(DayTable.date == day).first()
        if not day_record:
            return []
        return self.db.query(PlankTable).filter_by(user_id=user_id, day_id=day_record.id).all()

    def get_users_with_pushups_on_day(self, day: date) -> list[tuple[UserTable, PushUpsTable]]:
        return (
            self.db.query(UserTable, PushUpsTable)
            .join(PushUpsTable, UserTable.id == PushUpsTable.user_id)
            .join(DayTable, DayTable.id == PushUpsTable.day_id)
            .filter(DayTable.date == day)
            .order_by(desc(PushUpsTable.pushups_done))
            .all()
        )

    def get_users_with_abs_on_day(self, day: date) -> list[tuple[UserTable, AbsTable]]:
        return (
            self.db.query(UserTable, AbsTable)
            .join(AbsTable, UserTable.id == AbsTable.user_id)
            .join(DayTable, DayTable.id == AbsTable.day_id)
            .filter(DayTable.date == day)
            .order_by(desc(AbsTable.abs_done))
            .all()
        )

    def get_users_with_pullups_on_day(self, day: date) -> list[tuple[UserTable, PullUpsTable]]:
        return (
            self.db.query(UserTable, PullUpsTable)
            .join(PullUpsTable, UserTable.id == PullUpsTable.user_id)
            .join(DayTable, DayTable.id == PullUpsTable.day_id)
            .filter(DayTable.date == day)
            .order_by(desc(PullUpsTable.pullups_done))
            .all()
        )

    def get_users_with_plank_on_day(self, day: date) -> list[tuple[UserTable, PlankTable]]:
        return (
            self.db.query(UserTable, PlankTable)
            .join(PlankTable, UserTable.id == PlankTable.user_id)
            .join(DayTable, DayTable.id == PlankTable.day_id)
            .filter(DayTable.date == day)
            .order_by(desc(PlankTable.duration_seconds))
            .all()
        )
