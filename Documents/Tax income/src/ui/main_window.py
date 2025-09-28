"""
Main Window for Oman Tax Calculator

Provides the primary user interface for tax calculations.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QGroupBox,
                             QFormLayout, QTextEdit, QApplication, QMenuBar,
                             QMenu, QAction, QStatusBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from src.models.tax_calculator import TaxCalculator


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

        # Create main layout
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
            income = float(self.income_input.text() or "0")
            self.tax_calculator.set_annual_income(income)

            # Get deductions
            education = float(self.education_input.text() or "0")
            medical = float(self.medical_input.text() or "0")
            zakat = float(self.zakat_input.text() or "0")
            housing = float(self.housing_input.text() or "0")

            self.tax_calculator.set_deduction('education', education)
            self.tax_calculator.set_deduction('medical', medical)
            self.tax_calculator.set_deduction('zakat', zakat)
            self.tax_calculator.set_deduction('housing', housing)

            # Calculate and display results
            summary = self.tax_calculator.get_tax_summary()
            self.display_results(summary)

            self.status_bar.showMessage("Tax calculation completed")

        except ValueError:
            self.status_bar.showMessage("Error: Please enter valid numbers")
            self.results_text.setText("Error: Please enter valid numbers only.")

    def display_results(self, summary):
        """Display tax calculation results"""
        results_text = f"""
TAX CALCULATION SUMMARY
=======================

Annual Income:          OMR {summary['annual_income']:,.2f}
Total Deductions:       OMR {summary['total_deductions']:,.2f}
Taxable Income:         OMR {summary['taxable_income']:,.2f}

Tax Threshold:          OMR {summary['tax_threshold']:,.2f}
Tax Rate:               {summary['tax_rate']*100:.1f}%

TAX OWED:              OMR {summary['tax_owed']:,.2f}
Net Income After Tax:   OMR {summary['net_income']:,.2f}

Note: Tax applies only to income above OMR 42,000 threshold.
Effective from January 1, 2028.
        """
        self.results_text.setText(results_text.strip())

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
        about_text = """
Oman Tax Calculator v1.0

This application calculates personal income tax according to the
Oman Personal Income Tax Law 2025.

Key Features:
• 5% flat rate on income above OMR 42,000
• Support for education, medical, zakat, and housing deductions
• Comprehensive tax summary

Effective from January 1, 2028.
        """
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(self, "About Oman Tax Calculator", about_text.strip())