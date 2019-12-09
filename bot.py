import telebot
import config
from debt import Debt

bot = telebot.TeleBot(config.Token);
payers = []
debtors = []
debt_id = 0

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Здоровенькі були")
    config.state = 'new debt'
    bot.send_message(message.chat.id, text='Раджу всім додатися в список юзерів, щоб я міг надавати вам свої послуги.')
    bot.send_message(message.chat.id, text='Для цього напишіть команду /add та дотримуйтеся інструкцій.')


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.from_user.id, "В кого проблеми? Давайте розбиратися")


@bot.message_handler(commands=['add'])
def new_user_welcome(message):
    if message.from_user.id in current_group:
        bot.send_message(message.chat.id, 'Я вже вас знаю, ' +
                         config.names_lib[str(message.chat.id)][message.from_user.id])
        bot.send_message(message.chat.id, 'Якщо бажаєте змінити свій нік, напишіть /rename')
        return
    config.state = 'get name' + str(message.chat.id)
    bot.send_message(message.from_user.id, "Як вас звати?")


@bot.message_handler(func=lambda call: config.state[:8] == 'get name')
def get_name(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Приємно познайомитися, ' + message.text + '!')
    group_id = config.state[8:]
    if group_id not in config.debt_groups:
        config.debt_groups[group_id] = []
        config.id_lib[group_id] = {}
        config.names_lib[group_id] = {}
    config.debt_groups[group_id].append(user_id)
    config.id_lib[group_id].update([(message.text, user_id)])
    config.names_lib[group_id].update([(user_id, message.text)])

    text = 'Users in this group:\n'
    for i in config.debt_groups[group_id]:
        text += config.names_lib[group_id][i] + '\n'
    bot.send_message(group_id, text)
    config.state = ''


@bot.message_handler(commands=['debt'])
def get_command(message):
    config.state = 'new'
    str_group = str(message.chat.id)
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_raz = telebot.types.InlineKeyboardButton(text='Додати новий борг', callback_data=str_group + 'd')
    key_m = telebot.types.InlineKeyboardButton(text='Показати список боргів', callback_data=str_group + 'l')
    keyboard.add(key_raz)
    keyboard.add(key_m)
    question = "Хтось знову заборгував?)"
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: config.state == 'new')
def form(call):
    if call.data[-1] == 'd':
        add_new_debt(call.data[:-1], call.from_user.id)
        result = 'Вітаю з новою покупкою!'
    else:
        result = 'От список поточних боргів:'
        list_debts(call.data[:-1])
    bot.send_message(call.data[:-1], result)


def add_new_debt(group_id, user_id):
    global debt_id
    new_id = debt_id
    debt_id += 1
    new_debt = Debt()
    if group_id in config.current_debt_id:
        config.depts[group_id].append(new_debt)
        config.current_debt_id[group_id] += 1
    else:
        config.depts.update((group_id, [new_debt]))
        config.current_debt_id.update((group_id, 1))
    get_payer(group_id, user_id, new_id)


def get_payer(group_id, user_id, current_debt_id):
    bot.send_message(user_id, text='Хто купляв?')
    config.state = 'payer' + str(group_id)


@bot.message_handler(func=lambda call: config.state[:5] == 'payer', content_types=['text'])
def get_text_messages(message):
    group_id = config.state[5:]
    if message.text in config.id_lib[group_id]:
        bot.send_message(message.from_user.id, "OK")
        config.state = 'debtors'
        bot.send_message(message.from_user.id, text='Хто купляв?')
    else:
        bot.send_message(message.from_user.id, "Ви вказали невірне ім'я, спробуйте ще раз")


@bot.message_handler(func=lambda call: config.state[:7] == 'debtors', content_types=['text'])
def get_text_messages(message):
    group_id = config.state[7:]
    debtor = message.text
    if debtor in config.id_lib[group_id]:
        #
        bot.send_message(message.from_user.id, "OK, ще хтось?")

    else:
        bot.send_message(message.from_user.id, "Ви вказали невірне ім'я, спробуйте ще раз")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привіт":
        bot.send_message(message.from_user.id, "Привіт, чим я можу допомогити?")
    else:
        bot.send_message(message.from_user.id, "Я тут для підрахунку боргів, а не для балачок. Напиши /help.")


@bot.callback_query_handler(func=lambda call: config.state == 'debt')
def register_new_debt(call):
    if call.data[-1] == 'c':
        return
    done = False
    if call.data[-1] == 'd':
        done = True
        call.data = call.data[:-1]
    space_id = 0
    while call.data[space_id] != ' ':
        space_id += 1
    current_debt_id = int(call.data[0:space_id])
    call.data = call.data[space_id:]
    in_the_debt = set(map(int, call.data.split(' ')))
    # bot.send_message(call.data[:-1], result)
    if not done:
        new_person_to_debt(call.from_user.id, current_debt_id, in_the_debt)
    else:
        result = '0'
        config.state = 'confirm'
        require_confirm(current_debt_id, result)


def new_person_to_debt(user_id, current_debt_id, in_the_debt=None):
    if in_the_debt is None:
        in_the_debt = set()
    keyboard = telebot.types.InlineKeyboardMarkup()
    str_group = str(current_debt_id) + str((i + ' ') for i in in_the_debt)
    key_pos = []
    for i in config.names_lib.values():
        if i not in in_the_debt:
            key_pos.append(telebot.types.InlineKeyboardButton(text=i.id, callback_data=str_group + str(i)))
            keyboard.add(key_pos[i])
    key_pas = telebot.types.InlineKeyboardButton(text='Cancel', callback_data=str_group + 'c')
    keyboard.add(key_pas)
    if in_the_debt != {}:
        key_done = telebot.types.InlineKeyboardButton(text='Done', callback_data=str_group + 'd')
        keyboard.add(key_done)
        question = "Хто іще боржник?"
    else:
        question = "Хто боржник?"
    bot.send_message(user_id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: config.state == 'confirm')
def get_confirm(call):
    if call.data[-1] == 'N':
        return
    call.data = call.data[:-1]
    bot.send_message(call.from_user.id, call.data)


def require_confirm(str_result, user_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_y = telebot.types.InlineKeyboardButton(text='Так', callback_data=str_result + 'Y')
    key_n = telebot.types.InlineKeyboardButton(text='Ні', callback_data=str_result + 'N')
    keyboard.add(key_y)
    keyboard.add(key_n)
    question = "Все вірно?"
    bot.send_message(user_id, text=question, reply_markup=keyboard)











def list_debts(group_id):
    pass


bot.polling(none_stop=True, interval=0)