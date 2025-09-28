"""Custom exceptions for tax calculator"""

class TaxCalculatorError(Exception):
    """Base exception for tax calculator"""
    pass

class InvalidIncomeError(TaxCalculatorError):
    """Raised when income is invalid"""
    pass

class InvalidDeductionError(TaxCalculatorError):
    """Raised when deduction is invalid"""
    pass

class FileOperationError(TaxCalculatorError):
    """Raised when file operation fails"""
    pass

class ValidationError(TaxCalculatorError):
    """Raised when validation fails"""
    pass
