"""
Taxpayer model for storing individual tax information
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
from enum import Enum


class ResidencyStatus(Enum):
    """Taxpayer residency status"""
    RESIDENT = "resident"
    NON_RESIDENT_CITIZEN = "non_resident_citizen"
    NON_RESIDENT_FOREIGNER = "non_resident_foreigner"


class IncomeSource(Enum):
    """Types of income sources"""
    SALARY = "salary"
    BUSINESS = "business"
    INVESTMENT = "investment"
    RENTAL = "rental"
    OTHER = "other"


@dataclass
class IncomeEntry:
    """Individual income entry"""
    source: IncomeSource
    amount: float
    description: str = ""
    is_exempt: bool = False


@dataclass
class Taxpayer:
    """Represents a taxpayer with all relevant information"""

    # Personal information
    name: str = ""
    civil_id: str = ""
    residency_status: ResidencyStatus = ResidencyStatus.RESIDENT

    # Income information
    income_entries: Dict[str, IncomeEntry] = field(default_factory=dict)

    # Deductions
    deductions: Dict[str, float] = field(default_factory=lambda: {
        'education': 0.0,
        'medical': 0.0,
        'zakat': 0.0,
        'housing': 0.0
    })

    # Metadata
    tax_year: int = field(default_factory=lambda: datetime.now().year)
    created_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)

    def add_income(self, source: IncomeSource, amount: float,
                   description: str = "", is_exempt: bool = False) -> None:
        """Add an income entry"""
        entry_id = f"{source.value}_{len(self.income_entries)}"
        self.income_entries[entry_id] = IncomeEntry(
            source=source,
            amount=amount,
            description=description,
            is_exempt=is_exempt
        )
        self.last_modified = datetime.now()

    def get_total_income(self, include_exempt: bool = True) -> float:
        """Calculate total income"""
        total = 0.0
        for entry in self.income_entries.values():
            if include_exempt or not entry.is_exempt:
                total += entry.amount
        return total

    def get_taxable_income(self) -> float:
        """Get taxable income (excluding exempt income)"""
        return self.get_total_income(include_exempt=False)

    def set_deduction(self, category: str, amount: float) -> None:
        """Set deduction amount for a category"""
        if category in self.deductions:
            self.deductions[category] = max(0, amount)
            self.last_modified = datetime.now()

    def get_total_deductions(self) -> float:
        """Calculate total deductions"""
        return sum(self.deductions.values())

    def is_tax_resident(self) -> bool:
        """Check if taxpayer is a tax resident"""
        return self.residency_status == ResidencyStatus.RESIDENT

    def to_dict(self) -> Dict:
        """Convert taxpayer to dictionary for serialization"""
        return {
            'name': self.name,
            'civil_id': self.civil_id,
            'residency_status': self.residency_status.value,
            'income_entries': {
                key: {
                    'source': entry.source.value,
                    'amount': entry.amount,
                    'description': entry.description,
                    'is_exempt': entry.is_exempt
                }
                for key, entry in self.income_entries.items()
            },
            'deductions': self.deductions,
            'tax_year': self.tax_year,
            'created_date': self.created_date.isoformat(),
            'last_modified': self.last_modified.isoformat()
        }