from datetime import date
from src.repository.pushup import DatabaseRepository


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

    def get_user_summary(self, nickname: str):
        user = self.repo.get_user_by_nickname(nickname)
        if not user:
            return f"No user found with nickname '{nickname}'"

        all_pushups = self.repo.get_pushups_for_user(user.id)
 
        if not all_pushups:
            return f"No workouts yet, {nickname}!"

        total = sum(entry.pushups_done for entry in all_pushups)
        days = len(all_pushups)
        avg = total / days
        max_pushups = max(entry.pushups_done for entry in all_pushups)

        feedback = (
            "Beast Mode!" if total > 60  else
            "Keep it up!" if total > 80  else
            "Just getting started!"
        )

        return {
            "nickname": nickname,
            "total_pushups": total,
            "days_trained": days,
            "average_per_day": round(avg, 1),
            "max_pushups_in_a_day": max_pushups,
            "motivation": feedback
        }

