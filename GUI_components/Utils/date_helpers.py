# Utils/date_helpers.py
from datetime import datetime

def validate_date_format(date_string):
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        return None

