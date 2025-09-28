"""
Tax data models and constants for Oman tax system
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class TaxBracket:
    """Represents a tax bracket"""
    min_income: float
    max_income: float
    rate: float
    threshold_deduction: float = 0.0


@dataclass
class DeductionCategory:
    """Represents a deduction category"""
    name: str
    description: str
    max_amount: float = float('inf')
    percentage_limit: float = 1.0


class OmanTaxData:
    """Contains Oman tax system data and constants"""

    # Tax year when the law becomes effective
    EFFECTIVE_YEAR = 2028

    # Current tax structure (2025 law)
    TAX_THRESHOLD = 42000.0  # OMR
    TAX_RATE = 0.05  # 5%

    # Deduction categories
    DEDUCTION_CATEGORIES = {
        'education': DeductionCategory(
            name='Education',
            description='Educational expenses for taxpayer and dependents',
            max_amount=5000.0  # Example limit
        ),
        'medical': DeductionCategory(
            name='Medical',
            description='Medical expenses not covered by insurance',
            max_amount=3000.0  # Example limit
        ),
        'zakat': DeductionCategory(
            name='Zakat',
            description='Charitable donations and zakat payments',
            percentage_limit=0.10  # 10% of income limit
        ),
        'housing': DeductionCategory(
            name='Housing',
            description='Housing loan interest and rental expenses',
            max_amount=8000.0  # Example limit
        )
    }

    # Exempt income types
    EXEMPT_INCOME_TYPES = [
        'Gain on sale of main residence',
        'Foreign salary (for certain categories)',
        'Inheritance',
        'Income from sale of secondary residence (one-time)',
        'Gifts',
        'Life insurance proceeds',
        'Compensation for personal injury'
    ]

    @classmethod
    def get_tax_info(cls) -> Dict:
        """Get complete tax system information"""
        return {
            'effective_year': cls.EFFECTIVE_YEAR,
            'threshold': cls.TAX_THRESHOLD,
            'rate': cls.TAX_RATE,
            'deduction_categories': cls.DEDUCTION_CATEGORIES,
            'exempt_income_types': cls.EXEMPT_INCOME_TYPES
        }

    @classmethod
    def is_tax_effective(cls, year: int = None) -> bool:
        """Check if tax law is effective for given year"""
        if year is None:
            year = datetime.now().year
        return year >= cls.EFFECTIVE_YEAR

    @classmethod
    def get_deduction_limit(cls, category: str, annual_income: float) -> float:
        """Get deduction limit for a category"""
        if category not in cls.DEDUCTION_CATEGORIES:
            return 0.0

        cat_info = cls.DEDUCTION_CATEGORIES[category]

        # Check percentage limit
        percentage_limit = annual_income * cat_info.percentage_limit

        # Return the minimum of max_amount and percentage limit
        return min(cat_info.max_amount, percentage_limit)