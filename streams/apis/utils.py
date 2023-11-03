import re
from datetime import datetime
import emoji

# def clean_review(string):
#     if string:
#         emoji_pattern = re.compile("["
#             u"\U0001F600-\U0001F64F"  # emoticon
#             u"\U0001F300-\U0001F5FF"  # simboli & pictogram
#             u"\U0001F680-\U0001F6FF"  # trasporti & simboli
#             u"\U0001F1E0-\U0001F1FF"  # bandiere (Unicode 6.0)
#             u"\U00002702-\U000027B0"
#             u"\U000024C2-\U0001F251"
#             "]+", flags=re.UNICODE)
#         return emoji_pattern.sub(r'', string)
#     return None


def clean_review(string):
    if string:
        string = emoji.demojize(string)
        string = re.sub(r':[a-zA-Z_]+:', '', string)
        return string
    return None



def clean_date(string):
    return datetime.strptime(string, '%Y-%m-%dT%H:%M:%S%z')