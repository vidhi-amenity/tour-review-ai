from datetime import datetime

def clean_date(str_date):
    try:
        return datetime.strptime(str_date, "%d/%m/%Y")
    except:
        return None