from telegram import Update


def get_nickname(update: Update) -> str:
    user = update.effective_user
    return user.username or f"{user.first_name}_{user.id}"
