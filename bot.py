import telebot
from database import *
from Group import Debt, Group

bot = telebot.TeleBot('1054698181:AAEmAqgJ_pc6P7Hbd6XWN2Bb-MJzxS4os1U')
group = Group()
reachable_users = []
groups = {}
state = ''


#TODO -list:
    #TODO: refactoring: wanna separate group and personal speaking into different files
    #TODO: state-variable: must be personalized for each user, so they can use bot on the same time
    #TODO: need to take float-arguments when reading someone's debt
    #TODO: need to figure out a way to approve new debt-system and to cancel-out debts


@bot.message_handler(commands=['start'])
def send_welcome(message):
    global reachable_users, group, groups
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
        print_all_people()
        #bot.send_message(group.id, text=str(type(group.id_lib) + group.id_lib['Den']))

    else:
        bot.send_message(message.chat.id, text='Всім привіт! Я - Debt Keeper Bot, радий знайомству!')
        bot.send_message(message.chat.id, text='Раджу всім додатися в список юзерів, щоб я міг надавати вам свої послуги.')
        bot.send_message(message.chat.id, text='Для цього напишіть команду /add та дотримуйтеся інструкцій.')
        group.id = str(message.chat.id)
        group.names_lib = {}
        group.id_lib = {}
        groups.update([(group_id, group)])
        save_to_database(groups)
        

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.from_user.id, "В кого проблеми? Давайте розбиратися")


@bot.message_handler(func=lambda call: state == '', commands=['add'])
def new_user_welcome(message):
    global state, reachable_users, group
    user_id = str(message.from_user.id)
    if user_id not in reachable_users:
        bot.send_message(group.id, 'Я не маю права починати діалог з користувачем')
        bot.send_message(group.id, 'Будь ласка, напишіть мені в лс, щоб я міг додати вас')
    else:
        if user_id in group.names_lib:
            bot.send_message(group.id, 'Я вже вас знаю, ' + group.names_lib[user_id])
            bot.send_message(group.id, 'Якщо бажаєте змінити свій нік, напишіть /rename')
            return
        else:

            state = 'get name'
            bot.send_message(user_id, "Як вас звати?")


@bot.message_handler(func=lambda call: state != '', commands=['add'])
def busy(message):
    bot.send_message(message.chat.id, 'Вибачте, я зараз спілкуюся з іншим користувачем, спробуйте пізніше')


@bot.message_handler(commands=['list'])
def listing(message):
    print_all_people()


@bot.message_handler(commands=['all'])
def listing(message):
    print_all_debts()


def print_all_debts():
    for i in group.debts:
        bot.send_message(group.id, debt_to_text(i))


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


@bot.message_handler(commands=['resolve'])
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
        sum_val = debt.sum/len(debt.debtors)
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
    n = len(plus_money)-1
    m = len(minus_money)-1
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
        if n > 0 and plus_money[n-1][0] > minus_money[m][0]:
            move(plus_money)
        elif n >= 0 and m >= 0:
            solution.append((minus_money[m][1], plus_money[n][1], plus_money[n][0]))
            minus_money[m] = (minus_money[m][0] - plus_money[n][0], minus_money[m][1])
            #minus_money[m][0] -= plus_money[n][0]
            del plus_money[n]
            n -= 1

    bot.send_message(group.id, "Here's my solution")
    for s in solution:
        bot.send_message(group.id, group.names_lib[s[0]] + " -> " + group.names_lib[s[1]] + " : " + str(s[2]))

    print(solution)


@bot.message_handler(func=lambda call: state == 'get name')
def get_name(message):
    global group, state
    user_id = str(message.from_user.id)
    bot.send_message(user_id, 'Приємно познайомитися, ' + message.text + '!')
    group.add_user(user_id, message.text)
    list_users(group)

    groups[group.id].renew(group)
    save_to_database(groups)
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
        add_new_debt(call.from_user.id)
        result = 'Вітаю з новою покупкою!'
    else:
        result = 'От список поточних боргів:'
        print_all_debts()
    bot.send_message(group.id, result)


def add_new_debt(user_id):
    global group, state
    group.current_debt_id += 1
    new_debt = Debt()
    group.debts.append(new_debt)
    bot.send_message(user_id, text='Хто платив?')
    state = 'payer'


@bot.message_handler(func=lambda call: state == 'payer', content_types=['text'])
def get_text_messages(message):
    global group, state
    user_id = message.from_user.id
    if message.text == '/cancel':
        group.debts.pop_back()
        group.current_debt_id -= 1
        state = ''
        return
    if message.text in group.id_lib:
        bot.send_message(user_id, "OK")
        curr_debt_id = group.current_debt_id-1
        print(curr_debt_id, len(group.debts))
        group.debts[curr_debt_id].payer = group.id_lib[message.text]
        state = 'debtors'
        group.debts[curr_debt_id].debtors = []
        bot.send_message(user_id, text='За кого платили?')
        bot.send_message(user_id, "(напишіть '/every' щоб додати всіх з чату)")
    else:
        bot.send_message(user_id, "Ви вказали невірне ім'я, спробуйте ще раз")


@bot.message_handler(func=lambda call: state == 'debtors', content_types=['text'])
def get_debtors(message):
    global group, state
    user_id = message.from_user.id
    debtor = message.text
    cur_debt_id = group.current_debt_id-1

    if message.text == '/cancel':
        bot.send_message(user_id, "Відміна!")
        group.debts.pop()
        group.current_debt_id -= 1
        state = ''
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
    print(debt_to_text(group.debts[cur_debt_id]))
    groups[group.id].renew(group)
    save_to_database(groups)
    state = ''


@bot.message_handler(func=lambda call: state == 'confirm', content_types=['text'])
def get_confirmation(message):
    bot.send_message(message.from_user.id, "Все вірно?")


@bot.message_handler(func=lambda call: state == '', content_types=['text', 'private'] )
def get_text_messages(message):
    global reachable_users
    user_id = str(message.from_user.id)
    if user_id not in reachable_users:
        reachable_users.append(user_id)
    remember_users(reachable_users)
    if message.text == "Привіт":
        bot.send_message(user_id, "Привіт, дякую що написав!")
    else:
        bot.send_message(user_id, "Що ще нового?")


def require_confirm(str_result, user_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_y = telebot.types.InlineKeyboardButton(text='Так', callback_data='Y')
    key_n = telebot.types.InlineKeyboardButton(text='Ні', callback_data='N')
    keyboard.add(key_y)
    keyboard.add(key_n)
    question = 'Все вірно?'
    state = 'confirm'
    bot.send_message(user_id, text=str_result)
    bot.send_message(user_id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: state == 'confirm')
def get_confirm(call):
    global state
    if call.data== 'N':
        group.debts.pop_back()
        group.current_debt_id -= 1
        state = ''
        return
    text = 'New debt : ' + debt_to_text(group.debts[group.current_debt_id-1])
    bot.send_message(call.from_user.id, call.data)



bot.polling(none_stop=True, interval=0)
