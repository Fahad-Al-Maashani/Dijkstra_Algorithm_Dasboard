"""
Currency conversion utilities for multi-currency support
"""

from typing import Dict, Optional
from datetime import datetime


class CurrencyConverter:
    """Handle currency conversions for tax calculations"""

    # Exchange rates to OMR (approximate rates)
    EXCHANGE_RATES = {
        'USD': 0.3854,  # 1 USD = 0.3854 OMR
        'EUR': 0.4214,  # 1 EUR = 0.4214 OMR
        'GBP': 0.4897,  # 1 GBP = 0.4897 OMR
        'AED': 0.1049,  # 1 AED = 0.1049 OMR
        'SAR': 0.1028,  # 1 SAR = 0.1028 OMR
        'KWD': 1.2641,  # 1 KWD = 1.2641 OMR
        'BHD': 1.0204,  # 1 BHD = 1.0204 OMR
        'QAR': 0.1058,  # 1 QAR = 0.1058 OMR
        'OMR': 1.0000   # Base currency
    }

    @classmethod
    def convert_to_omr(cls, amount: float, from_currency: str) -> float:
        """Convert amount from specified currency to OMR"""
        if from_currency not in cls.EXCHANGE_RATES:
            raise ValueError(f"Unsupported currency: {from_currency}")

        rate = cls.EXCHANGE_RATES[from_currency]
        return amount * rate

    @classmethod
    def convert_from_omr(cls, amount: float, to_currency: str) -> float:
        """Convert amount from OMR to specified currency"""
        if to_currency not in cls.EXCHANGE_RATES:
            raise ValueError(f"Unsupported currency: {to_currency}")

        rate = cls.EXCHANGE_RATES[to_currency]
        return amount / rate

    @classmethod
    def get_supported_currencies(cls) -> list:
        """Get list of supported currencies"""
        return list(cls.EXCHANGE_RATES.keys())

    @classmethod
    def format_currency(cls, amount: float, currency: str) -> str:
        """Format amount with currency symbol"""
        symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'AED': 'AED',
            'SAR': 'SAR',
            'KWD': 'KWD',
            'BHD': 'BHD',
            'QAR': 'QAR',
            'OMR': 'OMR'
        }

        symbol = symbols.get(currency, currency)
        return f"{symbol} {amount:,.2f}"