import logging
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update,
                      InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler, filters)
from config import TOKEN, USER_ID

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define states
LANGUAGE, USER_NAME, BIRTH_DATE, DISTRICT, APARTMENT_TYPE, FLOOR_OR_FLOORS, APARTMENT_CONDITION, ROOMS, PRICE, CONTACT = range(10)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for the preferred language."""
    keyboard = [
        [InlineKeyboardButton('Azərbaycan dili', callback_data='az')],
        [InlineKeyboardButton('Русский', callback_data='ru')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите язык / Dil seçin:', reply_markup=reply_markup)
    return LANGUAGE


async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected language and asks for the client's name."""
    query = update.callback_query
    await query.answer()
    language = query.data
    context.user_data['language'] = language

    if language == 'ru':
        await query.edit_message_text('<b>Здравствуйте! Мы поможем вам с продажей вашей недвижимости.\n'
                                      'Пожалуйста, начнем с вашего имени.</b>', parse_mode='HTML')
    else:
        await query.edit_message_text('<b>Salam! Biz sizə əmlakınızı satmaqda kömək edəcəyik.\n'
                                      'Xahiş edirik adınızı qeyd edin.</b>', parse_mode='HTML')
    return USER_NAME


async def user_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the client's name and asks for their full birth date."""
    context.user_data['user_name'] = update.message.text
    language = context.user_data['language']

    if language == 'ru':
        await update.message.reply_text('<b>Пожалуйста, укажите вашу полную дату рождения (например, 01.01.1990).</b>', parse_mode='HTML')
    else:
        await update.message.reply_text('<b>Zəhmət olmasa tam doğum tarixinizi qeyd edin (məsələn, 01.01.1990).</b>', parse_mode='HTML')
    return BIRTH_DATE


async def birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the birth date and asks for the district."""
    context.user_data['birth_date'] = update.message.text
    language = context.user_data['language']

    if language == 'ru':
        await update.message.reply_text('<b>Укажите район, где расположена квартира.</b>', parse_mode='HTML')
    else:
        await update.message.reply_text('<b>Mənzilin yerləşdiyi rayonu qeyd edin.</b>', parse_mode='HTML')
    return DISTRICT


async def district(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the district and asks whether the property is in a building or a private house."""
    context.user_data['district'] = update.message.text
    language = context.user_data['language']

    keyboard = [
        [InlineKeyboardButton('Квартира', callback_data='building')],
        [InlineKeyboardButton('Частный дом', callback_data='private')],
    ] if language == 'ru' else [
        [InlineKeyboardButton('Mənzil', callback_data='building')],
        [InlineKeyboardButton('Həyət evi', callback_data='private')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if language == 'ru':
        await update.message.reply_text('<b>Это квартира в здании или частный дом?</b>', parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text('<b>Bu mənzil binada yoxsa şəxsi evdir?</b>', parse_mode='HTML', reply_markup=reply_markup)
    return APARTMENT_TYPE


async def apartment_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the apartment type and asks the next question based on the type of property."""
    query = update.callback_query
    await query.answer()
    context.user_data['apartment_type'] = query.data
    language = context.user_data['language']

    if query.data == 'building':
        if language == 'ru':
            await query.edit_message_text('<b>На каком этаже находится квартира?</b>', parse_mode='HTML')
        else:
            await query.edit_message_text('<b>Mənzil hansı mərtəbədə yerləşir?</b>', parse_mode='HTML')
    else:
        if language == 'ru':
            await query.edit_message_text('<b>Сколько этажей в доме?</b>', parse_mode='HTML')
        else:
            await query.edit_message_text('<b>Evin neçə mərtəbəsi var?</b>', parse_mode='HTML')

    return FLOOR_OR_FLOORS


async def floor_or_floors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the number of floors or the floor the apartment is on, and asks for the apartment's condition."""
    context.user_data['floor_or_floors'] = update.message.text
    language = context.user_data['language']

    keyboard = [
        [InlineKeyboardButton('Новое', callback_data='Новое')],
        [InlineKeyboardButton('Хорошее', callback_data='Хорошее')],
        [InlineKeyboardButton('Среднее', callback_data='Среднее')],
        [InlineKeyboardButton('Требует ремонта', callback_data='Требует ремонта')],
    ] if language == 'ru' else [
        [InlineKeyboardButton('Yeni', callback_data='Yeni')],
        [InlineKeyboardButton('Yaxşı', callback_data='Yaxşı')],
        [InlineKeyboardButton('Orta', callback_data='Orta')],
        [InlineKeyboardButton('Təmiri lazımdır', callback_data='Təmiri lazımdır')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if language == 'ru':
        await update.message.reply_text('<b>Какое состояние квартиры?</b>', parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text('<b>Mənzilin vəziyyəti necədir?</b>', parse_mode='HTML', reply_markup=reply_markup)
    return APARTMENT_CONDITION


async def apartment_condition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the apartment's condition and asks for the number of rooms."""
    query = update.callback_query
    await query.answer()
    context.user_data['apartment_condition'] = query.data
    language = context.user_data['language']

    if language == 'ru':
        await query.edit_message_text('<b>Сколько комнат в квартире?</b>', parse_mode='HTML')
    else:
        await query.edit_message_text('<b>Mənzildə neçə otaq var?</b>', parse_mode='HTML')
    return ROOMS


async def rooms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the number of rooms and asks for the price."""
    context.user_data['rooms'] = update.message.text
    language = context.user_data['language']

    if language == 'ru':
        await update.message.reply_text('<b>Какую цену за квартиру вы предлагаете(в манатах)?</b>', parse_mode='HTML')
    else:
        await update.message.reply_text('<b>Mənzilin qiymətini neçə manat təklif edirsiniz?</b>', parse_mode='HTML')
    return PRICE


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the price and asks for the client's contact details."""
    context.user_data['price'] = update.message.text
    language = context.user_data['language']

    if language == 'ru':
        await update.message.reply_text('<b>Пожалуйста, укажите ваш ник в Telegram или номер телефона для связи.</b>', parse_mode='HTML')
    else:
        await update.message.reply_text('<b>Zəhmət olmasa Telegram istifadəçi adınızı və ya əlaqə nömrənizi qeyd edin.</b>', parse_mode='HTML')
    return CONTACT


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the contact details and summarizes the input."""
    context.user_data['contact'] = update.message.text
    user_data = context.user_data
    language = user_data['language']
    
    summary_text_ru = (
        f"<b>Сводка информации:</b>\n"
        f"<b>Имя:</b> {user_data['user_name']}\n"
        f"<b>Дата рождения:</b> {user_data['birth_date']}\n"
        f"<b>Район:</b> {user_data['district']}\n"
        f"<b>Тип жилья:</b> {'Здание' if user_data['apartment_type'] == 'building' else 'Частный дом'}\n"
        f"<b>{'Этаж квартиры' if user_data['apartment_type'] == 'building' else 'Этажей в доме'}:</b> {user_data['floor_or_floors']}\n"
        f"<b>Состояние квартиры:</b> {user_data['apartment_condition']}\n"
        f"<b>Количество комнат:</b> {user_data['rooms']}\n"
        f"<b>Цена:</b> {user_data['price']}\n"
        f"<b>Контакт:</b> {user_data['contact']}"
    )

    summary_text_az = (
        f"<b>Məlumat xülasəsi:</b>\n"
        f"<b>Ad:</b> {user_data['user_name']}\n"
        f"<b>Doğum tarixi:</b> {user_data['birth_date']}\n"
        f"<b>Rayon:</b> {user_data['district']}\n"
        f"<b>Evin növü:</b> {'Bina' if user_data['apartment_type'] == 'building' else 'Xüsusi ev'}\n"
        f"<b>{'Mənzilin mərtəbəsi' if user_data['apartment_type'] == 'building' else 'Evin mərtəbə sayı'}:</b> {user_data['floor_or_floors']}\n"
        f"<b>Mənzilin vəziyyəti:</b> {user_data['apartment_condition']}\n"
        f"<b>Otaq sayı:</b> {user_data['rooms']}\n"
        f"<b>Qiymət:</b> {user_data['price']}\n"
        f"<b>Əlaqə:</b> {user_data['contact']}"
    )
    
    summary_text = summary_text_ru if language == 'ru' else summary_text_az
    await update.message.reply_text(summary_text, parse_mode='HTML')
    await context.bot.send_message(chat_id=USER_ID, text=summary_text, parse_mode='HTML')
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    language = context.user_data.get('language', 'ru')  # Default to Russian if language not set
    cancel_text = 'Процесс отменен. Если у вас будут вопросы, не стесняйтесь писать.' if language == 'ru' else 'Proses ləğv olundu. Suallarınız varsa, çəkinmədən yaza bilərsiniz.'
    await update.message.reply_text(cancel_text, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [CallbackQueryHandler(select_language)],
            USER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_name)],
            BIRTH_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, birth_date)],
            DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, district)],
            APARTMENT_TYPE: [CallbackQueryHandler(apartment_type)],
            FLOOR_OR_FLOORS: [MessageHandler(filters.TEXT & ~filters.COMMAND, floor_or_floors)],
            APARTMENT_CONDITION: [CallbackQueryHandler(apartment_condition)],
            ROOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, rooms)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
