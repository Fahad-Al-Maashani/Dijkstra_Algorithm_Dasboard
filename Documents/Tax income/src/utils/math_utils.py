"""Mathematical utility functions"""

def round_currency(amount: float) -> float:
    """Round amount to 2 decimal places"""
    return round(amount, 2)

def calculate_percentage(amount: float, rate: float) -> float:
    """Calculate percentage of amount"""
    return amount * rate

def format_number(number: float) -> str:
    """Format number with commas"""
    return f'{number:,.2f}'

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(value, max_val))
