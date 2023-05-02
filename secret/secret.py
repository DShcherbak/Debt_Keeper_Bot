import csv 


secret = ""

with open('secret/secret.config', newline='', encoding='utf-8') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"', lineterminator='\n')
    secret = spamreader.__next__()[0]