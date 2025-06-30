from calendar import monthrange
from datetime import date, timedelta
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

    def record_abs(self, nickname: str, abs_done: int):
        user = self.repo.get_user_by_nickname(nickname)
        if not user:
            user = self.repo.add_user(nickname=nickname)

        result = self.repo.record_abs(
            user_id=user.id,
            day=date.today(),
            abs_done=abs_done
        )
        return result

    def record_phrase(self, phrase: str):
        try:
            result = self.repo.add_phrase(phrase=phrase)
            if not result:
                return None
            return "Записал"
        except:
            return None

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
        if not anecdote:
            return None
        today = date.today()
        anecdote.last_sent = today
        self.repo.update_anecdote(id=anecdote.id, new_date=today)
        return anecdote.anecdote

    def get_random_motivational_phrase(self):
        phrase = self.repo.get_random_phrase()
        if not phrase:
            return None
        return phrase.phrase

    def extract_scores(self):
        today = date.today()

        # Top pushups
        users_pushups = self.repo.get_users_w_scores(today)
        leaderboard = f"🏆 Топ за {today.strftime('%d.%m.%Y')} по отжиманиям\n\n"
        for idx, (user, pushup) in enumerate(users_pushups, start=1):
            leaderboard += f"{idx}. {user.nickname} – {pushup.pushups_done} отжиманий\n"

        # Top abs (if available)
        users_abs = self.repo.get_users_w_abs(today)
        if users_abs:
            leaderboard += f"\n🧱 Топ по прессу\n\n"
            for idx, (user, abs_record) in enumerate(users_abs, start=1):
                leaderboard += f"{idx}. {user.nickname} – {abs_record.abs_done} упражнений на пресс\n"

        return leaderboard


    def get_days_in_current_month(self) -> int:
        today = date.today()
        return monthrange(today.year, today.month)[1]

    def get_user_summary(self, nickname: str) -> dict:
        user = self.repo.get_user_by_nickname(nickname)
        if not user:
            return {
                "nickname": nickname,
                "total_pushups": 0,
                "total_abs": 0,
                "days_trained": 0,
                "average_per_day": 0,
                "max_pushups_in_a_day": 0,
                "motivation": "",
                "today_pushups": 0,
                "today_abs": 0,
                "monthly_percentage_pushups": 0,
                "monthly_percentage_abs": 0,
            }

        all_pushups = self.repo.get_pushups_for_user(user.id)
        all_abs = self.repo.get_abs_for_user(user.id)

        total_pushups = sum(p.pushups_done or 0 for p in all_pushups)
        total_abs = sum(a.abs_done or 0 for a in all_abs)

        pushup_days = {p.day_id for p in all_pushups}
        abs_days = {a.day_id for a in all_abs}
        all_days = pushup_days.union(abs_days)
        days_trained = len(all_days)

        average_per_day = (total_pushups // days_trained) if days_trained > 0 else 0
        max_pushups = max((p.pushups_done or 0 for p in all_pushups), default=0)

        today = date.today()
        today_pushups = sum(p.pushups_done or 0 for p in self.repo.get_pushups_for_user_on_day(user.id, today))
        today_abs = sum(a.abs_done or 0 for a in self.repo.get_abs_for_user_on_day(user.id, today))

        motivation = "Продолжай в том же духе!" if today_pushups > 0 or today_abs > 0 else "Сегодня еще не качался!"

        # Monthly progress calculation
        current_year = today.year
        current_month = today.month
        days_in_month = self.get_days_in_current_month()
        monthly_pushups = sum(
            p.pushups_done or 0
            for p in all_pushups
            if p.day and p.day.date.month == current_month and p.day.date.year == current_year
        )

        monthly_abs = sum(
            a.abs_done or 0
            for a in all_abs
            if a.day and a.day.date.month == current_month and a.day.date.year == current_year
        )

        daily_goal = 100
        max_pushups_this_month = days_in_month * daily_goal
        max_abs_this_month = days_in_month * daily_goal

        monthly_percentage_pushups = round((monthly_pushups / max_pushups_this_month) * 100, 2)
        monthly_percentage_abs = round((monthly_abs / max_abs_this_month) * 100, 2)

        return {
            "nickname": nickname,
            "total_pushups": total_pushups,
            "total_abs": total_abs,
            "days_trained": days_trained,
            "average_per_day": average_per_day,
            "max_pushups_in_a_day": max_pushups,
            "motivation": motivation,
            "today_pushups": today_pushups,
            "today_abs": today_abs,
            "monthly_percentage_pushups": monthly_percentage_pushups,
            "monthly_percentage_abs": monthly_percentage_abs,
        }

    def find_article_if_exists_by_url(self, url: str) -> bool:
        return self.repo.get_article_by_url(url) is not None

    def save_article(self, title: str, url: str) -> bool:
        if self.find_article_if_exists_by_url(url):
            return False
        return self.repo.save_article(title, url)

    def all_phrases(self):

        phrases = self.repo.get_all_phrases()
        print(phrases)
        return phrases
