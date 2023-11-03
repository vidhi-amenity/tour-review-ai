from dateutil import parser
import re
import emoji
import hashlib
from datetime import datetime


def clean_date(str_date):
    try:

        parsed_date = parser.parse(str_date, fuzzy=True)

        # Ottieni la data odierna
        today = datetime.now()

        # Se il mese e l'anno della data analizzata sono uguali a quelli di oggi, ritorna la data così com'è
        if parsed_date.month == today.month and parsed_date.year == today.year:
            return parsed_date
        else:
            # Altrimenti, ritorna il primo giorno del mese della data analizzata
            return parsed_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        parsed_date = parser.parse(str_date, fuzzy=True)
        return parsed_date.replace(day=1)


    except:
        return None


def clean_id(string):
    if string:
        return string.split('-')[1]

    return None

def clean_rating(string):
    if string:
        return string.split('_')[-1][0]

    return None

def remove_emoji(text):
    if text:
        string = emoji.demojize(text)
        string = re.sub(r':[a-zA-Z_]+:', '', string)
        return string
    return None

def generate_id(text):
    hash_object = hashlib.sha256(text.encode())
    return hash_object.hexdigest()[:20]

def replace_domain_extension(url, new_extension='.com'):
    return re.sub(r'(https://www\.tripadvisor)\.\w{2,3}', r'\1' + new_extension, url)
