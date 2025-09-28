"""
Input validation utilities for tax calculator
"""

import re
from typing import Union, Tuple


class InputValidator:
    """Validates user input for tax calculations"""

    @staticmethod
    def validate_currency(value: str) -> Tuple[bool, float]:
        """
        Validate currency input

        Returns:
            Tuple[bool, float]: (is_valid, validated_value)
        """
        if not value or value.strip() == "":
            return True, 0.0

        # Remove common currency symbols and whitespace
        cleaned = re.sub(r'[OMR\s,]', '', value.strip())

        try:
            amount = float(cleaned)
            if amount < 0:
                return False, 0.0
            return True, amount
        except ValueError:
            return False, 0.0

    @staticmethod
    def validate_positive_number(value: str) -> Tuple[bool, float]:
        """
        Validate positive number input

        Returns:
            Tuple[bool, float]: (is_valid, validated_value)
        """
        try:
            num = float(value.strip())
            return num >= 0, max(0, num)
        except (ValueError, AttributeError):
            return False, 0.0

    @staticmethod
    def format_currency(amount: float) -> str:
        """Format amount as currency string"""
        return f"OMR {amount:,.2f}"

    @staticmethod
    def format_percentage(rate: float) -> str:
        """Format rate as percentage string"""
        return f"{rate * 100:.1f}%"