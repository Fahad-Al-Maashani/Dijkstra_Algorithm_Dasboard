"""
Dialog windows for the tax calculator application
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox, QTextEdit,
                             QDialogButtonBox, QFormLayout, QGroupBox,
                             QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from src.models.taxpayer import ResidencyStatus, IncomeSource
from src.utils.currency_converter import CurrencyConverter


class TaxpayerInfoDialog(QDialog):
    """Dialog for entering taxpayer information"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Taxpayer Information")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)

        # Personal info group
        personal_group = QGroupBox("Personal Information")
        personal_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.civil_id_input = QLineEdit()
        self.residency_combo = QComboBox()

        for status in ResidencyStatus:
            self.residency_combo.addItem(status.value.replace('_', ' ').title(), status)

        personal_layout.addRow("Full Name:", self.name_input)
        personal_layout.addRow("Civil ID:", self.civil_id_input)
        personal_layout.addRow("Residency Status:", self.residency_combo)

        personal_group.setLayout(personal_layout)
        layout.addWidget(personal_group)

        # Tax year
        year_group = QGroupBox("Tax Year")
        year_layout = QFormLayout()

        self.year_spin = QSpinBox()
        self.year_spin.setRange(2028, 2050)
        self.year_spin.setValue(2028)

        year_layout.addRow("Tax Year:", self.year_spin)
        year_group.setLayout(year_layout)
        layout.addWidget(year_group)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_taxpayer_info(self):
        """Get taxpayer information from dialog"""
        return {
            'name': self.name_input.text(),
            'civil_id': self.civil_id_input.text(),
            'residency_status': self.residency_combo.currentData(),
            'tax_year': self.year_spin.value()
        }


class IncomeEntryDialog(QDialog):
    """Dialog for adding income entries"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Income Entry")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)

        # Income details group
        income_group = QGroupBox("Income Details")
        income_layout = QFormLayout()

        self.source_combo = QComboBox()
        for source in IncomeSource:
            self.source_combo.addItem(source.value.title(), source)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")

        self.currency_combo = QComboBox()
        for currency in CurrencyConverter.get_supported_currencies():
            self.currency_combo.addItem(currency)
        self.currency_combo.setCurrentText("OMR")

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Optional description")

        self.exempt_checkbox = QCheckBox("This income is exempt from tax")

        income_layout.addRow("Income Source:", self.source_combo)
        income_layout.addRow("Amount:", self.amount_input)
        income_layout.addRow("Currency:", self.currency_combo)
        income_layout.addRow("Description:", self.description_input)
        income_layout.addRow("", self.exempt_checkbox)

        income_group.setLayout(income_layout)
        layout.addWidget(income_group)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_income_data(self):
        """Get income data from dialog"""
        try:
            amount = float(self.amount_input.text())
            currency = self.currency_combo.currentText()

            # Convert to OMR if needed
            if currency != "OMR":
                amount = CurrencyConverter.convert_to_omr(amount, currency)

            return {
                'source': self.source_combo.currentData(),
                'amount': amount,
                'description': self.description_input.text(),
                'is_exempt': self.exempt_checkbox.isChecked()
            }
        except ValueError:
            return None


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