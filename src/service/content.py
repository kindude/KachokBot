from datetime import date
from .llm import PhraseGenerator
from ..repository.content import ContentRepository
from ..repository.users import UserRepository

_ADMIN_NICKNAME = "Guest_0"


class ContentService:
    def __init__(self):
        self._content = ContentRepository()
        self._users = UserRepository()

    def close(self):
        self._content.close()
        self._users.close()

    def record_anecdote(self, nickname: str, anecdote: str) -> str:
        user = self._users.get_user_by_nickname(nickname)
        if not user or user.nickname != _ADMIN_NICKNAME:
            return "Ты не Марк!"
        self._content.add_anecdote(anecdote)
        return "Анекдот записан, мастер"

    def get_random_anecdote(self) -> str | None:
        anecdote = self._content.get_random_anecdote()
        if not anecdote:
            return None
        self._content.update_anecdote_date(anecdote.id, date.today())
        return anecdote.anecdote

    def record_phrase(self, phrase: str) -> str:
        self._content.add_phrase(phrase)
        return "Записал"

    def get_random_phrase(self) -> str | None:
        phrase = self._content.get_random_phrase()
        return phrase.phrase if phrase else None

    def get_motivational_phrase(self, exercise_context: str) -> str | None:
        """Try LLM first, fall back to a saved phrase from the DB."""
        phrase = PhraseGenerator().generate(exercise_context)
        return phrase or self.get_random_phrase()
