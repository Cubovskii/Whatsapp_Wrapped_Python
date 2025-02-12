from tkinter.filedialog import askopenfilename
import os
from emoji import EMOJI_DATA
from datetime import date, datetime, time
from time import time

filetypes = [
    ("Text files", "*.txt")
]

now_path = os.path.dirname(os.path.realpath(__file__))
filepath = askopenfilename(initialdir = now_path, filetypes = filetypes)
file_name = filepath.split('/')[-1][:-3]
print(f"Analisi della chat WhatsApp {file_name[18:-1]}")
it = time()

with open(filepath, 'r', encoding='utf-8') as file:
    data_file = file.readlines()


def askforinput(question: str, *, error_txt: str = 'Invalid input!', output_type=str,
                clear_spaces: bool = True, format_str: bool = False) -> str | int | float:
    while 1:
        i = str(input(question))

        if clear_spaces:
            i = i.lstrip().rstrip()

        try:
            i = float(i)
            if output_type == float:
                return i

            tmp = int(i)
            if tmp == i and output_type == int:
                return tmp

        except ValueError:
            pass
        if format_str:
            try:
                i = i.lower()
            except ValueError:
                pass
        if output_type == str:
            return str(i)

        print(error_txt, '\n')


class Message:
    def __init__(self, rawtxt: str):

        def divide_first_char(string: str, char: str):
            item1: str
            item2: str
            list1: str | list[str]

            item1, *list1 = string.split(char)
            try:
                item2 = char.join(list1)
            except AttributeError:
                item2 = list1
            return item1, item2

        dividing_char1 = ', '  # divides "part1" in "date" and "time"
        dividing_char2 = ' - '  # divides "the line" (rawtxt) in "part1" and "part2"
        dividing_char3 = ': '  # divides "part2" in "user" and "message"

        date_and_time, user_and_data = divide_first_char(rawtxt, dividing_char2)
        date1, time1 = divide_first_char(date_and_time, dividing_char1)
        user, text = divide_first_char(user_and_data, dividing_char3)
        text = text.rstrip('\n')

        minutes = int(time1.split(':')[1])
        hours = int(time1.split(':')[0])
        day = int(date1.split('/')[0])
        month = int(date1.split('/')[1])
        year = int(date1.split('/')[2]) + 2000

        self.date = date(year, month, day)
        self.time = time(hours, minutes)
        self.datetime = datetime(year, month, day, hours, minutes)

        self.user: str = user
        self.edited: bool = False

        if text.endswith("<Questo messaggio è stato modificato>"):
            self.edited = True
            text = text[:-37]

        if text == '' and self.user.endswith('\n'):
            self.type = 'sys'
            self.text = self.user
            self.user = '$system$'
        elif text == 'null':
            self.type = 'svm'
            self.text = '<Single-View message>'
        elif text == "<Il messaggio vocale visualizzabile una volta è stato omesso>":
            self.type = 'svvm'
            self.text = '<Single-View voice message>'
        elif text == "In attesa del messaggio":
            self.type = "error"
            self.text = text
        elif text == '<Media omessi>':
            self.type = 'media'
            self.text = '<Media omitted>'
        elif text == '<Video note omitted>':
            self.type = 'vnote'
            self.text = text
        elif text == "Hai eliminato questo messaggio." or text == "Questo messaggio è stato eliminato.":
            self.type = "del"
            self.text = "<Message deleted>"
        elif text == "SONDAGGIO:":
            self.type = 'poll'
            self.text = text
        elif text[:7] == "EVENTO:":
            self.type = 'event'
            self.text = text
        else:
            self.type = "txt"
            self.text = text

    def append_text(self, text: str) -> None:
        self.text = self.text + '\n' + text.rstrip('\n')
        if self.text != self.text.lstrip("<Questo messaggio è stato modificato>"):
            self.edited = True
            self.text = self.text.lstrip("<Questo messaggio è stato modificato>")

    def __str__(self) -> str:
        return fr'{self.datetime} | {self.user} | {self.type} | {self.text} | Edited: {self.edited}'


mlist: list[Message] = []

for line in data_file[:]:
    check = not line[0:1].isdigit()
    if len(list(line)) < 17:
        mlist[-1].append_text(line)
    elif check or line[2] != "/" or line[16] != '-':
        mlist[-1].append_text(line)
    else:
        mlist.append(Message(line))

users: dict[str, int] = {}
for m in mlist:
    if m.user not in users:
        users[m.user] = 1
    else:
        users[m.user] += 1


def dict_sorter(inputdict: dict):
    return {k : v for k, v in sorted(inputdict.items(), key = lambda item: item[1], reverse = True)}


def messagefilter(inputlist: list[Message], keytype: str = 'txt', count: bool = False) -> list[Message] | int:
    output: list[Message] = []
    for m in inputlist:
        if m.type == keytype:
            output.append(m)
    if count:
        return len(output)
    else:
        return output

editedm: list[Message] = []
for m in mlist:
    if m.edited:
        editedm.append(m)
textm: list[Message] = messagefilter(mlist)


def str_cleaner(string: str, chars: list[str]) -> str:
    return "".join([x for x in string if x not in chars])


words: dict[str, int] = {}
chars_to_remove: list[str] = (
    list('<>"*_-`<>?@,.=+!\'’;:{}[]()') +
    list(EMOJI_DATA.keys()) +
    [str(n) for n in range(10)]
)

for m in messagefilter(mlist):
    for word in m.text.split():
        word = str_cleaner(word.lower(), chars_to_remove)
        if word == '':
            continue
        elif word not in words:
            words[word] = 1
        else:
            words[word] += 1


print(f"Totale messaggi: {len(mlist)}")
print(f'Media messaggi: {'placeholder'}') #####################################
print(f'Data primo messaggio: {mlist[0].datetime}')

print(f'Messaggi testuali: {len(textm)}')
print(f'Messaggi modificati: {len(editedm)}')
print(f'File multimediali: {messagefilter(mlist, 'media', True)}')
print(f'Messaggi eliminati: {messagefilter(mlist, 'del', True)}')
print(f'Messaggi a un unica visualizzazione: {messagefilter(mlist, 'svm', True)}')
print(f"Vocali a una solo visualizzazione: {messagefilter(mlist, 'svvm', True)}")
print(f"Sondaggi: {messagefilter(mlist, 'poll', True)}")
print(f"Eventi: {messagefilter(mlist, 'event', True)}")
print(f"Sconosciuto: {messagefilter(mlist, 'error', True)}")
print(f'Messaggi di sistema: {messagefilter(mlist, 'sys', True)}')
print()

print("Messaggi per utente:")
[print('   ', k, ':', v) for k, v in dict_sorter(users).items() if k != '$system$']
print()

print("Parole piu usate (sopra i 3 caratteri):")
words2 = {w : n for w, n in words.items() if len(list(w)) > 3}
[print(f"    {word} : {n}") for word, n in dict(list(dict_sorter(words2).items())[:10]).items()]
print()

print("Parole piu usate (tutte):")
[print(f"    {word} : {n}") for word, n in dict(list(dict_sorter(words).items())[:10]).items()]

print(f"Tempo necessario per l'analisi: {time() - it}")
while 1:
    r = int(input()) - 1

    print(f'Index: {r} \n{mlist[r]}')