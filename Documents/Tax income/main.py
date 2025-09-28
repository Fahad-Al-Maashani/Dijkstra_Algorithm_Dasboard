#!/usr/bin/env python3
"""
Oman Tax Income Calculator
Main application entry point

This application calculates personal income tax according to Oman tax law (2025).
Tax rate: 5% flat rate on income above OMR 42,000 threshold
Effective from January 1, 2028
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow

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