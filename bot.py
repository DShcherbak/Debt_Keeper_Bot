import telebot;
bot = telebot.TeleBot('1054698181:AAEmAqgJ_pc6P7Hbd6XWN2Bb-MJzxS4os1U');


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Здоровенькі були")
    ask_bidding(message.chat.id, message.from_user.id)


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.from_user.id, "В кого проблеми? Давайте розбиратися")




@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привіт":
        bot.send_message(message.from_user.id, "Привіт, чим я можу допомогити?")
    else:
        bot.send_message(message.from_user.id, "0______________0. Напиши /help.")

@bot.message_handler(commands=['new'])
def get_text_messages(message):
    ask_new_debt(message.chat.id, message.from_user.id)

def new_debt(group_id, user_id):
    in_the_debt = []
    

def add_person_to_debt(group_id, user_id):
    str_group = str(group_id)
    keyboard = telebot.types.InlineKeyboardMarkup()
    for i in range(0
        key_pos[i] = telebot.types.InlineKeyboardButton(text='Додати новий персональний борг', callback_data=str_group + 'r')
    key_pas = 
    keyboard.add(key_raz)
    keyboard.add(key_pas)
    keyboard.add(key_m)
    question = "Хтось знову заборгував?)"
    bot.send_message(user_id, text=question, reply_markup=keyboard)


    

# (func=lambda call: config.state == 'bidding')

def test_message(message):
    return message


@bot.callback_query_handler(func=test_message)
def bidding(call):
    if call.data[-1] == 'r':
        result = 'У нас нові боржнички!'
    elif call.data[-1] == 'f':
        result = 'Вітаю з новою покупкою! Що придбали?'
    else:
        result = 'От список поточних боргів:'
    bot.send_message(call.data[:-1], result)


def ask_bidding(group_id, user_id):
    str_group = str(group_id)
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_raz = telebot.types.InlineKeyboardButton(text='Додати новий персональний борг', callback_data=str_group + 'r')
    key_pas = telebot.types.InlineKeyboardButton(text='Додати новий груповий борг', callback_data=str_group + 'f')
    key_m = telebot.types.InlineKeyboardButton(text='Показати поточний розв\'язок', callback_data=str_group + 'm')
    keyboard.add(key_raz)
    keyboard.add(key_pas)
    keyboard.add(key_m)
    question = "Хтось знову заборгував?)"
    bot.send_message(user_id, text=question, reply_markup=keyboard)


bot.polling(none_stop=True, interval=0)
