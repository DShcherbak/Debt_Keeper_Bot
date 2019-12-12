import telebot
import config
from database import *

bot = telebot.TeleBot(config.Token)
group = Group()
state = ''

@bot.message_handler(commands=['start'])
def send_welcome(message):
    file_info = read_from_database()

    group_id = str(message.chat.id)
    if group_id in file_info.keys():
        group.decode_from_JSON(file_info[str(message.chat.id)])
        bot.send_message(group.id, "Радий знову вас чути!")
    else:
        bot.send_message(message.chat.id, text='Всім привіт! Я - Debt Keeper Bot, радий знайомству!')
        bot.send_message(message.chat.id, text='Раджу всім додатися в список юзерів, щоб я міг надавати вам свої послуги.')
        bot.send_message(message.chat.id, text='Для цього напишіть команду /add та дотримуйтеся інструкцій.')
        group.id = message.chat.id
        


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.from_user.id, "В кого проблеми? Давайте розбиратися")


@bot.message_handler(commands=['resolve'])
def send_resolve(message):
    resolve(message.chat.id, config.debts[message.chat.id])


@bot.message_handler(func=lambda call: config.state == '', commands=['add'])
def new_user_welcome(message):
    if str(message.from_user.id) in config.debt_groups[str(message.chat.id)]:
        bot.send_message(message.chat.id, 'Я вже вас знаю, ' +
                         config.names_lib[str(message.chat.id)][message.from_user.id])
        bot.send_message(message.chat.id, 'Якщо бажаєте змінити свій нік, напишіть /rename')
        return
    config.state = 'get name' + str(message.chat.id)
    bot.send_message(message.from_user.id, "Як вас звати?")


@bot.message_handler(func=lambda call: config.state != '', commands=['add'])
def busy(message):
    bot.send_message(message.chat.id, 'Вибачте, я зараз спілкуюся з іншим користувачем, спробуйте пізніше')


def print_all_debts(group_id):
    for i in config.debts[group_id]:
        print_debt(group_id, i)


def print_debt(group_id, debt):
    text = config.names_lib[group_id][debt.payer] + ' : ' + config.names_lib[group_id][debt.sum] + ' <- '
    for d in debt.debtors:
        text += config.names_lib[group_id][d] + ', '
    bot.send_message(group_id, text)


def resolve(group_id, debt_array):
    if debt_array.size() == 0:
        return
    n = config.debt_groups[group_id].size()
    graph = [[0 for i in range(n)] for j in range(n)]
    for debt in debt_array:
        payer = debt.payer
        sum_val = debt.sum/debt.debtors.size()
        for debtor in debt.debtors:
            if not debtor == payer:
                graph[debtor][payer] += sum
    print(graph)
    personal_total = {0: pers for pers in config.debt_groups[group_id]}
    for pers in personal_total.keys():
        for i in range(n):
            personal_total[pers] += (graph[i][pers] - graph[pers][i])
    print(personal_total)

    plus_money = []
    minus_money = []
    all_set = []

    for pers in personal_total.keys():
        if personal_total[pers] > 0:
            plus_money.append((personal_total[pers], pers))
        elif personal_total[pers] < 0:
            minus_money.append((-personal_total[pers], pers))
        else:
            all_set.append(pers)

    plus_money.sort()
    minus_money.sort()

    i = 0
    j = 0
    n = len(plus_money)
    m = len(minus_money)
    solution = []
    while i < n and j < m:
        if plus_money[i][0] < minus_money[j][0]:
            i += 1
        elif plus_money[i][0] > minus_money[j][0]:
            j += 1
        else:
            solution.append((minus_money[j][1], plus_money[i][1], plus_money[i][0]))
            del plus_money[i]
            del minus_money[j]
            n -= 1
            m -= 1
    while n > 0:
        while plus_money[n-1][0] >= minus_money[m-1][0]:
            solution.append((minus_money[m - 1][1], plus_money[n - 1][1], minus_money[m-1][0]))
            plus_money[n - 1][0] -= minus_money[m - 1][0]
            del minus_money[m - 1]
            m -= 1
        if n > 1 and plus_money[n-2][0] > minus_money[m-1][0]:
            move(plus_money)
        else:
            solution.append((minus_money[m - 1][1], plus_money[n - 1][1], plus_money[n - 1][0]))
            minus_money[m - 1][0] -= plus_money[n - 1][0]
            del plus_money[n - 1]
            n -= 1


def move(array):
    n = len(array)
    while n > 1 and array[n - 1][0] > array[n - 2][0]:
        array[n - 1], array[n - 2] = array[n - 2], array[n - 1]
        n -= 1


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
        print_all_debts(call.data[:-1])
    bot.send_message(call.data[:-1], result)


def add_new_debt(group_id, user_id):
    new_id = config.current_debt_id[group_id]
    config.current_debt_id[group_id] += 1
    new_debt = Debt()
    if group_id in config.current_debt_id:
        config.debts[group_id].append(new_debt)
        config.current_debt_id[group_id] += 1
    else:
        config.debts.update([(group_id, [new_debt])])
        config.current_debt_id.update([(group_id, 1)])
    get_payer(group_id, user_id, new_id)


def get_payer(group_id, user_id, current_debt_id):
    bot.send_message(user_id, text='Хто платив?')
    config.state = 'payer' + group_id


@bot.message_handler(func=lambda call: config.state[:5] == 'payer', content_types=['text'])
def get_text_messages(message):
    group_id = config.state[5:]
    if message.text in config.id_lib[group_id]:
        bot.send_message(message.from_user.id, "OK")
        curr_debt_id = config.current_debt_id[group_id]-1
        config.debts[group_id][curr_debt_id].payer = config.id_lib[group_id][message.text]
        config.state = 'debtors' + group_id
        bot.send_message(message.from_user.id, text='За кого заплатили?')
        bot.send_message(message.from_user.id, "(напишіть '/all' щоб додати всіх з чату)")
    else:
        bot.send_message(message.from_user.id, "Ви вказали невірне ім'я, спробуйте ще раз")


@bot.message_handler(func=lambda call: config.state[:7] == 'debtors', content_types=['text'])
def get_text_messages(message):
    group_id = config.state[7:]
    debtor = message.text
    cur_debt_id = config.current_debt_id[group_id]-1
    if message.text == '/cancel':
        config.debts[group_id].pop_back()
        config.current_debt_id[group_id] -= 1
        config.state = ''
        return
    if config.debts[group_id][cur_debt_id].debtors == [] and message.text == '/break':
        bot.send_message(message.from_user.id, "Має бути принаймні один боржник.")
        bot.send_message(message.from_user.id, "Введіть ім'я щоб продовдити або '/cancel' для скасування")
        return
    if message.text == '/all':
        cur_debt_id = config.current_debt_id[group_id]-1
        for i in config.debt_groups[group_id]:
            if i not in config.debts[cur_debt_id].debtors:
                config.debts[cur_debt_id].debtors.append(config.id_lib[group_id][i])

    if message.text == '/break' or message.text == '/all':
        bot.send_message(message.from_user.id, "OK")
        config.state = 'sum' + str(group_id)
        bot.send_message(message.from_user.id, "Яка сума боргу?")

    if debtor in config.id_lib[group_id].keys():
        if debtor in config.debts[group_id][cur_debt_id].debtors:
            bot.send_message(message.from_user.id, "Цього боржника вже згадували, модливо ще хтось?")
        else:
            bot.send_message(message.from_user.id,  "OK, ще хтось? (напишіть '/break' щоб закінчити перерахунок)")
            config.debts[group_id][cur_debt_id].debtors.append(config.id_lib[group_id][debtor])
    else:
        bot.send_message(message.from_user.id, "Ви вказали невірне ім'я, спробуйте ще раз")


@bot.message_handler(func=lambda call: config.state[:3] == 'sum', content_types=['text'])
def get_sum(message):
    if not message.text.isdigit():
        bot.send_message(message.from_user.id, "Необхідно ввести додатнє число, спробуйте ще раз")
        return
    debt_sum = int(message.text)
    if debt_sum <= 0:
        bot.send_message(message.from_user.id, "Необхідно ввести додатнє число, спробуйте ще раз")
        return
    group_id = config.state[3:]
    cur_debt_id = config.current_debt_id[group_id]-1
    config.debts[group_id][cur_debt_id].sum = debt_sum
    bot.send_message(message.from_user.id, "OK")


    config.state = ''


@bot.message_handler(func=lambda call: config.state[:3] == 'confirm', content_types=['text'])
def get_confirmation(message):
    bot.send_message(message.from_user.id, "Все вірно?")


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





bot.polling(none_stop=True, interval=0)
