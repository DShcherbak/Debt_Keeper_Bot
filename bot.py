import telebot
from database import *
from Group import Debt, Group

bot = telebot.TeleBot('1054698181:AAEmAqgJ_pc6P7Hbd6XWN2Bb-MJzxS4os1U')

reachable_users = []
groups = {}
incoming_debts = {}
state = {}
previous_solution = {}



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
    text += "А тут доступні команди /start, /help, /cancel"
    text += "/cancel - відміна будь-якої поочної операції"
    bot.send_message(message.from_user.id, text)


def check_user_state(message, st):
    return state[str(message.from_user.id)][:len(st)] == st


def get_group_id(current_state):
    if current_state[0].isdigit():
        return current_state
    if current_state[:8] == 'get name':
        return current_state[8:]
    if current_state[:3] == 'new':
        return current_state[3:]
    if current_state[:5] == 'payer':
        return current_state[5:]
    if current_state[:7] == 'debtors':
        return current_state[7:]
    if current_state[:3] == 'sum':
        return current_state[3:]


@bot.message_handler(func=lambda message: message.chat.type == 'private', commands=['cancel'])
def personal_help(message):
    text = "Відміна"

    bot.send_message(message.from_user.id, text)


'''
@bot.message_handler(func=lambda message: (message.chat.type == 'private'), content_types=['text'])
def messaging(message):
    user_id = str(message.from_user.id)
    if user_id not in reachable_users:
        reachable_users.append(user_id)
        remember_users(reachable_users)
    text = 'Вау, з вами так цікаво! Розкажіть ще щось.'
    bot.send_message(user_id, text)
'''


@bot.message_handler(func=lambda message: message.chat.type == 'group', commands=['start'])
def send_welcome(message):
    global reachable_users, groups, state
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
        group = groups[group_id]
        print(group.id_lib)
        bot.send_message(group.id, "Радий знову вас чути!")
        print_all_people(group_id)
    else:
        bot.send_message(message.chat.id, 'Всім привіт! Я - Debt Keeper Bot, радий знайомству!')
        bot.send_message(message.chat.id, 'Раджу всім додатися в список юзерів, щоб я міг надавати вам свої послуги.')
        bot.send_message(message.chat.id, 'Для цього напишіть команду /add та дотримуйтеся інструкцій.')
        group = Group()
        group.id = str(message.chat.id)
        groups.update([(group_id, group)])
        save_to_database(groups)
    previous_solution.update([(str(message.chat.id), [(-1, -1, -1)])])
    state.update([(str(message.from_user.id), str(message.chat.id))])


@bot.message_handler(func=lambda message: message.chat.type == 'group', commands=['help'])
def send_help(message):
    text = "Отже, що я вмію:\n"
    text += "/add - додати нового користувача до групи\n"
    text += "/debt - додати новий борг\n"
    text += "/list - вивести список користувачів\n"
    text += "/all - вивести список боргів\n"
    text += "/resolve - розрахувати найпростіший варіант повернення заборгованостей\n"
    text += "/approve - прийняти запропонований мною варіант як поточну"
    text += " (команда /approve може бути виконана тільки після виконання операції /resolve."
    text += "Також прохання бути обачними, адже виконання команди призводить до втрати"
    text += " історії попередніх заборгованостей, залишаються лише суми, які учасники мають повернути."
    text += "Раджу порадитись з іншими учасниками перш ніж застосовувати цю команду)"
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: message.chat.type == 'group', commands=['add'])
def new_user_welcome(message):
    group = groups[str(message.chat.id)]
    user_id = str(message.from_user.id)
    if user_id not in reachable_users:
        print(user_id, " not in ", reachable_users)
        bot.send_message(group.id, 'Я не маю права починати діалог з користувачем')
        bot.send_message(group.id, 'Будь ласка, напишіть мені в лс, щоб я міг додати вас')
    else:

        if user_id in group.names_lib:
            bot.send_message(group.id, 'Бажаєте змінити ім\'я, га , ' + group.names_lib[
                user_id] + '? Нічого, тут немає чого соромитись.')
            bot.send_message(user_id, 'Яке ваше нове прізвисько?')
        else:
            bot.send_message(user_id, "Як вас звати?")

        state[user_id] = 'get name' + str(message.chat.id)


@bot.message_handler(func=lambda message: message.chat.type == 'group', commands=['list'])
def listing(message):
    print_all_people(str(message.chat.id))


@bot.message_handler(func=lambda message: message.chat.type == 'group', commands=['all'])
def listing(message):
    print_all_debts(str(message.chat.id))


@bot.message_handler(func=lambda message: message.chat.type == 'group', commands=['resolve'])
def resolve(message):
    global previous_solution
    group_id = str(message.chat.id)
    group = groups[group_id]
    debt_array = group.debts
    if len(debt_array) == 0:
        return
    n = len(group.id_lib)

    vertices = {}
    cnt = 0
    for i in group.id_lib:
        vertices.update([(group.id_lib[i], cnt)])
        cnt += 1

    graph = [[0 for i in range(n)] for j in range(n)]
    for debt in debt_array:
        print(debt_to_text(debt, group_id))
        payer = debt.payer
        sum_val = debt.sum / len(debt.debtors)
        for debtor in debt.debtors:
            if not debtor == payer:
                graph[vertices[debtor]][vertices[payer]] += sum_val
        print(graph)

    personal_total = {pers: 0 for pers in group.id_lib.values()}
    for pers in personal_total:
        for i in range(n):
            personal_total[pers] += (graph[i][vertices[pers]] - graph[vertices[pers]][i])
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
            if plus_money[n][0] < 0.25:
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
    #previous_solution[group_id] = []
    previous_solution[group_id] = list(solution)
    if not solution:
        bot.send_message(group.id, "Все чисто, боргів не лишилось!")
    print(solution)


@bot.message_handler(func=lambda message: message.chat.type == 'group', commands=['approve'])
def approval(message):
    global previous_solution
    group_id = str(message.chat.id)
    if (not previous_solution[group_id] == []) and previous_solution[group_id][0][0] == -1:
        bot.send_message(group_id, "Спершу необхідно викнати команду /resolve")
        return
    bot.send_message(group_id, "OK, міняю список боргів ")
    group = groups[group_id]
    group.debts = []
    for d in previous_solution[group_id]:
        print("blablabal")
        print(d)
        new_debt = Debt()
        new_debt. payer = d[1]
        new_debt.debtors = [d[0]]
        new_debt.sum = d[2]
        groups[group_id].debts.append(new_debt)
    previous_solution = [(-1, -1, -1)]
    save_to_database(groups)
    print_all_debts(group_id)


@bot.message_handler(func=lambda message: (str(message.from_user.id) in reachable_users) and check_user_state(message, 'get name'))
def get_name(message):
    user_id = str(message.from_user.id)
    group = groups[state[user_id][8:]]
    bot.send_message(user_id, 'Приємно познайомитися, ' + message.text + '!')
    group.add_user(user_id, message.text)
    list_users(group)
    state.update([(user_id, '')])
    groups[group.id].renew(group)
    save_to_database(groups)


def list_users(group):
    text = 'Users in this group:\n'
    for i in group.names_lib:
        text += group.names_lib[i] + '\n'
    bot.send_message(group.id, text)


@bot.message_handler(commands=['debt'])
def get_command(message):
    group_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    state[user_id] = 'new' + group_id
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_new_debt = telebot.types.InlineKeyboardButton(text='Додати новий борг', callback_data='new_debt')
    key_list = telebot.types.InlineKeyboardButton(text='Показати список боргів', callback_data='list_debts')
    key_people = telebot.types.InlineKeyboardButton(text='Показати список людей', callback_data='list_people')
    keyboard.add(key_new_debt)
    keyboard.add(key_list)
    keyboard.add(key_people)
    question = "Хтось знову заборгував?)"
    bot.send_message(user_id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(
    func=lambda message: (str(message.from_user.id) in reachable_users) and state[str(message.from_user.id)][:3] == 'new')
def form(call):
    user_id = str(call.from_user.id)
    group_id = state[user_id][3:]
    if call.data == 'new_debt':
        add_new_debt(user_id, group_id)
    elif call.data == 'list_debts':
        print_all_debts(group_id, user_id)
        state[user_id] = group_id
    else:
        print_all_people(group_id, user_id)
        state[user_id] = group_id


def add_new_debt(user_id, group_id):
    incoming_debts.update([(user_id, (group_id, Debt()))])
    bot.send_message(user_id, text='Хто платив?')
    state[user_id] = 'payer' + group_id


@bot.message_handler(func=lambda message: (str(message.from_user.id) in reachable_users)
                                            and check_user_state(message, 'payer'), content_types=['text'])
def get_text_messages(message):
    user_id = str(message.from_user.id)
    group_id = incoming_debts[user_id][0]
    group = groups[group_id]
    if message.text == '/cancel':
        incoming_debts.pop(user_id)
        state[user_id] = ''
        return
    if message.text in group.id_lib:
        bot.send_message(user_id, "OK")
        incoming_debts[user_id][1].payer = group.id_lib[message.text]
        state[user_id] = 'debtors' + group_id
        incoming_debts[user_id][1].debtors = []
        bot.send_message(user_id, text='За кого платили?')
        bot.send_message(user_id, "(напишіть '/every' щоб додати всіх з чату)")
    else:
        bot.send_message(user_id, "Ви вказали невірне ім'я, спробуйте ще раз")


@bot.message_handler(func=lambda message: (str(message.from_user.id) in reachable_users) and (
        check_user_state(message, 'debtors')), content_types=['text'])
def get_debtors(message):
    user_id = str(message.from_user.id)
    debtor = message.text
    group_id = state[user_id][7:]
    group = groups[group_id]
    if message.text == '/cancel':
        bot.send_message(user_id, "Відміна!")
        incoming_debts.pop(user_id)
        state[user_id] = group_id
        return
    if incoming_debts[user_id][1].debtors == [] and message.text == '/break':
        bot.send_message(user_id, "Має бути принаймні один боржник.")
        bot.send_message(user_id, "Введіть ім'я щоб продовдити або '/cancel' для скасування")
        return
    if message.text == '/every':
        for i in group.id_lib:
            print(i, group.id_lib[i])
            if group.id_lib[i] not in incoming_debts[user_id][1].debtors:
                incoming_debts[user_id][1].debtors.append(group.id_lib[i])
    if message.text == '/break' or message.text == '/every':
        bot.send_message(user_id, "OK")
        state[user_id] = 'sum' + group_id
        bot.send_message(user_id, "Яка сума боргу?")
    elif debtor in group.id_lib:
        if debtor in incoming_debts[user_id][1].debtors:
            bot.send_message(user_id, "Цього боржника вже згадували, модливо ще хтось?")
        else:
            bot.send_message(user_id, "OK, ще хтось? (напишіть '/break' щоб закінчити перерахунок)")
            incoming_debts[user_id][1].debtors.append(group.id_lib[debtor])
    else:
        bot.send_message(user_id, "Ви вказали невірне ім'я, спробуйте ще раз")


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


@bot.message_handler(func=lambda message: (str(message.from_user.id) in reachable_users) and check_user_state(message, 'sum'), content_types=['text'])
def get_sum(message):
    user_id = str(message.from_user.id)
    group_id = state[user_id][3:]
    if not is_float(message.text):
        bot.send_message(user_id, "Необхідно ввести додатнє число, спробуйте ще раз")
        return
    debt_sum = float(message.text)
    if debt_sum <= 0:
        bot.send_message(user_id, "Необхідно ввести додатнє число, спробуйте ще раз")
        return
    incoming_debts[user_id][1].sum = debt_sum
    groups[group_id].debts.append(incoming_debts[user_id][1])
    bot.send_message(user_id, "OK")
    bot.send_message(group_id, "Вітаю з новою покупкою!")
    save_to_database(groups)
    state[user_id] = group_id


def print_all_debts(group_id, where_to=""):
    if where_to == "":
        where_to = group_id
    group = groups[group_id]
    text = 'Поточні борги:\n'
    for i in group.debts:
        text += debt_to_text(i, group_id) + '\n'
    bot.send_message(where_to, text)


def print_all_people(group_id, where_to=""):
    if where_to == "":
        where_to = group_id
    group = groups[group_id]
    text = 'Учасники групи:\n'
    for i in group.names_lib:
        text += group.names_lib[i] + '\n'
    bot.send_message(where_to, text)


def debt_to_text(debt, group_id):
    group = groups[group_id]
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
