"""
Oman Tax Calculator Model

Implements tax calculation logic according to Oman Personal Income Tax Law 2025.
"""

class TaxCalculator:
    """
    Calculates personal income tax according to Oman tax law.

    Tax Structure:
    - Threshold: OMR 42,000 annual income
    - Rate: 5% flat rate on income exceeding the threshold
    - Effective: January 1, 2028
    """

    TAX_THRESHOLD = 42000.0  # OMR
    TAX_RATE = 0.05  # 5%

    def __init__(self):
        self.annual_income = 0.0
        self.deductions = {
            'education': 0.0,
            'medical': 0.0,
            'zakat': 0.0,
            'housing': 0.0
        }

    def set_annual_income(self, income: float) -> None:
        """Set annual income in OMR"""
        self.annual_income = max(0, income)

    def set_deduction(self, category: str, amount: float) -> None:
        """Set deduction amount for a specific category"""
        if category in self.deductions:
            self.deductions[category] = max(0, amount)

    def calculate_total_deductions(self) -> float:
        """Calculate total allowable deductions"""
        return sum(self.deductions.values())

    def calculate_taxable_income(self) -> float:
        """Calculate taxable income after deductions"""
        return max(0, self.annual_income - self.calculate_total_deductions())

    def calculate_tax_owed(self) -> float:
        """Calculate total tax owed"""
        taxable_income = self.calculate_taxable_income()

        if taxable_income <= self.TAX_THRESHOLD:
            return 0.0

        return (taxable_income - self.TAX_THRESHOLD) * self.TAX_RATE

    def get_tax_summary(self) -> dict:
        """Get complete tax calculation summary"""
        return {
            'annual_income': self.annual_income,
            'total_deductions': self.calculate_total_deductions(),
            'taxable_income': self.calculate_taxable_income(),
            'tax_threshold': self.TAX_THRESHOLD,
            'tax_rate': self.TAX_RATE,
            'tax_owed': self.calculate_tax_owed(),
            'net_income': self.annual_income - self.calculate_tax_owed()
        }