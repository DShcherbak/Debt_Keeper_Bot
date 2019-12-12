import telebot
from database import *
from Group import Debt, Group

bot = telebot.TeleBot('1054698181:AAEmAqgJ_pc6P7Hbd6XWN2Bb-MJzxS4os1U')
group = Group()
reachable_users = []
state = ''


@bot.message_handler(commands=['start'])
def send_welcome(message):
    global reachable_users, group
    file_info = read_from_database()
    reachable_users = get_users()

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
def send_help(message):
    bot.send_message(message.from_user.id, "В кого проблеми? Давайте розбиратися")


@bot.message_handler(commands=['resolve'])
def send_resolve(message):
    resolve(message.chat.id, group.debts) #TODO Probobly the whole resolve metod might wanna be here


@bot.message_handler(func=lambda call: state == '', commands=['add'])
def new_user_welcome(message):
    global state, reachable_users
    user_id = str(message.from_user.id)
    if user_id not in reachable_users:
        bot.send_message(group.id, 'Я не маю права починати діалог з користувачем')
        bot.send_message(group.id, 'Будь ласка, напишіть мені в лс, щоб я міг додати вас')
    else:
        if user_id in group.id_lib:
            bot.send_message(group.id, 'Я вже вас знаю, ' + group.names_lib[user_id])
            bot.send_message(group.id, 'Якщо бажаєте змінити свій нік, напишіть /rename')
            return
        else:
            state = 'get name'
            bot.send_message(user_id, "Як вас звати?")


@bot.message_handler(func=lambda call: state != '', commands=['add'])
def busy(message):
    bot.send_message(message.chat.id, 'Вибачте, я зараз спілкуюся з іншим користувачем, спробуйте пізніше')


def print_all_debts(group_id):
    for i in group.debts:
        print_debt(i)


def print_debt(debt):
    global group
    text = group.names_lib[debt.payer] + ' : ' + debt.sum + ' <- '
    for d in debt.debtors:
        text += group.names_lib[d] + ', '
    bot.send_message(group.id, text)


def move(array):
    n = len(array)
    while n > 1 and array[n - 1][0] > array[n - 2][0]:
        array[n - 1], array[n - 2] = array[n - 2], array[n - 1]
        n -= 1


def resolve(debt_array):
    global group
    if debt_array.size() == 0:
        return
    n = group.id_lib.size()
    graph = [[0 for i in range(n)] for j in range(n)]
    for debt in debt_array:
        payer = debt.payer
        sum_val = debt.sum/debt.debtors.size()
        for debtor in debt.debtors:
            if not debtor == payer:
                graph[debtor][payer] += sum_val
    print(graph)


    personal_total = {pers: 0 for pers in group.id_lib.values()}
    for pers in personal_total:
        for i in range(n):
            personal_total[pers] += (graph[i][pers] - graph[pers][i])
    print(personal_total)


    plus_money = []
    minus_money = []
    all_set = []

    for pers in personal_total:
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
    print(solution)


@bot.message_handler(func=lambda call: state == 'get name')
def get_name(message):
    global group, state
    user_id = message.from_user.id
    bot.send_message(user_id, 'Приємно познайомитися, ' + message.text + '!')
    group.add_user(user_id, message.text)
    list_users(group)
    state = ''


def list_users(group):
    text = 'Users in this group:\n'
    for i in group.names_lib:
        text += group.names_lib[i] + '\n'
    bot.send_message(group.id, text)


@bot.message_handler(commands=['debt'])
def get_command(message):
    global group, state
    state = 'new'
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_new_debt = telebot.types.InlineKeyboardButton(text='Додати новий борг', callback_data='new_debt')
    key_list = telebot.types.InlineKeyboardButton(text='Показати список боргів', callback_data='list_debts')
    keyboard.add(key_new_debt)
    keyboard.add(key_list)
    question = "Хтось знову заборгував?)"
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: state == 'new')
def form(call):
    global group
    if call.data == 'new_debt':
        add_new_debt(group.id, call.from_user.id)
        result = 'Вітаю з новою покупкою!'
    else:
        result = 'От список поточних боргів:'
        print_all_debts(group.id)
    bot.send_message(group.id, result)


def add_new_debt(user_id):
    global group
    new_id = group.current_debt_id
    group.current_debt_id += 1
    new_debt = Debt()
    group.debts.append(new_debt)
    group.current_debt_id += 1
    bot.send_message(user_id, text='Хто платив?')
    state = 'payer'


@bot.message_handler(func=lambda call: state == 'payer', content_types=['text'])
def get_text_messages(message):
    global group, state
    user_id = message.from_user.id
    if message.text in group.id_lib:
        bot.send_message(user_id, "OK")
        curr_debt_id = group.current_debt_id-1
        group.debts[curr_debt_id].payer = group.id_lib[message.text]
        state = 'debtors'
        bot.send_message(user_id, text='За кого платили?')
        bot.send_message(user_id, "(напишіть '/all' щоб додати всіх з чату)")
    else:
        bot.send_message(user_id, "Ви вказали невірне ім'я, спробуйте ще раз")


@bot.message_handler(func=lambda call: state == 'debtors', content_types=['text'])
def get_text_messages(message):
    global group, state
    user_id = message.from_user.id
    debtor = message.text
    cur_debt_id = group.current_debt_id-1
    if message.text == '/cancel':
        group.debts.pop_back()
        group.current_debt_id -= 1
        state = ''
        return
    if group.debts[cur_debt_id].debtors == [] and message.text == '/break':
        bot.send_message(user_id, "Має бути принаймні один боржник.")
        bot.send_message(user_id, "Введіть ім'я щоб продовдити або '/cancel' для скасування")
        return
    if message.text == '/all':
        for i in group.names_lib:
            if i not in group.debts[cur_debt_id].debtors:
                group.debts[cur_debt_id].debtors.append(group.id_lib[i])
    if message.text == '/break' or message.text == '/all':
        bot.send_message(user_id, "OK")
        state = 'sum'
        bot.send_message(user_id, "Яка сума боргу?")
    if debtor in group.id_lib:
        if debtor in group.debts[cur_debt_id].debtors:
            bot.send_message(user_id, "Цього боржника вже згадували, модливо ще хтось?")
        else:
            bot.send_message(user_id,  "OK, ще хтось? (напишіть '/break' щоб закінчити перерахунок)")
            group.debts[cur_debt_id].debtors.append(group.id_lib[debtor])
    else:
        bot.send_message(user_id, "Ви вказали невірне ім'я, спробуйте ще раз")


@bot.message_handler(func=lambda call: state == 'sum', content_types=['text'])
def get_sum(message):
    global group, state
    user_id = message.from_user.id
    if not message.text.isdigit():
        bot.send_message(user_id, "Необхідно ввести додатнє число, спробуйте ще раз")
        return
    debt_sum = int(message.text)
    if debt_sum <= 0:
        bot.send_message(user_id, "Необхідно ввести додатнє число, спробуйте ще раз")
        return
    cur_debt_id = group.current_debt_id-1
    group.debts[cur_debt_id].sum = debt_sum
    bot.send_message(user_id, "OK")
    state = ''


@bot.message_handler(func=lambda call: state[:3] == 'confirm', content_types=['text'])
def get_confirmation(message):
    bot.send_message(message.from_user.id, "Все вірно?")

















@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привіт":
        bot.send_message(message.from_user.id, "Привіт, чим я можу допомогити?")
    else:
        bot.send_message(message.from_user.id, "Я тут для підрахунку боргів, а не для балачок. Напиши /help.")


@bot.callback_query_handler(func=lambda call: state == 'debt')
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
        state = 'confirm'
        require_confirm(current_debt_id, result)


def new_person_to_debt(user_id, current_debt_id, in_the_debt=None):
    if in_the_debt is None:
        in_the_debt = set()
    keyboard = telebot.types.InlineKeyboardMarkup()
    str_group = str(current_debt_id) + str((i + ' ') for i in in_the_debt)
    key_pos = []
    for i in group.names_lib.values():
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


@bot.callback_query_handler(func=lambda call: state == 'confirm')
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
