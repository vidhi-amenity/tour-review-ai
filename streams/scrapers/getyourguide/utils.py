from dateutil import parser


def clean_date(str_date):
    try:
        return parser.parse(str_date, fuzzy=True)
    except:
        return None


def clean_id(string):
    if string:
        return string.lower().replace("booking:", "").replace(" ", "")

    return None
