import csv
from enum import Enum

dictionary = {}

class Lang(Enum):
    UKR = 1

current_language = Lang.UKR


class LangCode(Enum):
    Hello = 1
    Greet = 2
    PersonalHelp = 3
    GroupGreet = 4
    WelcomeBack = 5
    GroupHelp = 6
    CantWriteFirst = 7
    ChangeName = 8
    GetName = 9
    Cancel = 10
    Solution = 11
    AllClear= 12
    NiceToMeet =13
    ResolveSuccess = 14
    NewDebt = 15
    DebtList = 16
    DebtQuestion = 17
    UserList = 18
    TransactionList = 19
    WhoPayed = 20
    WrongName = 21
    Debtors = 22
    AtLeastOne = 23
    OK = 24
    Sum = 25
    RepeatedName = 26
    AnyoneElse = 27
    PositiveNum = 28
    TransactionAdded = 29
    StartFirst = 30


def lang(code):
    return dictionary[current_language][code]


def lang_format(code, *args):
    return format(lang(code), args)


def load_lang():
    with open('lang/lang.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"', lineterminator='\n')
        lang_names = spamreader.__next__()
        for lang_name in lang_names:
            dictionary[lang_name] = {}
        j = 1
        for row in spamreader:
            for i in range(len(lang_names)):
                dictionary[lang_names[i]][LangCode(j)] = row[i]
            j += 1
    #  print(dictionary)
    #  print(dictionary[Lang.UKR])
