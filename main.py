from emoji import EMOJI_DATA
from datetime import datetime, timedelta
from time import time, sleep


def menu(question: str,
         options: list[str | int],
         errortxt: str = "Input non valido!",
         selectiontxt: str = "Scrivi la tua scelta qui: ",
         use_index: bool = True,
         use_options: bool = True,
         return_index: bool = False) -> str | int:
    if not (use_index or use_options):
        raise ValueError("Please activate one of the two options to scan the response!")
    if not options:
        raise ValueError("Options list can't be empty!")
    options = [str(o).lower() for o in options]
    while True:
        print(question.capitalize())
        for n, a in enumerate(options):
            print(f'{n + 1}. {a.title()}' if use_index else a.title())
        option = input(selectiontxt).lower().strip()
        if use_index:
            try:
                tmp = int(option)
                if 1 <= tmp <= tmp + 1:
                    option = options[int(option) - 1]
                    if option in options:
                        break
            except ValueError:
                pass
            except IndexError:
                pass
        if (option in [o.lower() for o in options] or option in [o.capitalize() for o in options]) and use_options:
            break
        else:
            print(errortxt.capitalize() + '\n')
    print()
    if return_index:
        return options.index(option)
    else:
        return option


def iterinput(prompt: str, stop_val: str | list[str]):
    out = ""
    print(prompt, end = "")
    if type(stop_val) is not list:
        stop_val = [stop_val]
    while True:
        i = input()
        if i.strip() in stop_val:
            break
        out += f"{i}\n"
    return out


def check(txt):
    return txt[0:1].isdigit() and txt[2] == "/" and txt[16] == '-'


data_file: str = ''
file_name: str = ''
using_pc = bool(menu("Stai utilizzando un computer?", ["si", "no"], return_index = True)) ^ True
if using_pc:
    from tkinter.filedialog import askopenfilename
    import zipfile
    from shutil import rmtree
    import os
    filetypes: list[tuple[str, str | list[str] | tuple[str, ...]]] = [
        ("Whatsapp chats", ("*.txt", "*.zip"))
    ]
    now_path: str = os.path.dirname(os.path.realpath(__file__))
    temp_path: str = rf'{now_path}\temp'
    is_zip: bool = False

    while 1:
        filepath: str = askopenfilename(initialdir = now_path, filetypes = filetypes)

        if filepath.endswith(".txt"):
            file_name = filepath.split('/')[-1][:-4]

        elif filepath.endswith(".zip"):
            is_zip = True

            if os.path.exists(temp_path):
                rmtree(temp_path)
            os.makedirs(temp_path)

            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(temp_path)

            file_name = filepath.split('/')[-1][:-4]
            filepath = fr"{temp_path}\{file_name}.txt"

        else:
            raise IOError("The selection got stopped.")

        with open(filepath, 'r', encoding='utf-8') as file:
            data_file = file.readlines()

        if is_zip:
            if os.path.exists(temp_path):
                rmtree(temp_path)

        if check(data_file[0]):
            break
        else:
            print("File selezionato non risulta essere una chat Whatsapp, si prega di riprovare.\n")
            sleep(1)

    print(f"File selezionato: {filepath}\n")

elif not using_pc:
    while True:
        data_file = iterinput(
            "Incolla il contenuto del file di testo e poi inserisci \"continua\" per continuare:\n",
            ["Continua", "continua"]).splitlines(True)
        print()

        if check(data_file[0]):
            break
        else:
            print("File incollato non risulta essere una chat Whatsapp, si prega di riprovare.\n")
            sleep(1)

analysis_lvl = menu("Seleziona il tipo di analisi che vuoi eseguire:",
                    ["analisi superficiale", "analisi approfondita", "analisi completa"],
                    return_index = True) + 1


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


print(f"Analisi della chat WhatsApp {file_name[18:] if using_pc else ''}:\n")
it = time()

mlist: list[Message] = []

for line in data_file[:]:

    if len(list(line)) < 17:
        mlist[-1].append_text(line)
    elif not check(line):
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


tfgc: timedelta = datetime.now() - mlist[0].datetime
'''Time from group creation'''
mmpd: int = len(mlist) / tfgc.days
'''Median messages per day'''

textm: list[Message] = []
editedm: list[Message] = []
words: dict[str, int] = {}

if analysis_lvl >= 2:
    for m in mlist:
        if m.edited:
            editedm.append(m)
    textm = messagefilter(mlist)


if analysis_lvl >= 2:
    if analysis_lvl == 2:
        for m in messagefilter(mlist):
            for word in m.text.split():
                word = word.lower()
                if word == '':
                    continue
                elif word not in words:
                    words[word] = 1
                else:
                    words[word] += 1
    else:
        chars_to_remove: list[str] = (
                list('<>"*_-`<>?@,.=+!\'’;:{}[]()') +
                list(EMOJI_DATA.keys()) +
                [str(n) for n in range(10)]
        )

        def str_cleaner(string: str, chars: list[str]) -> str:
            return "".join([x for x in string if x not in chars])

        for m in messagefilter(mlist):
            for word in m.text.split():
                word = str_cleaner(word.lower(), chars_to_remove)
                if word == '':
                    continue
                elif word not in words:
                    words[word] = 1
                else:
                    words[word] += 1

dates1: list = [datetime.today().date()]
for m in reversed(mlist):
    date1 = m.datetime.date()
    if date1 not in dates1:
        dates1.append(date1)

streak = 0
for n, date1 in enumerate(dates1):
    try:
        if date1 - timedelta(1) == dates1[n+1]:
            streak += 1
        else:
            break
    except IndexError:
        break

print(f"Totale messaggi: {len(mlist)}")
print(f'Media messaggi per giorno: {mmpd if analysis_lvl <= 2 else f"{mmpd:0f}"}')

print(f'Data primo messaggio: {mlist[0].datetime} ({tfgc.days} giorni fa)\n')

if analysis_lvl >= 2:
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

if analysis_lvl >= 2:
    print("Parole piu usate (sopra i 3 caratteri):")
    words2 = {w : n for w, n in words.items() if len(list(w)) > 3}
    [print(f"    {word} : {n}") for word, n in dict(list(dict_sorter(words2).items())[:10]).items()]
    print()

    print("Parole piu usate (tutte):")
    [print(f"    {word} : {n}") for word, n in dict(list(dict_sorter(words).items())[:10]).items()]
    print()


print(f'Chat Streak: {streak} 🔥')
print(f"Durata analisi: {time() - it} secondi")