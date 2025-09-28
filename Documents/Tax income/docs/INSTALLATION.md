# Installation Guide

## Prerequisites

- Python 3.7 or higher
- PyQt5 library
- Git (for cloning the repository)

## System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **RAM**: Minimum 4GB recommended
- **Storage**: 100MB free space

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Fahad-Al-Maashani/Tax_Income.git
cd Tax_Income
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv tax_calc_env
source tax_calc_env/bin/activate  # On Windows: tax_calc_env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python main.py
```

## Troubleshooting

### Common Issues

1. **PyQt5 Installation Issues**
   - Ensure you have the latest pip: `pip install --upgrade pip`
   - Try installing PyQt5 separately: `pip install PyQt5`

2. **Import Errors**
   - Verify Python path includes the project directory
   - Check virtual environment activation

3. **Permission Errors**
   - Ensure write permissions for log and config directories
   - Run with appropriate user privileges

## Development Setup

For development, install additional dependencies:

```bash
pip install pytest pytest-cov black flake8
```

## Verification

After installation, verify the setup:

```bash
python -c "from src.models.tax_calculator import TaxCalculator; print('Installation successful!')"
```