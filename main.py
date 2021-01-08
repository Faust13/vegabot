import telebot
import airtable
import time
import logging
#from settings import *

atb_api_key = ''
atb_base_key = ''
atb_table = ''
tg_api_key = ''
err_message = '///ОШИБКА \n>>УД4Л3ННЫЙ У33Л: НЕТ 0Т83ТА \n//П3РЕЗ4ПУСК'
admin_chat=""


airtable = airtable.Airtable(atb_base_key, atb_table, atb_api_key)
bot = telebot.TeleBot(tg_api_key, parse_mode="HTML")
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

commands = {  # command description used in the "help" command
    'start'       : 'Начало работы',
    'register'    : 'Подать заявку на вступление в клан',
    'help'        : 'Помощь',
    'reset'       : 'Перезапустить процесс подачи заявки',
}

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    usr_data = []
    result = call.message.text.split('\n')
    print(result)
    firstline = result[0].split('@')
    nickname=firstline[1]
    print(nickname)
    try:
        usr_data=airtable.search('tg', nickname)
        print(usr_data)
    except:
        pass
    if call.data == "aprove": 
        if usr_data == []:
            try:
                usr_data=airtable.search('tg', nickname)
            except:
                bot.send_message(call.message.chat.id, 'Все сломалось, жмякни кнопку еще разок!')
        else:
            target_chat_id=usr_data[0].get('fields').get('chat_id')
            print(target_chat_id)
            msg = '\n<b>Пользователь принят в клан, не забудьте одобрить заявку в <a href="https://www.bungie.net/ru/ClanV2?groupid=2135560">Bungie.net</a>!</b>'
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text+msg, reply_markup=None)
            bot.send_message(target_chat_id, 'Администрация клана рассмотрела вашу заявку. Добро пожаловать! Для координации и общения у нас есть <a href="https://t.me/joinchat/T-VtrgW1KbFcWfoo">чат</a>.')
    elif call.data == "decline":
        bot.send_message(call.message.chat.id, 'Было принято решение отказать соискателю.')
        bot.send_message(target_chat_id, 'Администрация клана рассмотрела вашу заявку. К сожалению, на данный момент мы не готовы вас принять.')



@bot.message_handler(commands=['start'])
def command_start(message):
    username = message.chat.username
    chat_id = message.from_user.id
    if username != None:
        try:
            usr_data=airtable.search('chat_id', str(chat_id))
            logging.info('Got some user data from airtable: '+usr_data)
        except Exception:
            usr_data=airtable.search('chat_id', str(chat_id)) #try again

            if usr_data == []:  # if user hasn't used the "/start" command yet:
                try:
                    airtable.insert({'chat_id': str(chat_id)})  # save user id
                    logging.info('New user with id '+str(chat_id)+' was added to database')
                except Exception:
                    airtable.insert({'chat_id': str(chat_id)})  # try to save again
                    logging.info('2nd try. New user with id '+str(chat_id)+' was added to database')
                bot.send_message(chat_id, '''Привет, страж! Я - фрейм Xbox-клана Guardian.FM VEGA.
Моей задачей является автоматизация рутинных действий внутри клана. Вот что ты можешь сделать: ''')
                command_help(message)  # show the new user the help page
            else:
                cln_data = usr_data[0].get('fields')
                if cln_data.get('xboxlive') == None:
                    cln_data.update({'xboxlive':'страж'})
                else:
                    pass
                bot.send_message(chat_id, "И снова привет, "+cln_data.get('xboxlive')+". Чем могу помочь?")
        except Exception:
            bot.send_message(chat_id, err_message)
    else:
        bot.send_message(chat_id, '''❌❌❌ Ой-ей, похоже, у тебя не установлен телеграм-тэг. В таком случае, администрация клана не сможет тебя найти и пригласить в наш телеграм-чат. Что же делать делать?
Ты можешь установить тэг, <a href="https://telegramzy.ru/nik-v-telegramm/">как это сделать - описано в этой инструкции</a>. После этого ты сможешь заполнить анкету соискателя, написав /register.
''')


# help page
@bot.message_handler(commands=['help'])
def command_help(message):
    chat_id = message.from_user.id
    help_text = "Доступные команды: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + " - "
        help_text += commands[key] + "\n"
    bot.send_message(chat_id, help_text)  # send the generated help page


@bot.message_handler(commands=['register'])
def register(message):
    chat_id = message.from_user.id
    username = message.chat.username

    #logging.info('Username is '+username)
    if username != None:
        try:
            bot.send_chat_action(chat_id, 'typing')  # show the bot "typing" (max. 5 secs)
            time.sleep(3)
            airtable.update_by_field('chat_id', str(chat_id), {'tg': username})
            bot.send_message(message.from_user.id, '''Перед подачей заявки, пожалуйста, ознакомься с уставом клана. Он находится <a href="https://docs.google.com/document/d/1phtUEpk8as8rn3pLCT5eelAdsCH1QB8d5vT7E4YDS4w">тут</a>.
<b>⚠️⚠️⚠️ Обрати внимание - дальнейшее продолжение диалога со мной подтверждает то, что ты ознакомился и согласен с уставом! ⚠️⚠️⚠️</b>

Для продолжения напиши мне свой gamertag Xbox Live (никнейм):
''')
            bot.register_next_step_handler(message, get_xbl_id)
        except Exception:
            bot.send_message(chat_id, err_message)
    else:
        bot.send_message(chat_id, '''❌ Прости, у тебя не установлен телеграм-тэг. 
Напомню, что ты можешь установить тэг, как это сделать - <a href="https://telegramzy.ru/nik-v-telegramm/">описано в этой инструкции</a>.
После этого у тебя появится возможность продолжить процесс подачи заявки на вступление в клан.
''')
        logging.info('Here is user without username. chat_id is '+str(chat_id))

@bot.message_handler(commands=['reset'])
def reset(message):
    register(message)

@bot.message_handler(content_types=['text'])
def get_xbl_id(message):
    if message.text == '/reset':
        reset(message)
    elif message.text == '/help':
        command_help(message)
    else:
        bot.send_message(message.from_user.id, 'Как тебя зовут?')
        xbl_id = message.text
        try:
            airtable.update_by_field('chat_id', str(message.from_user.id), {'xboxlive': xbl_id})
        except Exception:
            bot.send_message(message.from_user.id, err_message)

        bot.register_next_step_handler(message, get_name)

def get_name(message):
    if message.text == '/reset':
        reset(message)
    elif message.text == '/help':
        command_help(message)
    else:
        name = message.text
        try:
            airtable.update_by_field('chat_id', str(message.from_user.id), {'name': name})
        except Exception:
            bot.send_message(message.from_user.id, err_message)
            get_name(message)

        bot.send_message(message.from_user.id, 'Сколько тебе лет?')
        bot.register_next_step_handler(message, get_age)

def get_age(message):
    if message.text == '/reset':
        reset(message)
    else:
        age = 0
        if age == 0:
            try:
                age = int(message.text)
            except Exception:
                age = 0
        try:
            airtable.update_by_field('chat_id', str(message.from_user.id), {'age': age})
        except Exception:
            bot.send_message(message.from_user.id, err_message)
            get_age(message)

        bot.send_message(message.from_user.id, '''Отлично! Последний штрих - расскажи немного о себе. \n
Да, это не обязательно, но заявки от участников, которые не поленились и потратили 5 минут на "интро" рассматриваются администраторами быстрее. \n
Хоть я и бездушная машина, я понимаю, что писать о себе всегда сложно, поэтому вот список вопросов, на которые ты можешь ответить в своем интро: как давно ты играешь в Destiny? Где живешь? Чем увлекаешься IRL? Ходил ли ты в рейды, и если да - то какой из них - твой любимый?''')
        bot.register_next_step_handler(message, get_about)

def get_about(message):
    if message.text == '/reset':
        reset(message)
    elif message.text == '/help':
        command_help(message)
    else:
        about = message.text
        try:
            airtable.update_by_field('chat_id', str(message.from_user.id), {'about': about})
            user_data = airtable.search('chat_id', str(message.from_user.id))
        except Exception:
            bot.send_message(message.from_user.id, err_message)
            get_about(message)
        global clean_data
        clean_data = user_data[0].get('fields')
        msg = 'Telegram: @'+clean_data.get('tg')+'\nXBL: '+clean_data.get('xboxlive')+'\nИмя: '+clean_data.get('name')+'\nВозраст: '+str(clean_data.get('age'))+'\nО себе: '+clean_data.get('about')
        #keyboard block
        keyboard_aprove = telebot.types.InlineKeyboardMarkup(row_width=1)
        key_aprove = telebot.types.InlineKeyboardButton(text='Да', callback_data='aprove')
        keyboard_aprove.add(key_aprove) 
        key_decline = telebot.types.InlineKeyboardButton(text='Нет', callback_data='decline')
        keyboard_aprove.add(key_decline)

        bot.send_message(admin_chat, text=msg, reply_markup=keyboard_aprove)
        bot.send_message(message.from_user.id, 'Если ты где-то что-то заполнил неправильно - не переживай. Ты можешь просто ввести /reset и снова заполнить анкету соискателя. Главное - без фанатизма.')
        bot.send_message(message.from_user.id, 'Если же все ок - нет причин волноваться, твоя заявка была передана на рассмотрение администрации. А пока можешь отправить заявку на вступление в <a href="https://www.bungie.net/ru/ClanV2?groupid=2135560">наш клан в Bungie.net</a> (если ты этого все еще не сделал).')

bot.polling(none_stop=True, interval=2)