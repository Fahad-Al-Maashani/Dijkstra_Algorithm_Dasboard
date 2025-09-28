"""
Date utility functions for the tax calculator
"""

from datetime import datetime, date
from typing import Optional


def get_current_tax_year() -> int:
    """Get the current tax year"""
    return datetime.now().year


def format_date_display(date_obj: date) -> str:
    """Format date for display in UI"""
    return date_obj.strftime('%Y-%m-%d')


def is_tax_year_effective(year: int) -> bool:
    """Check if tax law is effective for given year"""
    return year >= 2028


def get_tax_year_start_date(year: int) -> date:
    """Get the start date of a tax year"""
    return date(year, 1, 1)


def get_tax_year_end_date(year: int) -> date:
    """Get the end date of a tax year"""
    return date(year, 12, 31)


def calculate_days_in_tax_year(year: int) -> int:
    """Calculate number of days in tax year"""
    start = get_tax_year_start_date(year)
    end = get_tax_year_end_date(year)
    return (end - start).days + 1


def format_timestamp() -> str:
    """Get formatted timestamp for logging"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

