from datetime import datetime, timedelta
from collections import deque
from typing import Union
import os, json, dotenv, pymorphy2, re, random as rnd, logging, sys

morph = pymorphy2.MorphAnalyzer()

if os.path.isfile('.env'):
    dotenv.load_dotenv()
elif os.path.isfile('../.env'):
    dotenv.load_dotenv('../.env')

token = os.environ['TOKEN']
db_url = os.environ['DATABASE_URL'].replace('postgres', 'postgresql')
local_debug = os.environ.get('DEBUG', 0) == '1'

punctuation = '“”„«».,~!@#$%^&*()_+-=`\'";:<>[]{}/\\|№ \n'
free_punctuation = '“”„«».,~!@#$%^&*()+=`\'";:<>[]{}/\\|№'


def getInd(text, substring):
    return 0 if substring not in text else text.index(substring)


def clean_text(text):
    return text.replace('<', '&lt;').replace('>', '&rt;').replace('&', '&amp;')


def split(text: str):
    tags = re.findall(r'<[^<>]+>', text)
    texts = []
    if len(tags) == 0:
        texts.append([text, 'default'])
    else:
        pos = getInd(text, tags[0])
        if pos > 0:
            texts.append([text[:pos], 'default'])
        text = text[pos:]
    q = deque()
    for i in range(len(tags)):
        if len(tags[i]):
            tagName = re.findall(r'</?(\w+).*>', tags[i])
            if not tagName: continue
            tagName = tagName[0]
            closing = re.fullmatch(r'</.+>', tags[i])
            if not closing:
                if len(q) == 0:
                    texts.append([tags[i], 'tagged'])
                else:
                    texts[-1][0] += tags[i]
                q.append(tagName)
            else:
                if len(q) == 0:
                    texts.append([tags[i], 'tagged'])
                else:
                    texts[-1][0] += tags[i]
                q.pop()
            text = text[len(tags[i]):]
        pos = getInd(text, tags[i + 1]) if i + 1 < len(tags) else len(text)
        if text[:pos]:
            if len(q):
                texts[-1][0] += text[:pos]
            else:
                texts.append([text[:pos], 'default'])
        text = text[pos:]
    res = []
    for text in texts:
        if text[1] == 'tagged':
            res.append(text[0])
        else:
            words = [word if i == 0 else f" {word}" for i, word in enumerate(text[0].split(' '))]
            res.extend(words)
    return res


def split_msg(msg: str, max_len=4096):
    texts = split(msg)
    res = [texts[0]]
    for i in range(1, len(texts)):
        text = texts[i]
        if len(res[-1] + text) < max_len:
            res[-1] += text
        else:
            res.append(text)
    return res


def load_json(name):
    name += '.json'
    if os.path.isfile(f'data/{name}'):
        with open(f'data/{name}', 'r', encoding='utf-8') as file:
            return json.load(file)
    elif os.path.isfile(f'../data/{name}'):
        with open(f'../data/{name}', 'r', encoding='utf-8') as file:
            return json.load(file)
    elif os.path.isfile(f'../../data/{name}'):
        with open(f'../../data/{name}', 'r', encoding='utf-8') as file:
            return json.load(file)
    print(f"{name} not found. Loaded None")
    return None


templates = load_json('templates')
dictionary = load_json('dictionary')
TAG_RE = re.compile(r'<[^>]+>')


def remove_chars(text, chars):
    pattern = f"[{'|'.join(chars)}]"
    return re.sub(pattern, '', text)


def dump(string: Union[dict, list]) -> str:
    return json.dumps(string, ensure_ascii=False)


def strftime(time: datetime, type='full') -> str:
    if type == 'time':
        return time.strftime("%H:%M")
    if type == 'full':
        return time.strftime("%d.%m.%Y %H:%M")
    return time.strftime("%d.%m.%Y")


def strptime(time: str, type='full') -> datetime:
    if type == 'full':
        return datetime.strptime(time, "%d.%m.%Y %H:%M")
    return datetime.strptime(time, "%d.%m.%Y")


def get_num() -> int:
    return rnd.randint(0, 2 ** 31 - 1)


def remove_space(text):
    return re.sub(r' +', ' ', text)


def remove_tags(text):
    return TAG_RE.sub(r'', text)


def now():
    return datetime.now()


def today():
    time_now = now()
    return datetime(time_now.year, time_now.month, time_now.day)


def unix(time: datetime):
    return (time - datetime(1970, 1, 1)).total_seconds()


def decline_word(word, num, with_num=False) -> str:
    if word in dictionary:
        type = 1
        if abs(num) == 1: type = 0
        if 10 <= abs(num) <= 14 or 5 <= abs(num) % 5 or num == 0: type = 2
        word = dictionary[word][type]
    else:
        word = morph.parse(word)[0].make_agree_with_number(num).word
    if with_num:
        return f"{num} {word}"
    return word


seconds_to_time = {'с': {"seconds": 1, "max": 60}, 'м': {"seconds": 60, "max": 60},
                   'ч': {"seconds": 3600, "max": 24}, 'д': {"seconds": 86400, "max": 100000}}
time_order = ['д', 'ч', 'м', 'с']


def seconds_to_text(seconds, full=False, default='чуть-чуть'):
    seconds = int(round(seconds))
    if seconds <= 0:
        return default
    times = {}
    max_time = -1
    for name, time_info in seconds_to_time.items():
        times[name] = (seconds // time_info['seconds']) % time_info['max']
        if times[name] > 0:
            max_time = name
    if max_time == 0:
        return default
    if not full:
        return f"{times[max_time]}{max_time}."
    text = " ".join([f"{times[name]}{name}." for name in time_order if times[name] > 0])
    return text
