# Oman Tax Calculator

A Python Qt application for calculating personal income tax according to Oman Personal Income Tax Law 2025.

## Overview

This application implements the new personal income tax system introduced in Oman, which becomes effective January 1, 2028. It features a 5% flat tax rate on annual income exceeding OMR 42,000.

## Features

- **Simple Tax Calculation**: 5% flat rate on income above OMR 42,000 threshold
- **Deduction Support**: Education, medical, zakat (charitable donations), and housing expenses
- **User-Friendly Interface**: Clean PyQt5 GUI with input validation
- **Real-time Calculation**: Instant tax calculation and summary
- **Currency Formatting**: Proper OMR currency display

## Tax Law Details

Based on Oman Personal Income Tax Law 2025:
- **Tax Rate**: 5% flat rate
- **Threshold**: OMR 42,000 annual income
- **Effective Date**: January 1, 2028
- **Scope**: Worldwide income for tax residents
- **Coverage**: Affects less than 1% of the population

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Fahad-Al-Maashani/Tax_Income.git
cd Tax_Income
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

1. Enter your annual income in OMR
2. Add any applicable deductions:
   - Education expenses
   - Medical expenses
   - Zakat/charitable donations
   - Housing expenses
3. Click "Calculate Tax" to see your tax summary

## Project Structure

```
Tax_Income/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── src/
│   ├── ui/
│   │   └── main_window.py  # Main GUI window
│   ├── models/
│   │   └── tax_calculator.py  # Tax calculation logic
│   ├── utils/
│   │   └── validators.py   # Input validation utilities
│   └── tests/
│       └── test_tax_calculator.py  # Unit tests
└── README.md
```

## Running Tests

```bash
python -m pytest src/tests/
```

## License

MIT License - see LICENSE file for details.