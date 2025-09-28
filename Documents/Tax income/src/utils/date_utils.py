from datetime import datetime

def get_current_tax_year():
    return datetime.now().year

def format_date_display(date):
    return date.strftime('%Y-%m-%d')

def is_tax_year_effective(year):
    return year >= 2028

