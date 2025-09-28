# Oman Tax Calculator v1.0.0 for Windows

## Installation Instructions

1. Extract this package to your desired location (e.g., Program Files or Desktop)
2. Double-click on OmanTaxCalculator.exe to run the application
3. If Windows Defender shows a warning, click "More info" then "Run anyway"

## Features

- Calculate personal income tax according to Oman Personal Income Tax Law 2025
- 5% flat rate on income above OMR 42,000 threshold
- Support for deductions:
  * Education expenses
  * Medical expenses
  * Zakat/charitable donations
  * Housing expenses
- Save and load calculations as JSON files
- Multi-currency support (USD, EUR, GBP, GCC currencies)
- Export calculations to CSV
- Professional tax reports

## How to Use

1. Enter your annual income in OMR
2. Add any applicable deductions in the respective fields
3. Click "Calculate Tax" to see your tax summary
4. Use File menu to save/load calculations

## System Requirements

- Windows 10 or later (64-bit)
- No additional software required (standalone executable)
- 4GB RAM recommended
- 100MB free disk space

## Tax Law Information

Based on Oman Personal Income Tax Law 2025:
- Tax Rate: 5% flat rate
- Threshold: OMR 42,000 annual income
- Effective Date: January 1, 2028
- Applies to tax residents on worldwide income

## Important Notes

- This calculator is for informational purposes only
- Tax calculations should be verified with official sources
- Consult with a qualified tax professional for official tax advice
- The developer is not responsible for any tax-related decisions based on this calculator

## Troubleshooting

1. If the application doesn't start:
   - Make sure you have Windows 10 or later
   - Try running as administrator
   - Check if antivirus software is blocking the application

2. If you get a "missing DLL" error:
   - Download and install Microsoft Visual C++ Redistributable 2019 or later

## Support

For technical issues or questions about the application, please contact the developer.

## Building for Windows

To create the Windows executable, run the following on a Windows machine:

1. Install Python 3.8+ and pip
2. pip install PyQt5 pyinstaller
3. pyinstaller --onefile --windowed --name "OmanTaxCalculator" oman_tax_calculator.py

## Version History

v1.0.0 - Initial release
- Core tax calculation functionality
- User-friendly PyQt5 interface
- File save/load capabilities
- Multi-currency support