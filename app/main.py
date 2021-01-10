import telebot
from messages import *
from settings import tg_api_key, admin_chat
from repository import UserRepository


bot = telebot.TeleBot(tg_api_key, parse_mode="HTML")


@bot.callback_query_handler(lambda call: call.data in ['approve', 'decline'])
def prove_callback(call):
    telegram_tag = call.message.text[call.message.text.find('@')+1:call.message.text.find('\n')]
    user_data = UserRepository().get_user(telegram_tag)
    target_chat_id = user_data['fields'].get('chat_id')
    if call.data == "approve":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=call.message.text + ADMIN_APPROVE_MESSAGE,
            reply_markup=None
        )
        bot.send_message(target_chat_id, APPROVE_TO_USER_MESSAGE)
    elif call.data == "decline":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=call.message.text + ADMIN_DECLINE_MESSAGE,
            reply_markup=None
        )
        bot.send_message(target_chat_id, DECLINE_TO_USER_MESSAGE)


@bot.callback_query_handler(lambda call: call.data in ['register', 'help', 'reset'])
def handle_query(call):
    if call.data == "register":
        register(call.message)
    elif call.data == "help":
        print_help(call.message.chat.id)
    elif call.data == "reset":
        reset(call.message)


@bot.message_handler(commands=['start'])
def start(message):
    username = str(message.chat.username)
    chat_id = message.from_user.id
    bot.send_chat_action(chat_id, 'typing')

    if not username:
        bot.send_message(chat_id, TAG_ERROR_MESSAGE)
        return

    user_data = UserRepository().get_user(username)
    commands = {
        'register': 'Подать заявку на вступление в клан',
        'help': 'Помощь',
    }

    if not user_data:
        message = HELLO_MESSAGE
    else:
        if user_data['fields'].get('message_id', ''):
            commands = {
                'reset': 'Перезапустить процесс подачи заявки',
                'help': 'Помощь',
            }
        message = f"И снова привет, {user_data['fields'].get('xboxlive', 'Страж')}. Чем могу помочь?",

    bot.send_message(chat_id, text=message, reply_markup=get_command_buttons(commands))


def print_help(chat_id: int):
    bot.send_chat_action(chat_id, 'typing')
    bot.send_message(chat_id, HELP_MESSAGE)


def get_command_buttons(commands: dict):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=len(commands))
    for data, text in commands.items():
        key = telebot.types.InlineKeyboardButton(text=text, callback_data=data)
        keyboard.add(key)
    return keyboard


def register(message):
    chat_id = str(message.chat.id)
    username = message.chat.username
    if not username:
        bot.send_message(chat_id,  TAG_ERROR_MESSAGE)
        return

    bot.send_chat_action(chat_id, 'typing')
    UserRepository().add_user(username, chat_id)
    bot.send_message(message.chat.id, CLAN_CHARTER_MESSAGE)
    bot.send_message(message.chat.id, REQUEST_NICKNAME)
    bot.register_next_step_handler(message, set_xbox_live_id)


def reset(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'Итак, Страж, ты решил что-то изменить...')
    bot.send_message(message.chat.id, REQUEST_NICKNAME)
    bot.register_next_step_handler(message, set_xbox_live_id)


def set_xbox_live_id(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    UserRepository().change_user(message.chat.username, 'xboxlive', message.text)
    bot.send_message(message.from_user.id, REQUEST_NAME)
    bot.register_next_step_handler(message, set_name)


def set_name(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    UserRepository().change_user(message.chat.username, 'name', message.text)
    bot.send_message(message.from_user.id, REQUEST_AGE)
    bot.register_next_step_handler(message, set_age)


def set_age(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    try:
        age = int(message.text)
    except ValueError:
        age = 0

    UserRepository().change_user(message.chat.username, 'age', age)
    bot.send_message(message.from_user.id, REQUEST_ABOUT_MESSAGE)
    bot.register_next_step_handler(message, set_about)


def set_about(message):
    bot.send_chat_action(message.from_user.id, 'typing')
    UserRepository().change_user(message.chat.username, 'about', message.text)
    render_total(message.chat.username)


def render_total(telegram_tag: str):
    fields = UserRepository().get_user(telegram_tag)['fields']
    msg = f"Telegram: @{fields.get('tg', '')}\n" \
          f"XBL: {fields.get('xboxlive', '')}\n" \
          f"Имя: {fields.get('name', '')}\n" \
          f"Возраст: {fields.get('age', '')}\n" \
          f"О себе: {fields.get('about', '')}"

    keyboard_approve = telebot.types.InlineKeyboardMarkup(row_width=1)
    key_approve = telebot.types.InlineKeyboardButton(text='Да', callback_data='approve')
    keyboard_approve.add(key_approve)
    key_decline = telebot.types.InlineKeyboardButton(text='Нет', callback_data='decline')
    keyboard_approve.add(key_decline)

    if fields.get('message_id', ''):
        bot.edit_message_text(
            chat_id=admin_chat,
            message_id=int(fields['message_id']),
            text=msg,
            reply_markup=keyboard_approve
        )
    else:
        result = bot.send_message(admin_chat, text=msg, reply_markup=keyboard_approve)
        UserRepository().change_user(telegram_tag, 'message_id', str(result.message_id))

    keyboard_reset = telebot.types.InlineKeyboardMarkup(row_width=1)
    key_reset = telebot.types.InlineKeyboardButton(text='Перезапустить процесс подачи заявки', callback_data='reset')
    keyboard_reset.add(key_reset)
    bot.send_message(int(fields['chat_id']), text=RESET_MESSAGE, reply_markup=keyboard_reset)
    bot.send_message(int(fields['chat_id']), BUNGIE_NET_MESSAGE)



if __name__ == '__main__':
    bot.polling(none_stop=True, interval=2)
