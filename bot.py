import telebot
from database import *
from Group import Debt, Group

bot = telebot.TeleBot('1054698181:AAEmAqgJ_pc6P7Hbd6XWN2Bb-MJzxS4os1U')
group = Group()
reachable_users = []
groups = {}
state = {}


# TODO -list:
# TODO: state-variable: must be personalized for each user, so they can use bot on the same time
# TODO: need to take float-arguments when reading someone's debt
# TODO: need to figure out a way to approve new debt-system and to cancel-out debts
# TODO: make /cancel a command


@bot.message_handler(func=lambda message: message.chat.type == 'private', commands=['start'])
def send_hello(message):
    bot.send_message(message.from_user.id, 'Привіт, дякую що написали! Мене звати Debt Keeper Bot, радий знайомству!')
    bot.send_message(message.from_user.id, 'Тепер ви можете додати мене в будь-який чат, і я вестиму в ньому облік боргів')
    reachable_users.append(str(message.from_user.id))
    remember_users(reachable_users)


@bot.message_handler(func=lambda message: message.chat.type == 'private', commands=['help'])
def personal_help(message):
    text = "Я не так багато вмію в нашому з вами маленькому чаті. "
    text += "Але мене можна додати в групу, і там можна буде додавати борги між користувачами,"
    text += " а я буду їх запам'ятовувати."
    bot.send_message(message.from_user.id, text)


@bot.message_handler(func=lambda message: (message.chat.type == 'private')
                                          and (state[str(message.from_user.id)] == ''), content_types=['text'])
def messaging(message):
    user_id = str(message.from_user.id)
    if user_id not in reachable_users:
        reachable_users.append(user_id)
        remember_users(reachable_users)
    text = 'Вау, з вами так цікаво! Розкажіть ще щось.'
    bot.send_message(user_id, text)


@bot.message_handler(func=lambda message: message.chat.type == 'group', commands=['start'])
def send_welcome(message):
    global reachable_users, group, groups, state
    groups_dict = read_from_database()
    for group_id in groups_dict:
        g = Group()
        g.decode_from_json(groups_dict[group_id])
        # print(g.id_lib)
        groups.update([(group_id, g)])
    reachable_users = get_users()
    group_id = str(message.chat.id)

    if group_id in groups:
        print(groups[group_id])
        group.renew(groups[group_id])
        print(group.id_lib)
        bot.send_message(group.id, "Радий знову вас чути!")
        for user_id in group.names_lib:
            state.update([(user_id, '')])
        print_all_people()
    else:
        bot.send_message(message.chat.id, 'Всім привіт! Я - Debt Keeper Bot, радий знайомству!')
        bot.send_message(message.chat.id, 'Раджу всім додатися в список юзерів, щоб я міг надавати вам свої послуги.')
        bot.send_message(message.chat.id, 'Для цього напишіть команду /add та дотримуйтеся інструкцій.')
        group.id = str(message.chat.id)
        group.names_lib = {}
        group.id_lib = {}
        group.debts = []
        groups.update([(group_id, group)])
        save_to_database(groups)


@bot.message_handler(func=lambda message: message.chat.type == 'private', commands=['help'])
def personal_help(message):
    text = "Я не так багато вмію в нашому з вами маленькому чаті. "
    text += "Але мене можна додати в групу, і там можна буде додавати борги між користувачами,"
    text += " а я буду їх запам'ятовувати."
    bot.send_message(message.from_user.id, text)


@bot.message_handler(func=lambda message: message.chat.type == 'group', commands=['help'])
def send_help(message):
    text = "Отже, що я вмію:\n"
    text += "/add - додати нового користувача до групи\n"
    text += "/debt - додати новий борг\n"
    text += "/list - вивести список користувачів\n"
    text += "/all - вивести список боргів"
    bot.send_message(message.chat.id, text)


def correct_group_message(message, correct_state, equal=True):
    global state
    if equal:
        return (message.chat.type == 'group') and (str(message.from_user.id) in reachable_users) and (
                state[str(message.from_user.id)] == correct_state)
    else:
        return (message.chat.type == 'group') and (str(message.from_user.id) in reachable_users) and (
                state[str(message.from_user.id)] != correct_state)


@bot.message_handler(func=lambda message: message.chat.type == 'group', commands=['add'])
def new_user_welcome(message):
    global state, reachable_users, group
    user_id = str(message.from_user.id)
    if user_id not in reachable_users:
        bot.send_message(group.id, 'Я не маю права починати діалог з користувачем')
        bot.send_message(group.id, 'Будь ласка, напишіть мені в лс, щоб я міг додати вас')
    else:
        if user_id in group.names_lib:
            bot.send_message(group.id, 'Бажаєте змінити ім\'я, га , ' + group.names_lib[
                user_id] + '? Нічого, тут немає чого соромитись.')
            bot.send_message(user_id, 'Яке ваше нове прізвисько?')
        else:
            bot.send_message(user_id, "Як вас звати?")

        state[user_id] = 'get name'


'''
@bot.message_handler(func=lambda message: correct_group_message(message, '', False), commands=['add'])
def busy(message):
    bot.send_message(message.chat.id, 'Вибачте, я зараз спілкуюся з іншим користувачем, спробуйте пізніше')
'''


@bot.message_handler(func=lambda message: message.chat.type == 'group', commands=['list'])
def listing(message):
    print_all_people()


@bot.message_handler(func=lambda message: message.chat.type == 'group', commands=['all'])
def listing(message):
    print_all_debts()


@bot.message_handler(func=lambda message: message.chat.type == 'group', commands=['resolve'])
def resolve(message):
    global group
    debt_array = group.debts
    if len(debt_array) == 0:
        return
    n = len(group.id_lib)

    vertice = {}
    cnt = 0
    for i in group.id_lib:
        vertice.update([(group.id_lib[i], cnt)])
        cnt += 1

    graph = [[0 for i in range(n)] for j in range(n)]
    for debt in debt_array:
        print(debt_to_text(debt))
        payer = debt.payer
        sum_val = debt.sum / len(debt.debtors)
        for debtor in debt.debtors:
            if not debtor == payer:
                graph[vertice[debtor]][vertice[payer]] += sum_val
        print(graph)

    personal_total = {pers: 0 for pers in group.id_lib.values()}
    for pers in personal_total:
        for i in range(n):
            personal_total[pers] += (graph[i][vertice[pers]] - graph[vertice[pers]][i])
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
    n = len(plus_money) - 1
    m = len(minus_money) - 1
    solution = []
    while i <= n and j <= m:
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
    print(n, m, len(plus_money), len(minus_money))

    while n >= 0:
        while m >= 0 and plus_money[n][0] >= minus_money[m][0]:
            solution.append((minus_money[m][1], plus_money[n][1], minus_money[m][0]))
            plus_money[n] = (plus_money[n][0] - minus_money[m][0], plus_money[n][1])
            # plus_money[n][0] -= minus_money[m][0]
            del minus_money[m]
            m -= 1
            if plus_money[n][0] == 0:
                del plus_money[n]
                n -= 1
        if n > 0 and plus_money[n - 1][0] > minus_money[m][0]:
            move(plus_money)
        elif n >= 0 and m >= 0:
            solution.append((minus_money[m][1], plus_money[n][1], plus_money[n][0]))
            minus_money[m] = (minus_money[m][0] - plus_money[n][0], minus_money[m][1])
            # minus_money[m][0] -= plus_money[n][0]
            del plus_money[n]
            n -= 1

    bot.send_message(group.id, "Here's my solution")
    for s in solution:
        bot.send_message(group.id, group.names_lib[s[0]] + " -> " + group.names_lib[s[1]] + " : " + str(s[2]))

    print(solution)


@bot.message_handler(func=lambda message: (str(message.from_user.id) in reachable_users) and (
        state[str(message.from_user.id)] == 'get name'))
def get_name(message):
    global group, state
    user_id = str(message.from_user.id)
    bot.send_message(user_id, 'Приємно познайомитися, ' + message.text + '!')
    group.add_user(user_id, message.text)
    list_users(group)
    state.update([(user_id, '')])
    groups[group.id].renew(group)
    save_to_database(groups)
    state[user_id] = ''


def list_users(group):
    text = 'Users in this group:\n'
    for i in group.names_lib:
        text += group.names_lib[i] + '\n'
    bot.send_message(group.id, text)


@bot.message_handler(commands=['debt'])
def get_command(message):
    global group, state
    state[str(message.from_user.id)] = 'new'
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_new_debt = telebot.types.InlineKeyboardButton(text='Додати новий борг', callback_data='new_debt')
    key_list = telebot.types.InlineKeyboardButton(text='Показати список боргів', callback_data='list_debts')
    keyboard.add(key_new_debt)
    keyboard.add(key_list)
    question = "Хтось знову заборгував?)"
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(
    func=lambda message: (str(message.from_user.id) in reachable_users) and (state[str(message.from_user.id)] == 'new'))
def form(call):
    global group
    if call.data == 'new_debt':
        add_new_debt(str(call.from_user.id))
    else:
        print_all_debts()


def add_new_debt(user_id):
    global group, state
    group.current_debt_id += 1
    new_debt = Debt()
    group.debts.append(new_debt)
    bot.send_message(user_id, text='Хто платив?')
    state[user_id] = 'payer'


@bot.message_handler(func=lambda message: (str(message.from_user.id) in reachable_users)
                                            and (state[str(message.from_user.id)] == 'payer'), content_types=['text'])
def get_text_messages(message):
    global group, state
    user_id = str(message.from_user.id)
    if message.text == '/cancel':
        group.debts.pop_back()
        group.current_debt_id -= 1
        state[user_id] = ''
        return
    if message.text in group.id_lib:
        bot.send_message(user_id, "OK")
        curr_debt_id = group.current_debt_id - 1
        print(curr_debt_id, len(group.debts))
        group.debts[curr_debt_id].payer = group.id_lib[message.text]
        state[user_id] = 'debtors'
        group.debts[curr_debt_id].debtors = []
        bot.send_message(user_id, text='За кого платили?')
        bot.send_message(user_id, "(напишіть '/every' щоб додати всіх з чату)")
    else:
        bot.send_message(user_id, "Ви вказали невірне ім'я, спробуйте ще раз")


@bot.message_handler(func=lambda message: (str(message.from_user.id) in reachable_users) and (
        state[str(message.from_user.id)] == 'debtors'), content_types=['text'])
def get_debtors(message):
    global group, state
    user_id = str(message.from_user.id)
    debtor = message.text
    cur_debt_id = group.current_debt_id - 1

    if message.text == '/cancel':
        bot.send_message(user_id, "Відміна!")
        group.debts.pop()
        group.current_debt_id -= 1
        state[user_id] = ''
        return
    if group.debts[cur_debt_id].debtors == [] and message.text == '/break':
        bot.send_message(user_id, "Має бути принаймні один боржник.")
        bot.send_message(user_id, "Введіть ім'я щоб продовдити або '/cancel' для скасування")
        return
    if message.text == '/every':
        for i in group.id_lib:
            print(i, group.id_lib[i])
            if group.id_lib[i] not in group.debts[cur_debt_id].debtors:
                group.debts[cur_debt_id].debtors.append(group.id_lib[i])
    if message.text == '/break' or message.text == '/every':
        bot.send_message(user_id, "OK")
        state[user_id] = 'sum'
        bot.send_message(user_id, "Яка сума боргу?")
    if debtor in group.id_lib:
        if debtor in group.debts[cur_debt_id].debtors:
            bot.send_message(user_id, "Цього боржника вже згадували, модливо ще хтось?")
        else:
            bot.send_message(user_id, "OK, ще хтось? (напишіть '/break' щоб закінчити перерахунок)")
            group.debts[cur_debt_id].debtors.append(group.id_lib[debtor])
    else:
        bot.send_message(user_id, "Ви вказали невірне ім'я, спробуйте ще раз")


@bot.message_handler(
    func=lambda message: (str(message.from_user.id) in reachable_users) and (state[str(message.from_user.id)] == 'sum'),
    content_types=['text'])
def get_sum(message):
    global group, state
    user_id = str(message.from_user.id)
    if not message.text.isdigit():
        bot.send_message(user_id, "Необхідно ввести додатнє число, спробуйте ще раз")
        return
    debt_sum = int(message.text)
    if debt_sum <= 0:
        bot.send_message(user_id, "Необхідно ввести додатнє число, спробуйте ще раз")
        return
    cur_debt_id = group.current_debt_id - 1
    group.debts[cur_debt_id].sum = debt_sum
    bot.send_message(user_id, "OK")
    bot.send_message(group.id, "Вітаю з новою покупкою!")
    print(debt_to_text(group.debts[cur_debt_id]))
    groups[group.id].renew(group)
    save_to_database(groups)
    state[user_id] = ''


def print_all_debts():
    text = 'Поточні борги:\n'
    for i in group.debts:
        text += debt_to_text(i) + '\n'
    bot.send_message(group.id, text)


def print_all_people():
    text = 'Учасники групи:\n'
    for i in group.names_lib:
        text += group.names_lib[i] + '\n'
    bot.send_message(group.id, text)


def debt_to_text(debt):
    global group
    text = group.names_lib[debt.payer] + ' : ' + str(debt.sum) + ' <- '
    for d in debt.debtors:
        text += group.names_lib[d] + ', '
    text = text[:-2] + ';'
    return text


def move(array):
    n = len(array)
    while n > 1 and array[n - 1][0] < array[n - 2][0]:
        array[n - 1], array[n - 2] = array[n - 2], array[n - 1]
        n -= 1


bot.polling(none_stop=True, interval=0)
