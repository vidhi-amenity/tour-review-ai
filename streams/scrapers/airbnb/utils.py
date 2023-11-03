from datetime import datetime
import re

def clean_date(str_date):
    try:
        # return datetime.date.today()
        return datetime.strptime(str_date, '%B %Y')
    except:
        return datetime.date.today().replace(day=1)


def remove_emoji(text):
    # filtrare gli emoji non supportati
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticon
        u"\U0001F300-\U0001F5FF"  # simboli & pictogram
        u"\U0001F680-\U0001F6FF"  # trasporti & simboli
        u"\U0001F1E0-\U0001F1FF"  # bandiere (Unicode 6.0)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)