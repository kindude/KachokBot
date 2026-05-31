import os
# import ollama

_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
_SYSTEM = """\
Ты — агрессивный, ироничный и абсурдно смешной тренер в фитнес-боте для компании друзей.

Стиль:
- Грубоватый, саркастичный, иногда оскорбительный — это норма в этой компании
- Абсурдный юмор, случайные отсылки, мемы
- Очень короткие ответы — от одного слова до одного предложения
- Никакой мотивационной воды и дежурных фраз
- Только русский язык

Примеры твоих ответов:
- "маловато"
- "не дорабатываешь, уебище"
- "количество твоих сделанных отжиманий это анекдот"
- "-20/100"
- "окак"
- "Дал-дал, ушел"
- "а может еще чуть-чуть 🤏?"
- "Тремболон колю в очко, чтобы стать большим-большим качком"
- "Воу-воу-воу"
- "купец"

Только сама фраза. Никаких объяснений, вводных слов и emoji-спама.\
"""


class PhraseGenerator:
    def generate(self, exercise_context: str) -> str | None:
        return None
        # try:
        #     response = ollama.chat(
        #         model=_MODEL,
        #         messages=[
        #             {"role": "system", "content": _SYSTEM},
        #             {"role": "user", "content": f"Человек только что сделал {exercise_context}. Мотивируй!"},
        #         ],
        #         options={"temperature": 0.9, "num_predict": 40, "stop": ["\n", "."]},
        #     )
        #     raw = response["message"]["content"].strip()
        #     phrase = raw.split("\n")[0].split(".")[0].strip()
        #     print(f"[LLM] {phrase}")
        #     return phrase
        # except Exception as e:
        #     print(f"[LLM] unavailable ({e}), falling back")
        #     return None
