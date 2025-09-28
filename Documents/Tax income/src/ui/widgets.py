"""
Custom widgets for the tax calculator application
"""

from PyQt5.QtWidgets import (QLineEdit, QLabel, QVBoxLayout, QHBoxLayout,
                             QWidget, QFrame, QPushButton, QSpinBox)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPalette


class CurrencyInput(QLineEdit):
    """Custom line edit for currency input with OMR formatting"""

    valueChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("0.00")
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text):
        """Handle text changes and emit value changed signal"""
        try:
            # Remove currency symbols and parse
            cleaned = text.replace('OMR', '').replace(',', '').strip()
            if cleaned:
                value = float(cleaned)
                self.valueChanged.emit(value)
            else:
                self.valueChanged.emit(0.0)
        except ValueError:
            pass

    def setValue(self, value: float):
        """Set the currency value"""
        self.setText(f"{value:,.2f}")

    def getValue(self) -> float:
        """Get the current currency value"""
        try:
            cleaned = self.text().replace('OMR', '').replace(',', '').strip()
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0


class InfoLabel(QLabel):
    """Custom label for displaying information with styling"""

    def __init__(self, text="", info_type="normal", parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self._set_style(info_type)

    def _set_style(self, info_type):
        """Set label style based on type"""
        if info_type == "title":
            font = QFont()
            font.setPointSize(14)
            font.setBold(True)
            self.setFont(font)
        elif info_type == "subtitle":
            font = QFont()
            font.setPointSize(10)
            font.setItalic(True)
            self.setFont(font)
        elif info_type == "warning":
            self.setStyleSheet("color: orange; font-weight: bold;")
        elif info_type == "error":
            self.setStyleSheet("color: red; font-weight: bold;")
        elif info_type == "success":
            self.setStyleSheet("color: green; font-weight: bold;")


class SectionFrame(QFrame):
    """Custom frame for creating distinct sections in the UI"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)

        layout = QVBoxLayout(self)

        if title:
            title_label = InfoLabel(title, "subtitle")
            layout.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

    def addWidget(self, widget):
        """Add widget to the section"""
        self.content_layout.addWidget(widget)

    def addLayout(self, layout):
        """Add layout to the section"""
        self.content_layout.addLayout(layout)


class CalculationSummary(QWidget):
    """Widget for displaying tax calculation summary"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize the summary UI"""
        layout = QVBoxLayout(self)

        # Title
        title = InfoLabel("Tax Calculation Summary", "title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Summary labels
        self.income_label = InfoLabel("Annual Income: OMR 0.00")
        self.deductions_label = InfoLabel("Total Deductions: OMR 0.00")
        self.taxable_label = InfoLabel("Taxable Income: OMR 0.00")
        self.tax_label = InfoLabel("Tax Owed: OMR 0.00", "success")
        self.net_label = InfoLabel("Net Income: OMR 0.00")

        layout.addWidget(self.income_label)
        layout.addWidget(self.deductions_label)
        layout.addWidget(self.taxable_label)
        layout.addWidget(self.tax_label)
        layout.addWidget(self.net_label)

    def update_summary(self, summary: dict):
        """Update the summary display"""
        self.income_label.setText(f"Annual Income: OMR {summary['annual_income']:,.2f}")
        self.deductions_label.setText(f"Total Deductions: OMR {summary['total_deductions']:,.2f}")
        self.taxable_label.setText(f"Taxable Income: OMR {summary['taxable_income']:,.2f}")
        self.tax_label.setText(f"Tax Owed: OMR {summary['tax_owed']:,.2f}")
        self.net_label.setText(f"Net Income: OMR {summary['net_income']:,.2f}")

        # Color code the tax amount
        if summary['tax_owed'] > 0:
            self.tax_label._set_style("warning")
        else:
            self.tax_label._set_style("success")