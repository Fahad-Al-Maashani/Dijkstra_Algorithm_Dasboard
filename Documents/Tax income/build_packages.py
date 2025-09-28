#!/usr/bin/env python3
"""
Build script to create standalone packages for Windows and macOS
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def install_dependencies():
    """Install required packages for building"""
    packages = [
        "PyQt5==5.15.9",
        "cx_Freeze==6.15.10",
        "pyinstaller==5.13.2"
    ]

    for package in packages:
        print(f"Installing {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

def build_with_pyinstaller():
    """Build using PyInstaller (works better for cross-platform)"""
    system = platform.system().lower()

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "OmanTaxCalculator",
        "--clean",
        "oman_tax_calculator.py"
    ]

    print(f"Building for {system}...")
    subprocess.run(cmd, check=True)

    return f"dist/OmanTaxCalculator{'.exe' if system == 'windows' else ''}"

def build_with_cx_freeze():
    """Build using cx_Freeze"""
    print("Building with cx_Freeze...")
    subprocess.run([sys.executable, "setup.py", "build"], check=True)

def create_distribution_package():
    """Create distribution package"""
    system = platform.system().lower()
    arch = platform.machine().lower()

    # Determine package name
    if system == "darwin" and "arm" in arch:
        pkg_name = "OmanTaxCalculator_macOS_M1"
    elif system == "darwin":
        pkg_name = "OmanTaxCalculator_macOS_Intel"
    elif system == "windows":
        pkg_name = "OmanTaxCalculator_Windows"
    else:
        pkg_name = f"OmanTaxCalculator_{system}"

    # Create package directory
    pkg_dir = Path(pkg_name)
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)
    pkg_dir.mkdir()

    # Copy executable
    if system == "windows":
        exe_path = Path("dist/OmanTaxCalculator.exe")
        if exe_path.exists():
            shutil.copy2(exe_path, pkg_dir / "OmanTaxCalculator.exe")
    else:
        exe_path = Path("dist/OmanTaxCalculator")
        if exe_path.exists():
            shutil.copy2(exe_path, pkg_dir / "OmanTaxCalculator")
            # Make executable on Unix systems
            os.chmod(pkg_dir / "OmanTaxCalculator", 0o755)

    # Create README
    readme_content = f"""
# Oman Tax Calculator v1.0.0

## Installation Instructions

### {system.title()} Installation:

1. Extract this package to your desired location
2. Double-click on OmanTaxCalculator to run the application

## Features

- Calculate personal income tax according to Oman Personal Income Tax Law 2025
- 5% flat rate on income above OMR 42,000
- Support for deductions (education, medical, zakat, housing)
- Save and load calculations
- Multi-currency support

## System Requirements

- {system.title()} operating system
- No additional software required (standalone executable)

## Support

For issues or questions, please contact the developer.

## Legal Notice

This calculator is based on Oman Personal Income Tax Law 2025.
Tax calculations are for informational purposes only.
Consult with a tax professional for official tax advice.
"""

    with open(pkg_dir / "README.txt", "w") as f:
        f.write(readme_content.strip())

    # Create ZIP package
    zip_path = f"{pkg_name}.zip"
    shutil.make_archive(pkg_name, 'zip', pkg_name)

    print(f"Package created: {zip_path}")
    return zip_path

def main():
    """Main build function"""
    print("Oman Tax Calculator - Package Builder")
    print("=" * 40)

    try:
        # Install dependencies
        print("Installing dependencies...")
        install_dependencies()

        # Build executable
        print("Building executable...")
        exe_path = build_with_pyinstaller()

        if not Path(exe_path).exists():
            print("Trying alternative build method...")
            build_with_cx_freeze()

        # Create distribution package
        print("Creating distribution package...")
        pkg_path = create_distribution_package()

        print(f"✅ Build completed successfully!")
        print(f"📦 Package: {pkg_path}")
        print(f"💻 Platform: {platform.system()} {platform.machine()}")

    except Exception as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()