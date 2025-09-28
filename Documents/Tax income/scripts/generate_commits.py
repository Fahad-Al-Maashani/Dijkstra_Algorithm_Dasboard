#!/usr/bin/env python3
"""
Script to generate meaningful commits for the tax calculator project
"""

import os
import subprocess
import time
from pathlib import Path


def run_git_command(command):
    """Run a git command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def create_file_with_content(file_path, content):
    """Create a file with given content"""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_documentation_files():
    """Generate documentation files"""
    docs = [
        {
            'path': 'docs/INSTALLATION.md',
            'content': '''# Installation Guide

## Prerequisites
- Python 3.7 or higher
- PyQt5

## Installation Steps
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`
''',
            'commit': 'Add installation documentation'
        },
        {
            'path': 'docs/USER_GUIDE.md',
            'content': '''# User Guide

## Getting Started
This guide helps you use the Oman Tax Calculator effectively.

## Main Features
- Income entry and calculation
- Deduction management
- Tax report generation
''',
            'commit': 'Add user guide documentation'
        },
        {
            'path': 'docs/API.md',
            'content': '''# API Documentation

## TaxCalculator Class
Main class for tax calculations.

## Methods
- `calculate_tax_owed()`: Calculate tax amount
- `set_annual_income()`: Set income amount
''',
            'commit': 'Add API documentation'
        }
    ]

    for doc in docs:
        create_file_with_content(doc['path'], doc['content'])
        run_git_command(f"git add {doc['path']}")
        run_git_command(f"git commit -m \"{doc['commit']}\"")
        time.sleep(1)


def generate_utility_files():
    """Generate utility files"""
    utils = [
        {
            'path': 'src/utils/date_utils.py',
            'content': '''"""Date utility functions"""
from datetime import datetime

def get_tax_year():
    return datetime.now().year

def format_date(date):
    return date.strftime('%Y-%m-%d')
''',
            'commit': 'Add date utility functions'
        },
        {
            'path': 'src/utils/math_utils.py',
            'content': '''"""Mathematical utility functions"""

def round_currency(amount):
    return round(amount, 2)

def percentage_of(amount, percentage):
    return amount * (percentage / 100)
''',
            'commit': 'Add mathematical utility functions'
        }
    ]

    for util in utils:
        create_file_with_content(util['path'], util['content'])
        run_git_command(f"git add {util['path']}")
        run_git_command(f"git commit -m \"{util['commit']}\"")
        time.sleep(1)


def main():
    """Main function to generate commits"""
    print("Generating documentation files...")
    generate_documentation_files()

    print("Generating utility files...")
    generate_utility_files()

    print("Commits generated successfully!")


if __name__ == "__main__":
    main()