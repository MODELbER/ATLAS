import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

# ================= ТОКЕН =================
BOT_TOKEN = "8829874034:AAE_1NGu9eNLuycB9oclC6eLOAfhziA3OPs"

# ================= ССЫЛКИ НА ГРУППЫ =================
GROUP_JUNIOR = "https://t.me/+jBwmXpmWJqYwNWNi"        # низшие разработчики
GROUP_MIDDLE = "https://t.me/+iYW99EYUzdk3MmM6"        # медиум Python
GROUP_CORE = "https://t.me/+-rHBe8fPJJpmY2Ri"          # высший класс
GROUP_JAVA = "https://t.me/+kPkPPKWBdto4OWNi"          # Java
GROUP_JS = "https://t.me/+dRqAqQ9pKYtmZTYy"            # JavaScript
GROUP_PROMO1 = "https://t.me/+KHzqbyHBnDJjZjRi"        # продвижение 1
GROUP_PROMO2 = "https://t.me/+-dymr3h0qC1kZDJi"        # продвижение 2

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

QUESTIONS = [
    {
        "text": "Привет! Я бот команды A.T.L.A.S.\n\n"
                "A.T.L.A.S — это голосовой помощник, как Алиса или Siri. "
                "Только он живёт на компьютере, работает без интернета, "
                "и его можно менять под себя.\n\n"
                "Ответь на пару вопросов, и я пойму, куда тебя направить.\n\n"
                "Ты программист?",
        "options": [
            ("Да, пишу код", 3),
            ("Нет, но хочу учиться", 2),
            ("Нет, я по другой части", 0),
        ],
    },
    {
        "text": "На каких языках пишешь? (выбери основной)",
        "options": [
            ("Python", 3),
            ("Java", 3),
            ("JavaScript", 3),
            ("Другой", 2),
            ("Не пишу код", 0),
        ],
    },
    {
        "text": "Какой у тебя уровень?",
        "options": [
            ("Пишу сложный код, архитектура", 5),
            ("Пишу средний код, модули", 3),
            ("Пишу промпты, тестирую", 2),
            ("Только учусь", 1),
            ("Не программист", 0),
        ],
    },
    {
        "text": "Что тебе интереснее всего?",
        "options": [
            ("Писать код", 3),
            ("Тестировать", 2),
            ("Продвигать проект", 1),
            ("Придумывать идеи", 2),
        ],
    },
    {
        "text": "Сколько времени в неделю готов уделять?",
        "options": [
            ("Больше 10 часов", 3),
            ("5-10 часов", 2),
            ("Пару часов", 1),
        ],
    },
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["current_q"] = 0
    context.user_data["score"] = 0
    context.user_data["lang"] = None
    await ask_question(update, context)


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q_index = context.user_data["current_q"]
    if q_index >= len(QUESTIONS):
        await finish_survey(update, context)
        return

    q = QUESTIONS[q_index]
    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"q{q_index}_{i}")]
        for i, (opt, _) in enumerate(q["options"])
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(q["text"], reply_markup=reply_markup)
    else:
        await update.message.reply_text(q["text"], reply_markup=reply_markup)


async def finish_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = context.user_data.get("score", 0)
    lang = context.user_data.get("lang", "Не пишу код")
    user_name = update.effective_user.full_name
    user_id = update.effective_user.id

    if score >= 14:
        group_name = "Ядро"
        link = GROUP_CORE
    elif score >= 8 and "Java" in lang:
        group_name = "Java-разработчик"
        link = GROUP_JAVA
    elif score >= 8 and "JavaScript" in lang:
        group_name = "JS-разработчик"
        link = GROUP_JS
    elif score >= 8:
        group_name = "Python-разработчик"
        link = GROUP_MIDDLE
    elif score >= 5:
        group_name = "Низший разработчик"
        link = GROUP_JUNIOR
    else:
        group_name = "Новичок"
        link = GROUP_PROMO1 if user_id % 2 == 0 else GROUP_PROMO2

    text = (
        f"Спасибо, {user_name}!\n\n"
        f"Твой результат: {score} баллов.\n"
        f"Ты — {group_name}.\n\n"
        f"Вступай в свою группу: {link}\n\n"
        f"Ты получишь уникальный код одного из первых участников. "
        f"Когда проект будет готов — у тебя будут особые условия."
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")

    logging.info(f"{user_name} ({user_id}) → {group_name}")


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    q_index = int(data.split("_")[0][1:])
    opt_index = int(data.split("_")[1])

    option_text, points = QUESTIONS[q_index]["options"][opt_index]
    context.user_data["score"] += points

    if q_index == 1:
        context.user_data["lang"] = option_text

    context.user_data["current_q"] += 1
    await ask_question(update, context)


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CallbackQueryHandler(handle_answer))
    print("Бот запущен.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
