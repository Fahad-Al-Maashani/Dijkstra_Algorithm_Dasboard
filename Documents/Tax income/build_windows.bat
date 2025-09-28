@echo off
REM Build script for Windows

echo Building Oman Tax Calculator for Windows...

REM Install dependencies
pip install -r requirements_build.txt

REM Create standalone executable with PyInstaller
pyinstaller --onefile --windowed ^
    --name "OmanTaxCalculator" ^
    --clean ^
    --distpath "./dist_windows" ^
    oman_tax_calculator.py

REM Create distribution package
set PKG_NAME=OmanTaxCalculator_Windows

REM Create package directory
mkdir "%PKG_NAME%"
copy "dist_windows\OmanTaxCalculator.exe" "%PKG_NAME%\"

REM Create README
echo # Oman Tax Calculator v1.0.0 for Windows > "%PKG_NAME%\README.txt"
echo. >> "%PKG_NAME%\README.txt"
echo ## Installation Instructions >> "%PKG_NAME%\README.txt"
echo. >> "%PKG_NAME%\README.txt"
echo 1. Extract this package to your desired location >> "%PKG_NAME%\README.txt"
echo 2. Double-click on OmanTaxCalculator.exe to run >> "%PKG_NAME%\README.txt"
echo. >> "%PKG_NAME%\README.txt"
echo ## Features >> "%PKG_NAME%\README.txt"
echo. >> "%PKG_NAME%\README.txt"
echo - Calculate personal income tax according to Oman Personal Income Tax Law 2025 >> "%PKG_NAME%\README.txt"
echo - 5%% flat rate on income above OMR 42,000 >> "%PKG_NAME%\README.txt"
echo - Support for deductions (education, medical, zakat, housing) >> "%PKG_NAME%\README.txt"
echo - Save and load calculations >> "%PKG_NAME%\README.txt"
echo. >> "%PKG_NAME%\README.txt"
echo ## System Requirements >> "%PKG_NAME%\README.txt"
echo. >> "%PKG_NAME%\README.txt"
echo - Windows 10 or later >> "%PKG_NAME%\README.txt"
echo - No additional software required >> "%PKG_NAME%\README.txt"
echo. >> "%PKG_NAME%\README.txt"
echo For issues, please contact the developer. >> "%PKG_NAME%\README.txt"

REM Create ZIP package (requires PowerShell)
powershell -command "Compress-Archive -Path '%PKG_NAME%' -DestinationPath '%PKG_NAME%.zip' -Force"

echo ✅ Windows package created: %PKG_NAME%.zip