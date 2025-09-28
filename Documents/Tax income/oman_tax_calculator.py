#!/usr/bin/env python3
"""
Oman Tax Calculator - Standalone Application
Calculates personal income tax according to Oman Personal Income Tax Law 2025
"""

import sys
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QTextEdit, QMenuBar, QMenu,
    QAction, QStatusBar, QMessageBox, QFileDialog, QComboBox, QCheckBox,
    QDialog, QDialogButtonBox, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon


class TaxCalculator:
    """
    Calculates personal income tax according to Oman tax law.
    Tax Structure: 5% flat rate on income above OMR 42,000 threshold
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


class InputValidator:
    """Validates user input for tax calculations"""

    @staticmethod
    def validate_currency(value: str) -> Tuple[bool, float]:
        """Validate currency input"""
        if not value or value.strip() == "":
            return True, 0.0

        # Remove common currency symbols and whitespace
        cleaned = value.replace('OMR', '').replace(',', '').strip()
        try:
            amount = float(cleaned)
            return amount >= 0, max(0, amount)
        except ValueError:
            return False, 0.0

    @staticmethod
    def format_currency(amount: float) -> str:
        """Format amount as currency string"""
        return f"OMR {amount:,.2f}"


class CurrencyConverter:
    """Handle currency conversions for multi-currency support"""

    EXCHANGE_RATES = {
        'USD': 0.3854,  'EUR': 0.4214,  'GBP': 0.4897,
        'AED': 0.1049,  'SAR': 0.1028,  'KWD': 1.2641,
        'BHD': 1.0204,  'QAR': 0.1058,  'OMR': 1.0000
    }

    @classmethod
    def convert_to_omr(cls, amount: float, from_currency: str) -> float:
        """Convert amount from specified currency to OMR"""
        if from_currency not in cls.EXCHANGE_RATES:
            raise ValueError(f"Unsupported currency: {from_currency}")
        return amount * cls.EXCHANGE_RATES[from_currency]

    @classmethod
    def get_supported_currencies(cls) -> list:
        """Get list of supported currencies"""
        return list(cls.EXCHANGE_RATES.keys())


class TaxFileOperations:
    """Handle file operations for tax calculations"""

    @staticmethod
    def save_calculation_json(calculation_data: Dict, file_path: str) -> bool:
        """Save tax calculation to JSON file"""
        try:
            calculation_data['timestamp'] = datetime.now().isoformat()
            calculation_data['version'] = '1.0'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(calculation_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    @staticmethod
    def load_calculation_json(file_path: str) -> Optional[Dict]:
        """Load tax calculation from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    @staticmethod
    def export_to_csv(calculations: list, file_path: str) -> bool:
        """Export calculations to CSV"""
        try:
            fieldnames = ['timestamp', 'annual_income', 'total_deductions',
                         'taxable_income', 'tax_owed', 'net_income']
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for calc in calculations:
                    writer.writerow(calc)
            return True
        except Exception:
            return False


class AboutDialog(QDialog):
    """About dialog for the application"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Oman Tax Calculator")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Initialize the about dialog"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Oman Tax Calculator")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Version
        version = QLabel("Version 1.0.0")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        # Description
        description = QTextEdit()
        description.setReadOnly(True)
        description.setMaximumHeight(200)
        description.setText("""
This application calculates personal income tax according to the Oman Personal Income Tax Law 2025.

Key Features:
• 5% flat rate on income above OMR 42,000
• Support for multiple income sources
• Deduction tracking for education, medical, zakat, and housing
• Multi-currency support
• Tax report generation

The tax law becomes effective January 1, 2028.

Developed for compliance with Oman Vision 2040 fiscal reforms.
        """.strip())
        layout.addWidget(description)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.tax_calculator = TaxCalculator()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Oman Tax Calculator")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Add title
        title_label = QLabel("Oman Personal Income Tax Calculator")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Add subtitle
        subtitle_label = QLabel("Based on Oman Personal Income Tax Law 2025")
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)

        # Create input section
        self.create_input_section(main_layout)

        # Create results section
        self.create_results_section(main_layout)

        # Create menu bar
        self.create_menu_bar()

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to calculate taxes")

    def create_input_section(self, parent_layout):
        """Create the input section of the UI"""
        # Income input group
        income_group = QGroupBox("Annual Income")
        income_layout = QFormLayout()

        self.income_input = QLineEdit()
        self.income_input.setPlaceholderText("Enter annual income in OMR")
        income_layout.addRow("Annual Income (OMR):", self.income_input)

        income_group.setLayout(income_layout)
        parent_layout.addWidget(income_group)

        # Deductions group
        deductions_group = QGroupBox("Deductions")
        deductions_layout = QFormLayout()

        self.education_input = QLineEdit()
        self.education_input.setPlaceholderText("Education expenses")
        deductions_layout.addRow("Education (OMR):", self.education_input)

        self.medical_input = QLineEdit()
        self.medical_input.setPlaceholderText("Medical expenses")
        deductions_layout.addRow("Medical (OMR):", self.medical_input)

        self.zakat_input = QLineEdit()
        self.zakat_input.setPlaceholderText("Zakat/charitable donations")
        deductions_layout.addRow("Zakat (OMR):", self.zakat_input)

        self.housing_input = QLineEdit()
        self.housing_input.setPlaceholderText("Housing expenses")
        deductions_layout.addRow("Housing (OMR):", self.housing_input)

        deductions_group.setLayout(deductions_layout)
        parent_layout.addWidget(deductions_group)

        # Calculate button
        self.calculate_button = QPushButton("Calculate Tax")
        self.calculate_button.clicked.connect(self.calculate_tax)
        parent_layout.addWidget(self.calculate_button)

    def create_results_section(self, parent_layout):
        """Create the results section of the UI"""
        results_group = QGroupBox("Tax Calculation Results")
        results_layout = QVBoxLayout()

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        results_layout.addWidget(self.results_text)

        results_group.setLayout(results_layout)
        parent_layout.addWidget(results_group)

    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        save_action = QAction('Save Calculation', self)
        save_action.triggered.connect(self.save_calculation)
        file_menu.addAction(save_action)

        load_action = QAction('Load Calculation', self)
        load_action.triggered.connect(self.load_calculation)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        clear_action = QAction('Clear All', self)
        clear_action.triggered.connect(self.clear_all)
        file_menu.addAction(clear_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def calculate_tax(self):
        """Calculate and display tax results"""
        try:
            # Get income
            is_valid, income = InputValidator.validate_currency(self.income_input.text())
            if not is_valid:
                raise ValueError("Invalid income amount")
            self.tax_calculator.set_annual_income(income)

            # Get deductions
            education = InputValidator.validate_currency(self.education_input.text())[1]
            medical = InputValidator.validate_currency(self.medical_input.text())[1]
            zakat = InputValidator.validate_currency(self.zakat_input.text())[1]
            housing = InputValidator.validate_currency(self.housing_input.text())[1]

            self.tax_calculator.set_deduction('education', education)
            self.tax_calculator.set_deduction('medical', medical)
            self.tax_calculator.set_deduction('zakat', zakat)
            self.tax_calculator.set_deduction('housing', housing)

            # Calculate and display results
            summary = self.tax_calculator.get_tax_summary()
            self.display_results(summary)

            self.status_bar.showMessage("Tax calculation completed")

        except ValueError as e:
            self.status_bar.showMessage(f"Error: {str(e)}")
            self.results_text.setText(f"Error: {str(e)}")

    def display_results(self, summary):
        """Display tax calculation results"""
        results_text = f"""
TAX CALCULATION SUMMARY
=======================

Annual Income:          {InputValidator.format_currency(summary['annual_income'])}
Total Deductions:       {InputValidator.format_currency(summary['total_deductions'])}
Taxable Income:         {InputValidator.format_currency(summary['taxable_income'])}

Tax Threshold:          {InputValidator.format_currency(summary['tax_threshold'])}
Tax Rate:               {summary['tax_rate']*100:.1f}%

TAX OWED:              {InputValidator.format_currency(summary['tax_owed'])}
Net Income After Tax:   {InputValidator.format_currency(summary['net_income'])}

Note: Tax applies only to income above OMR 42,000 threshold.
Effective from January 1, 2028.
        """
        self.results_text.setText(results_text.strip())

    def save_calculation(self):
        """Save current calculation to file"""
        if self.tax_calculator.annual_income == 0:
            QMessageBox.warning(self, "Warning", "No calculation to save!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Calculation", "", "JSON Files (*.json)")

        if file_path:
            summary = self.tax_calculator.get_tax_summary()
            summary['deductions'] = self.tax_calculator.deductions

            if TaxFileOperations.save_calculation_json(summary, file_path):
                QMessageBox.information(self, "Success", "Calculation saved successfully!")
                self.status_bar.showMessage(f"Saved to {file_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save calculation!")

    def load_calculation(self):
        """Load calculation from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Calculation", "", "JSON Files (*.json)")

        if file_path:
            data = TaxFileOperations.load_calculation_json(file_path)
            if data:
                self.tax_calculator.set_annual_income(data.get('annual_income', 0))

                deductions = data.get('deductions', {})
                self.education_input.setText(str(deductions.get('education', 0)))
                self.medical_input.setText(str(deductions.get('medical', 0)))
                self.zakat_input.setText(str(deductions.get('zakat', 0)))
                self.housing_input.setText(str(deductions.get('housing', 0)))
                self.income_input.setText(str(data.get('annual_income', 0)))

                self.calculate_tax()
                QMessageBox.information(self, "Success", "Calculation loaded successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to load calculation!")

    def clear_all(self):
        """Clear all input fields and results"""
        self.income_input.clear()
        self.education_input.clear()
        self.medical_input.clear()
        self.zakat_input.clear()
        self.housing_input.clear()
        self.results_text.clear()
        self.status_bar.showMessage("All fields cleared")

    def show_about(self):
        """Show about dialog"""
        dialog = AboutDialog(self)
        dialog.exec_()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Oman Tax Calculator")
    app.setApplicationVersion("1.0.0")

    window = MainWindow()
    window.show()

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())