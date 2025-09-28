"""
Setup script for creating standalone executables
"""

from cx_Freeze import setup, Executable
import sys
import os

# Dependencies
build_exe_options = {
    "packages": ["PyQt5", "json", "csv", "datetime", "pathlib"],
    "excludes": ["tkinter", "matplotlib", "numpy", "scipy"],
    "include_files": [],
    "zip_include_packages": "*",
    "zip_exclude_packages": ""
}

# Base for GUI applications
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Executable configuration
executables = [
    Executable(
        "oman_tax_calculator.py",
        base=base,
        target_name="OmanTaxCalculator",
        icon=None,  # Add icon file path if available
        shortcut_name="Oman Tax Calculator",
        shortcut_dir="DesktopFolder"
    )
]

setup(
    name="OmanTaxCalculator",
    version="1.0.0",
    description="Oman Personal Income Tax Calculator",
    author="Fahad Al-Maashani",
    options={"build_exe": build_exe_options},
    executables=executables
)