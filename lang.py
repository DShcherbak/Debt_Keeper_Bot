import csv
from enum import Enum

dictionary = {}
current_language = "UKR"


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


def lang(code):
    return dictionary[current_language][code]


def lang_format(code, *args):
    return format(lang(code), args)


def load_lang():
    with open('lang.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"', lineterminator='\n')
        lang_names = spamreader.__next__()
        for lang_name in lang_names:
            dictionary[lang_name] = {}
        j = 1
        for row in spamreader:
            for i in range(len(lang_names)):
                dictionary[lang_names[i]][LangCode(j)] = row[i]
            j += 1
    print(dictionary)
    print(dictionary["UKR"])
