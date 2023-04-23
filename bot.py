import telebot
from database import (remember_users, read_from_database,
                      get_users, save_to_database)
from lang import load_lang, lang, LangCode
from Group import Debt, Group
from state.state import *
from utils import *


bot = telebot.TeleBot('1054698181:AAEmAqgJ_pc6P7Hbd6XWN2Bb-MJzxS4os1U')

state = State()


#######################

# Private chat functions

#######################


@bot.message_handler(func=is_private, commands=['start'])
def send_hello(message):
    user_id = message.from_user.id
    bot.send_message(user_id, lang(LangCode.Hello))
    bot.send_message(user_id, lang(LangCode.Greet))
    state.reach_user(user_id)
    save_to_database(state)


@bot.message_handler(func=is_private, commands=['help'])
def personal_help(message):
    bot.send_message(message.from_user.id, lang(LangCode.PersonalHelp))


@bot.message_handler(func=is_private, commands=['cancel'])
def cancel(message):
    bot.send_message(message.from_user.id, lang(LangCode.Cancel))


#######################

# Group chat functions

#######################


@bot.message_handler(func=is_group, commands=['start'])
def send_welcome(message):
    group_id = str(message.chat.id)

    if group_id in state.groups:
        bot.send_message(group_id, lang(LangCode.WelcomeBack))
        list_people(group_id)
    else:
        bot.send_message(group_id, lang(LangCode.GroupGreet))
        state.add_group(Group(group_id))
        save_to_database(state)


@bot.message_handler(func=is_group, commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, lang(LangCode.GroupHelp))


@bot.message_handler(func=is_group, commands=['people'])
def list_people(message):
    text = lang(LangCode.UserList)
    for user in state.groups[str(message.chat.id)].users:
        text += user.name + '\n'
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=is_group, commands=['debts'])
def list_debts(message):
    text = lang(LangCode.TransactionList)
    debt_list = state.get_all_debts()
    bot.send_message(message.chat.id, text + debt_list)


@bot.message_handler(func=is_group, commands=['resolve'])
def resolve(message):
    group_id = str(message.chat.id)
    result = state.resolve(group_id)
    if len(result) == 0:
        bot.send_message(group_id, lang(LangCode.ResolveSuccess))
        return 
    
    pretty_result = pretty_debts(result)
    bot.send_message(group_id, format(lang(LangCode.Solution),
                                       pretty_result))
    print(pretty_result)


@bot.message_handler(func=is_group, commands=['settle'])
def settle(message):
    group_id = str(message.chat.id)
    state.settle(group_id)
    save_to_database(state)
    bot.send_message(group_id, lang(LangCode.AllClear))


#######################

# Adding user to group

#######################


@bot.message_handler(func=is_group, commands=['add'])
def new_user_welcome(message):
    (user_id, group_id) = parse_message(message)

    if not state.is_reachable(user_id)
        print(user_id, " not reachable ")
        bot.send_message(group_id, lang(LangCode.CantWriteFirst))
        return
    
    user_name = state.get_name(group_id, user_id)
    
    if user_id in state.groups[group_id].users:
        bot.send_message(group_id, format(lang(LangCode.ChangeName),
                                            user_name))
    else:
        state.add_user(group_id, user_id, "")
        bot.send_message(user_id, lang(LangCode.GetName))
    state.set_user_state(group_id, user_id, UserState.GetName)



@bot.message_handler(func=check_user_state(UserState.GetName))
def get_name(message):
    (user_id, group_id) = parse_message(message)
    user_name = message.text
    bot.send_message(user_id, format(lang(LangCode.NiceToMeet), user_name))
    state.groups[group_id].users[user_id].name = user_name
    save_to_database(state)


#######################

# New debt in group

#######################


@bot.message_handler(commands=['debt'])
def get_command(message):
    (user_id, group_id, user) = parse_group_message(message)
    user.set_state(UserState.Debt)

    keyboard = telebot.types.InlineKeyboardMarkup()
    key_new_debt = telebot.types.InlineKeyboardButton(text=lang(LangCode.NewDebt), callback_data='NewDebt')
    key_list = telebot.types.InlineKeyboardButton(text=lang(LangCode.DebtList), callback_data='DebtList')
    keyboard.add(key_new_debt)
    keyboard.add(key_list)

    bot.send_message(group_id, text=lang(LangCode.DebtList), reply_markup=keyboard)


@bot.callback_query_handler(func=check_user_state(UserState.Debt))
def form(call):
    (user_id, group_id, user) = parse_group_message(call)
    if call.data == 'NewDebt':
        bot.send_message(user_id, text=lang(LangCode.WhoPayed))
        user.set_state(UserState.Payer)
    elif call.data == 'DebtList':
        text = lang(LangCode.TransactionList)
        debt_list = state.get_all_debts()
        user.set_state(UserState.Payer)    
        bot.send_message(group_id, text + debt_list)


@bot.message_handler(func=check_user_state(UserState.Payer), content_types=['text'])
def get_text_messages(message):

    (user_id, group_id, user) = parse_group_message(message)
    (name, payer_id) = parse_user(message, group_id)

    if message.text == '/cancel':
        state.set_user_state(group_id, user_id, UserState.Default)
        return
    
    if not payer_id:
        bot.send_message(user_id, lang(LangCode.WrongName))
        return
    
    bot.send_message(user_id, lang(LangCode.OK))
    user.new_debt.payer = payer_id
    user.set_state(UserState.Debtors)
    bot.send_message(user_id, text=lang(LangCode.Debtors))
    


@bot.message_handler(func=check_user_state(UserState.Debtors), content_types=['text'])
def get_debtors(message):

    (user_id, group_id, user) = parse_group_message(message)
    (debtor_name, debtor_id) = parse_user(message, group_id)

    if message.text == '/cancel':
        bot.send_message(group_id, lang(LangCode.Cancel))
        user.set_state(UserState.Default)
        return

    if user.new_debt.debtors == [] and message.text == '/break':
        bot.send_message(user_id, lang(LangCode.AtLeastOne))
        return
    
    if message.text == '/every':
        user.new_debt.debtors = [x.id for x in state.groups[group_id].users if x.id != user_id]
        
    if message.text == '/break' or message.text == '/every':
        user.set_state(UserState.Sum)
        bot.send_message(user_id, lang(LangCode.OK))
        bot.send_message(user_id, lang(LangCode.Sum))
        return 
    
    if not debtor_id:
        bot.send_message(user_id, lang(LangCode.WrongName))
        return 
    
    if debtor_id in user.new_debt.debtors:
        bot.send_message(user_id, lang(LangCode.RepeatedName))
    else:
        user.new_debt.debtors.append(debtor_id)
        bot.send_message(user_id, lang(LangCode.AnyoneElse))
 

@bot.message_handler(func=check_user_state(UserState.Sum), content_types=['text'])
def get_sum(message):
    (user_id, group_id, user) = parse_group_message(message)

    debt_sum = parse_float(message.text)
    if debt_sum <= 0:
        bot.send_message(user_id, lang(LangCode.PositiveNum))
        return
    
    user.new_debt.sum = debt_sum
    state.add_debt(group_id, user.new_debt)
    user.set_state(UserState.Default)
    save_to_database(state)

    bot.send_message(user_id, lang(LangCode.OK))
    bot.send_message(group_id, lang(LangCode.TransactionAdded))


#######################

# Main

#######################


if __name__ == "__main__":
    load_lang()
    state = get_state()
    bot.polling(none_stop=True, interval=0)
