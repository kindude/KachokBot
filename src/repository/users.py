from ..db import SessionLocal
from ..models import UserTable


class UserRepository:
    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def add_user(self, nickname: str) -> UserTable:
        user = UserTable(nickname=nickname)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_nickname(self, nickname: str) -> UserTable | None:
        return self.db.query(UserTable).filter(UserTable.nickname == nickname).first()

    def get_user_by_id(self, user_id: int) -> UserTable | None:
        return self.db.query(UserTable).filter(UserTable.id == user_id).first()

    def get_all_users(self) -> list[UserTable]:
        return self.db.query(UserTable).all()
