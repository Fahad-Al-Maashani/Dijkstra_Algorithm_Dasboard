"""
Logging configuration for the tax calculator application
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


class TaxCalculatorLogger:
    """Custom logger for the tax calculator application"""

    def __init__(self, log_level=logging.INFO):
        self.log_level = log_level
        self.logger = None
        self._setup_logger()

    def _setup_logger(self):
        """Setup the logger with appropriate handlers"""
        self.logger = logging.getLogger('oman_tax_calculator')
        self.logger.setLevel(self.log_level)

        # Clear any existing handlers
        self.logger.handlers.clear()

        # Create log directory
        log_dir = Path.home() / '.oman_tax_calculator' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        # File handler for all logs
        log_file = log_dir / 'tax_calculator.log'
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler for development
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
        self.logger.addHandler(console_handler)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def log_calculation(self, taxpayer_name: str, income: float, tax_owed: float):
        """Log tax calculation details"""
        self.info(f"Tax calculation - Taxpayer: {taxpayer_name}, "
                  f"Income: OMR {income:,.2f}, Tax: OMR {tax_owed:,.2f}")

    def log_file_operation(self, operation: str, file_path: str, success: bool):
        """Log file operation"""
        status = "successful" if success else "failed"
        self.info(f"File operation {operation} {status} - Path: {file_path}")

    def log_error_with_details(self, error_type: str, details: str):
        """Log error with additional details"""
        self.error(f"{error_type}: {details}")


# Global logger instance
logger = TaxCalculatorLogger()