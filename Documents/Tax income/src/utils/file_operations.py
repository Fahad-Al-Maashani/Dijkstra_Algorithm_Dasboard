"""
File operations for saving and loading tax calculations
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class TaxFileOperations:
    """Handle file operations for tax calculations"""

    @staticmethod
    def save_calculation_json(calculation_data: Dict, file_path: str) -> bool:
        """Save tax calculation to JSON file"""
        try:
            # Add timestamp
            calculation_data['timestamp'] = datetime.now().isoformat()
            calculation_data['version'] = '1.0'

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(calculation_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving JSON: {e}")
            return False

    @staticmethod
    def load_calculation_json(file_path: str) -> Optional[Dict]:
        """Load tax calculation from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return None

    @staticmethod
    def export_to_csv(calculations: List[Dict], file_path: str) -> bool:
        """Export multiple calculations to CSV"""
        try:
            fieldnames = [
                'timestamp', 'annual_income', 'total_deductions',
                'taxable_income', 'tax_owed', 'net_income',
                'education_deduction', 'medical_deduction',
                'zakat_deduction', 'housing_deduction'
            ]

            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for calc in calculations:
                    row = {
                        'timestamp': calc.get('timestamp', ''),
                        'annual_income': calc.get('annual_income', 0),
                        'total_deductions': calc.get('total_deductions', 0),
                        'taxable_income': calc.get('taxable_income', 0),
                        'tax_owed': calc.get('tax_owed', 0),
                        'net_income': calc.get('net_income', 0),
                        'education_deduction': calc.get('deductions', {}).get('education', 0),
                        'medical_deduction': calc.get('deductions', {}).get('medical', 0),
                        'zakat_deduction': calc.get('deductions', {}).get('zakat', 0),
                        'housing_deduction': calc.get('deductions', {}).get('housing', 0)
                    }
                    writer.writerow(row)
            return True
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False

    @staticmethod
    def generate_tax_report(calculation_data: Dict, file_path: str) -> bool:
        """Generate a formatted tax report"""
        try:
            report_content = f"""
OMAN TAX CALCULATION REPORT
===========================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TAXPAYER INFORMATION
--------------------
Annual Income:        OMR {calculation_data['annual_income']:,.2f}

DEDUCTIONS
----------
Education:           OMR {calculation_data.get('deductions', {}).get('education', 0):,.2f}
Medical:             OMR {calculation_data.get('deductions', {}).get('medical', 0):,.2f}
Zakat:               OMR {calculation_data.get('deductions', {}).get('zakat', 0):,.2f}
Housing:             OMR {calculation_data.get('deductions', {}).get('housing', 0):,.2f}
Total Deductions:    OMR {calculation_data['total_deductions']:,.2f}

TAX CALCULATION
---------------
Taxable Income:      OMR {calculation_data['taxable_income']:,.2f}
Tax Threshold:       OMR {calculation_data['tax_threshold']:,.2f}
Tax Rate:            {calculation_data['tax_rate']*100:.1f}%
Tax Owed:            OMR {calculation_data['tax_owed']:,.2f}

SUMMARY
-------
Net Income After Tax: OMR {calculation_data['net_income']:,.2f}

Note: Calculation based on Oman Personal Income Tax Law 2025
Effective from January 1, 2028
"""

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_content.strip())
            return True
        except Exception as e:
            print(f"Error generating report: {e}")
            return False

    @staticmethod
    def create_backup_directory(base_path: str = None) -> Path:
        """Create backup directory for saved calculations"""
        if base_path is None:
            base_path = Path.home() / "OmanTaxCalculator"

        backup_dir = Path(base_path) / "calculations" / datetime.now().strftime('%Y')
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir