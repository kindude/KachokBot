from calendar import monthrange
from datetime import date
from ..repository.exercises import ExerciseRepository
from ..repository.users import UserRepository

_DAILY_GOAL = 100


def format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "0сек"
    m, s = divmod(seconds, 60)
    if m == 0:
        return f"{s}сек"
    return f"{m}мин {s:02d}сек" if s else f"{m}мин"


class ExerciseService:
    def __init__(self):
        self._exercises = ExerciseRepository()
        self._users = UserRepository()

    def close(self):
        self._exercises.close()
        self._users.close()

    def _get_or_create_user(self, nickname: str):
        user = self._users.get_user_by_nickname(nickname)
        if not user:
            user = self._users.add_user(nickname)
        return user

    def record_pushups(self, nickname: str, pushups_done: int):
        user = self._get_or_create_user(nickname)
        return self._exercises.record_pushups(user_id=user.id, day=date.today(), pushups_done=pushups_done)

    def record_abs(self, nickname: str, abs_done: int):
        user = self._get_or_create_user(nickname)
        return self._exercises.record_abs(user_id=user.id, day=date.today(), abs_done=abs_done)

    def record_pullups(self, nickname: str, pullups_done: int):
        user = self._get_or_create_user(nickname)
        return self._exercises.record_pullups(user_id=user.id, day=date.today(), pullups_done=pullups_done)

    def record_plank(self, nickname: str, duration_seconds: int):
        user = self._get_or_create_user(nickname)
        return self._exercises.record_plank(user_id=user.id, day=date.today(), duration_seconds=duration_seconds)

    def build_leaderboard(self) -> str:
        today = date.today()
        lines = [f"🏆 Топ за {today.strftime('%d.%m.%Y')}\n"]

        pushups = self._exercises.get_users_with_pushups_on_day(today)
        if pushups:
            lines.append("💪 Отжимания")
            for idx, (user, rec) in enumerate(pushups, 1):
                lines.append(f"  {idx}. {user.nickname} — {rec.pushups_done}")

        abs_records = self._exercises.get_users_with_abs_on_day(today)
        if abs_records:
            lines.append("\n🧱 Пресс")
            for idx, (user, rec) in enumerate(abs_records, 1):
                lines.append(f"  {idx}. {user.nickname} — {rec.abs_done}")

        pullups = self._exercises.get_users_with_pullups_on_day(today)
        if pullups:
            lines.append("\n🏋️ Подтягивания")
            for idx, (user, rec) in enumerate(pullups, 1):
                lines.append(f"  {idx}. {user.nickname} — {rec.pullups_done}")

        plank = self._exercises.get_users_with_plank_on_day(today)
        if plank:
            lines.append("\n⏱ Планка")
            for idx, (user, rec) in enumerate(plank, 1):
                lines.append(f"  {idx}. {user.nickname} — {format_duration(rec.duration_seconds)}")

        return "\n".join(lines)

    def get_user_summary(self, nickname: str) -> dict:
        user = self._users.get_user_by_nickname(nickname)
        if not user:
            return self._empty_summary(nickname)

        all_pushups = self._exercises.get_pushups_for_user(user.id)
        all_abs = self._exercises.get_abs_for_user(user.id)
        all_pullups = self._exercises.get_pullups_for_user(user.id)
        all_plank = self._exercises.get_plank_for_user(user.id)

        total_pushups = sum(p.pushups_done or 0 for p in all_pushups)
        total_abs = sum(a.abs_done or 0 for a in all_abs)
        total_pullups = sum(p.pullups_done or 0 for p in all_pullups)
        total_plank_seconds = sum(p.duration_seconds or 0 for p in all_plank)

        days_trained = len(
            {p.day_id for p in all_pushups}
            | {a.day_id for a in all_abs}
            | {p.day_id for p in all_pullups}
            | {p.day_id for p in all_plank}
        )
        average_per_day = total_pushups // days_trained if days_trained else 0
        average_abs_per_day = total_abs // days_trained if days_trained else 0
        average_pullups_per_day = total_pullups // days_trained if days_trained else 0
        max_pushups = max((p.pushups_done or 0 for p in all_pushups), default=0)
        max_abs = max((a.abs_done or 0 for a in all_abs), default=0)
        max_pullups = max((p.pullups_done or 0 for p in all_pullups), default=0)
        max_plank_seconds = max((p.duration_seconds or 0 for p in all_plank), default=0)

        today = date.today()
        today_pushups = sum(
            p.pushups_done or 0
            for p in self._exercises.get_pushups_for_user_on_day(user.id, today)
        )
        today_abs = sum(
            a.abs_done or 0
            for a in self._exercises.get_abs_for_user_on_day(user.id, today)
        )
        today_pullups = sum(
            p.pullups_done or 0
            for p in self._exercises.get_pullups_for_user_on_day(user.id, today)
        )
        today_plank_seconds = sum(
            p.duration_seconds or 0
            for p in self._exercises.get_plank_for_user_on_day(user.id, today)
        )

        active_today = any([today_pushups, today_abs, today_pullups, today_plank_seconds])
        motivation = "Продолжай в том же духе!" if active_today else "Сегодня еще не качался!"

        year, month = today.year, today.month
        days_in_month = monthrange(year, month)[1]
        monthly_pushups = sum(
            p.pushups_done or 0 for p in all_pushups
            if p.day and p.day.date.month == month and p.day.date.year == year
        )
        monthly_abs = sum(
            a.abs_done or 0 for a in all_abs
            if a.day and a.day.date.month == month and a.day.date.year == year
        )
        monthly_pullups = sum(
            p.pullups_done or 0 for p in all_pullups
            if p.day and p.day.date.month == month and p.day.date.year == year
        )

        goal_total = days_in_month * _DAILY_GOAL
        return {
            "nickname": nickname,
            "total_pushups": total_pushups,
            "total_abs": total_abs,
            "total_pullups": total_pullups,
            "total_plank": format_duration(total_plank_seconds),
            "days_trained": days_trained,
            "average_per_day": average_per_day,
            "average_abs_per_day": average_abs_per_day,
            "average_pullups_per_day": average_pullups_per_day,
            "max_pushups_in_a_day": max_pushups,
            "max_abs_in_a_day": max_abs,
            "max_pullups_in_a_day": max_pullups,
            "max_plank": format_duration(max_plank_seconds),
            "motivation": motivation,
            "today_pushups": today_pushups,
            "today_abs": today_abs,
            "today_pullups": today_pullups,
            "today_plank": format_duration(today_plank_seconds),
            "today_plank_seconds": today_plank_seconds,
            "monthly_percentage_pushups": round(monthly_pushups / goal_total * 100, 2),
            "monthly_percentage_abs": round(monthly_abs / goal_total * 100, 2),
            "monthly_percentage_pullups": round(monthly_pullups / goal_total * 100, 2),
        }

    @staticmethod
    def _empty_summary(nickname: str) -> dict:
        return {
            "nickname": nickname,
            "total_pushups": 0,
            "total_abs": 0,
            "total_pullups": 0,
            "total_plank": "0сек",
            "days_trained": 0,
            "average_per_day": 0,
            "average_abs_per_day": 0,
            "average_pullups_per_day": 0,
            "max_pushups_in_a_day": 0,
            "max_abs_in_a_day": 0,
            "max_pullups_in_a_day": 0,
            "max_plank": "0сек",
            "motivation": "",
            "today_pushups": 0,
            "today_abs": 0,
            "today_pullups": 0,
            "today_plank": "0сек",
            "today_plank_seconds": 0,
            "monthly_percentage_pushups": 0,
            "monthly_percentage_abs": 0,
            "monthly_percentage_pullups": 0,
        }
