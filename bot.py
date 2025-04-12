import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from datetime import datetime

TOKEN = '8192070018:AAG8sfBcVd10RGjT7ApS4bc3SO28KI-ZI3s'
GROUP_ID = '-4743904412'

QUESTIONS = [
    "👤Как вас зовут?",
    "🎂Сколько вам лет?",
    "🎮 Ваш NickName в Roblox (пример: @melancholiaYT)?",
    "📊Какой у Вас ранг в Pet Simulator 99?",
    "🔄Сколько у Вас перерождений в Pet Simulator 99?",
    "🥚Сколько Вы можете открывать яиц за раз?",
    "🐶Сколько Вы можете одевать питомцев одновременно?",
    "🐾Сколько у Вас Huge/Titanic питомцев?",
    "⏳Сколько времени Вы проводите в игре? (с учетом AFK)"
]

# Индексы вопросов, где ответ должен быть числом
NUMERIC_QUESTIONS = {1, 3, 4, 5, 6, 7}

user_answers = {}
user_states = {}
user_last_submission = {}  # Словарь для отслеживания последней заявки

async def start(update: Update, context: CallbackContext):
    buttons = [
        ["💎Владельцы клана [UTKI]"],
        ["✔️Заявление на вступление в клан"],
        ["💜Информация об клане"]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("Добро пожаловать в Помощника-Информатора клана UTKI!\n🔧Полезное послание от разработчика:\n❗Если ты случайно начал заполнять '✔️Заявление на вступление в клан' напиши /cancel и заполнение отменится!💖", reply_markup=reply_markup)

async def handle_menu_selection(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.effective_chat.id

    if text == "✔️Заявление на вступление в клан":
        # Проверяем, не отправлял ли пользователь заявку сегодня
        if user_id in user_last_submission:
            last_submission_date = user_last_submission[user_id]
            if last_submission_date == datetime.today().date():
                await context.bot.send_message(user_id, "❌ Вы уже отправили заявку сегодня. Попробуйте снова завтра.")
                return

        user_answers[user_id] = []
        user_states[user_id] = True
        await context.bot.send_message(user_id, QUESTIONS[0])
    elif text == "💎Владельцы клана [UTKI]":
        await context.bot.send_message(user_id, "👑 Владельцы клана UTKI:\n• @melancholiaYT (Создатель)\n• @Hildeyps (Помощник создателя клана)\n• @tt8teen (Бывший создатель, внёс огромный вклад в развитие клана)")
    elif text == "💜Информация об клане":
        await context.bot.send_message(user_id, "ℹ️ Информация и клане [UTKI]\n• Количество участников: 5/75\n• Уровень клана: 6 уровень\n• Цели:\n🦆Заполнить клан активными участниками\n🦆Попасть в топ 100 клановой битвы")
    else:
        await collect_answers(update, context)

async def collect_answers(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    message = update.message.text.strip()

    if user_states.get(user_id, False):
        current_index = len(user_answers[user_id])

        # Проверка: если вопрос требует цифру, а пользователь ввёл не число
        if current_index in NUMERIC_QUESTIONS and not message.isdigit():
            await context.bot.send_message(user_id, "Пожалуйста, введите только число.")
            return

        user_answers[user_id].append(message)

        if len(user_answers[user_id]) < len(QUESTIONS):
            next_question = QUESTIONS[len(user_answers[user_id])]
            await context.bot.send_message(user_id, next_question)
        else:
            await send_answers_to_group(update, context, user_id)
            user_states[user_id] = False
            # Записываем текущую дату в словарь, чтобы ограничить заявку одним разом в день
            user_last_submission[user_id] = datetime.today().date()
    else:
        await update.message.reply_text("Нажмите '✔️Заявление на вступление в клан', чтобы начать анкету.")

async def send_answers_to_group(update: Update, context: CallbackContext, user_id):
    user = update.effective_user
    username = f"@{user.username}" if user.username else f"Пользователь {user.first_name}"
    answers = user_answers.pop(user_id, [])

    if answers:
        text = f"📩 Ответы от {username}:\n\n" + "\n".join(
            [f"{QUESTIONS[i]} {answers[i]}" for i in range(len(answers))]
        )
        await context.bot.send_message(GROUP_ID, text)
        await context.bot.send_message(user_id, "✅ Спасибо! Ваше заявление на рассмотрении администрацией клана.")

# Добавление команды /cancel
async def cancel(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id

    if user_states.get(user_id, False):
        user_answers.pop(user_id, None)  # Удаляем ответы пользователя
        user_states[user_id] = False  # Завершаем анкету
        await context.bot.send_message(user_id, "❌ Вы отменили заполнение анкеты.")
    else:
        await update.message.reply_text("Вы не находитесь в процессе заполнения анкеты.")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))  # Добавляем обработчик для команды /cancel
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_selection))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
