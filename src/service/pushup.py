from datetime import date
from src.repository.pushup import DatabaseRepository
from datetime import date, datetime

class DatabaseService:
    def __init__(self):
        self.repo = DatabaseRepository()

    def close(self):
        self.repo.close()

    def record_pushups(self, nickname: str, pushups_done: int):
        user = self.repo.get_user_by_nickname(nickname)
        if not user:
            user = self.repo.add_user(nickname=nickname)

        result = self.repo.record_pushups(
            user_id=user.id,
            day=date.today(),
            pushups_done=pushups_done
        )
        return result

    def record_anecdote(self, nickname: str, anecdote: str):
        user = self.repo.get_user_by_nickname(nickname)
        if not user:
            return
        if user.nickname == "Guest_0":
            self.repo.record_anecdote(anecdote)
        else:
            return "Ты не Марк!"
        return "Анекдот записан, мастер"

    def get_random_anecdote(self):
        anecdote = self.repo.get_random_anecdote()
        if anecdote:
            return anecdote.anecdote



    def get_user_summary(self, nickname: str) -> dict:
        user = self.repo.get_user_by_nickname(nickname)
        if not user:
            return {
                "nickname": nickname,
                "total_pushups": 0,
                "days_trained": 0,
                "average_per_day": 0,
                "max_pushups_in_a_day": 0,
                "motivation": "",
                "today_pushups": 0,
                "monthly_percentage": 0
            }

        all_pushups = self.repo.get_pushups_for_user(user.id)
        if not all_pushups:
            return {
                "nickname": nickname,
                "total_pushups": 0,
                "days_trained": 0,
                "average_per_day": 0,
                "max_pushups_in_a_day": 0,
                "motivation": "",
                "today_pushups": 0,
                "monthly_percentage": 0
            }

        total_pushups = sum(p.pushups_done for p in all_pushups)
        unique_days = {p.day_id for p in all_pushups}
        days_trained = len(unique_days)
        average_per_day = total_pushups // days_trained
        max_pushups = max(p.pushups_done for p in all_pushups)

        today = date.today()
        today_pushups = sum(
            p.pushups_done for p in self.repo.get_pushups_for_user_on_day(user.id, today)
        )
        motivation = "Продолжай в том же духе!" if today_pushups > 0 else "Сегодня еще не качался!"

        return {
            "nickname": nickname,
            "total_pushups": total_pushups,
            "days_trained": days_trained,
            "average_per_day": average_per_day,
            "max_pushups_in_a_day": max_pushups,
            "motivation": motivation,
            "today_pushups": today_pushups,
            "monthly_percentage": round((total_pushups / (30 * 100)) * 100, 2)
        }

