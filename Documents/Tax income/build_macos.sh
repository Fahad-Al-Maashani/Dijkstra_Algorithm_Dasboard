#!/bin/bash
# Build script for macOS

echo "Building Oman Tax Calculator for macOS..."

# Install dependencies
pip install -r requirements_build.txt

# Create standalone executable with PyInstaller
pyinstaller --onefile --windowed \
    --name "OmanTaxCalculator" \
    --clean \
    --distpath "./dist_macos" \
    oman_tax_calculator.py

# Create app bundle structure
mkdir -p "OmanTaxCalculator.app/Contents/MacOS"
mkdir -p "OmanTaxCalculator.app/Contents/Resources"

# Copy executable
cp "./dist_macos/OmanTaxCalculator" "OmanTaxCalculator.app/Contents/MacOS/"

# Create Info.plist
cat > "OmanTaxCalculator.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>OmanTaxCalculator</string>
    <key>CFBundleIdentifier</key>
    <string>com.fahad.omantaxcalculator</string>
    <key>CFBundleName</key>
    <string>Oman Tax Calculator</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Make executable
chmod +x "OmanTaxCalculator.app/Contents/MacOS/OmanTaxCalculator"

# Create distribution package
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    PKG_NAME="OmanTaxCalculator_macOS_M1"
else
    PKG_NAME="OmanTaxCalculator_macOS_Intel"
fi

# Create package directory
mkdir -p "$PKG_NAME"
cp -R "OmanTaxCalculator.app" "$PKG_NAME/"

# Create README
cat > "$PKG_NAME/README.txt" << EOF
# Oman Tax Calculator v1.0.0 for macOS

## Installation Instructions

1. Extract this package to your Applications folder
2. Double-click on OmanTaxCalculator.app to run

## Features

- Calculate personal income tax according to Oman Personal Income Tax Law 2025
- 5% flat rate on income above OMR 42,000
- Support for deductions (education, medical, zakat, housing)
- Save and load calculations

## System Requirements

- macOS 10.14 or later
- No additional software required

For issues, please contact the developer.
EOF

# Create ZIP package
zip -r "${PKG_NAME}.zip" "$PKG_NAME"

echo "✅ macOS package created: ${PKG_NAME}.zip"