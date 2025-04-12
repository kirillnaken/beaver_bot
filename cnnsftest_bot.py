import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '7293327941:AAE3gElHwSbbtvhaJbiDzcQvr-N_GO3gRFY'
CHAT_ID = '-1002624398086'

NICKNAME, POSITION, QUERY = range(3)

main_keyboard = ReplyKeyboardMarkup([
    ['Владелец центра редакции 🤝', 'Заведующий центра редакции✔️'],
    ['Состав заместителей 🚚', 'Ценовая политика должностей 💰', 'Заявления на пост заместителя🤵‍♂️'],
    ['Вопросы/жалобы/предложения', 'Бронирование должности']
], resize_keyboard=True)

cancel_button = KeyboardButton("Отменить")
cancel_keyboard = ReplyKeyboardMarkup([[cancel_button]], resize_keyboard=True)

def connect_db():
    return sqlite3.connect('forms.db')

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT,
            question TEXT,
            position TEXT
        )
    ''')
    conn.commit()
    conn.close()

async def start(update: Update, context: CallbackContext) -> None:
    if str(update.message.chat_id) == CHAT_ID:
        return

    await update.message.reply_text('Выбери кнопку, которая тебя интересует', reply_markup=main_keyboard)

async def button_handler(update: Update, context: CallbackContext) -> None:
    if str(update.message.chat_id) == CHAT_ID:
        return

    user_choice = update.message.text
    if user_choice == 'Вопросы/жалобы/предложения':
        await start_query(update, context)
        return QUERY
    elif user_choice == 'Бронирование должности':
        await start_booking(update, context)
        return NICKNAME
    elif user_choice == "Отменить":
        await update.message.reply_text("Процесс отменен.", reply_markup=main_keyboard)
        context.user_data.clear()
        return ConversationHandler.END
    else:
        response = {
            'Владелец центра редакции 🤝': 'John_Moon - @attwood30',
            'Заведующий центра редакции✔️': 'Kaya_Murphy - @bbtatti',
            'Состав заместителей 🚚': 'Amsterdam_Forever - @sssk2226 \nDanill_Lester - @bebramanm \nJuggernaut_Kushida - @Dgust1n',
            'Ценовая политика должностей 💰': '6 ранг - 5О.ООО.ООО$/месяц \n 7 ранг - 7О.ООО.ООО$/месяц \n 8 ранг - I2O.OOO.OOO$/месяц',
            'Заявления на пост заместителя🤵‍♂️': 'Для подачи заявлние на пост заместителя - обращайтесь к Заведующему центра редакции - @bbtatti'
        }.get(user_choice)
        if response:
            await update.message.reply_text(response)
        else:
            await update.message.reply_text('Неверный выбор, попробуйте ещё раз.', reply_markup=main_keyboard)
        return ConversationHandler.END

async def start_booking(update: Update, context: CallbackContext) -> int:
    if str(update.message.chat_id) == CHAT_ID:
        return

    await update.message.reply_text('Введите свой Никнейм:', reply_markup=cancel_keyboard)
    return NICKNAME

async def nickname_handler(update: Update, context: CallbackContext) -> int:
    if str(update.message.chat_id) == CHAT_ID:
        return

    if update.message.text == "Отменить":
        await update.message.reply_text("Процесс отменен.", reply_markup=main_keyboard)
        context.user_data.clear()
        return ConversationHandler.END

    context.user_data['nickname'] = update.message.text
    await update.message.reply_text('Укажите должность (6, 7 или 8):', reply_markup=cancel_keyboard)
    return POSITION

async def position_handler(update: Update, context: CallbackContext) -> int:
    if str(update.message.chat_id) == CHAT_ID:
        return

    if update.message.text == "Отменить":
        await update.message.reply_text("Процесс отменен.", reply_markup=main_keyboard)
        context.user_data.clear()
        return ConversationHandler.END

    position = update.message.text.strip()
    if position in ['6', '7', '8']:
        context.user_data['position'] = position
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO submissions (nickname, position) VALUES (?, ?)',
                       (context.user_data['nickname'], position))
        conn.commit()
        conn.close()

        username = update.message.from_user.username if update.message.from_user.username else "Неизвестно"
        
        await context.bot.send_message(
            CHAT_ID, 
            f'Новое бронирование: {context.user_data["nickname"]}, Должность: {position}\nЮзернейм: @{username}'
        )

        await update.message.reply_text('Бронирование успешно завершено!', reply_markup=main_keyboard)
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text('Некорректная должность. Выберите 6, 7 или 8.', reply_markup=cancel_keyboard)
        return POSITION

async def start_query(update: Update, context: CallbackContext) -> int:
    if str(update.message.chat_id) == CHAT_ID:
        return

    await update.message.reply_text('Введите свой Никнейм и вопрос через запятую (например: Никнейм, Ваш вопрос):', reply_markup=cancel_keyboard)
    return QUERY

async def query_handler(update: Update, context: CallbackContext) -> int:
    if str(update.message.chat_id) == CHAT_ID:
        return

    if update.message.text == "Отменить":
        await update.message.reply_text("Процесс отменен.", reply_markup=main_keyboard)
        context.user_data.clear()
        return ConversationHandler.END

    try:
        nickname, question = map(str.strip, update.message.text.split(',', 1))
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO submissions (nickname, question) VALUES (?, ?)', (nickname, question))
        conn.commit()
        conn.close()

        username = update.message.from_user.username if update.message.from_user.username else "Неизвестно"
        
        await context.bot.send_message(
            CHAT_ID, 
            f'Новый вопрос: {nickname}, Вопрос: {question}\nЮзернейм: @{username}'
        )

        await update.message.reply_text(f'Ваш вопрос принят! Никнейм: {nickname}, Вопрос: {question}', reply_markup=main_keyboard)
        context.user_data.clear()
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text('Некорректный формат. Попробуйте ещё раз.')
        return QUERY

def main() -> None:
    create_table()
    application = Application.builder().token(TOKEN).build()

    conv_handler_booking = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Бронирование должности$'), start_booking)],
        states={
            NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, nickname_handler)],
            POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, position_handler)]
        },
        fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler)]
    )

    conv_handler_query = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Вопросы/жалобы/предложения$'), start_query)],
        states={
            QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, query_handler)]
        },
        fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler)]
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler_booking)
    application.add_handler(conv_handler_query)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    application.run_polling()

if __name__ == '__main__':
    main()
