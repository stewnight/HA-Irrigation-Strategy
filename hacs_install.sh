#!/bin/bash

# ================================================================
# CROP STEERING SYSTEM - HACS POST-INSTALL SCRIPT
# ================================================================
# This script automatically configures the system after HACS download
# ================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌱 Crop Steering System - HACS Post-Install Setup${NC}"
echo "================================================================"

# Default paths
HA_CONFIG_DIR="/config"
HACS_DOWNLOAD_DIR="/config/appdaemon/apps/HA-Irrigation-Strategy"

# Check if HACS downloaded the files
if [ ! -d "$HACS_DOWNLOAD_DIR" ]; then
    echo -e "${RED}❌ HACS download directory not found at $HACS_DOWNLOAD_DIR${NC}"
    echo "Please install via HACS first:"
    echo "HACS > Automation > Custom repositories"
    echo "Repository: https://github.com/JakeTheRabbit/HA-Irrigation-Strategy"
    echo "Category: AppDaemon"
    exit 1
fi

echo -e "${GREEN}✓ Found HACS download directory${NC}"

# Create packages directory if it doesn't exist
PACKAGES_DIR="$HA_CONFIG_DIR/packages"
if [ ! -d "$PACKAGES_DIR" ]; then
    echo "📁 Creating packages directory..."
    mkdir -p "$PACKAGES_DIR"
fi

# Move packages to correct location
echo "📦 Moving package files to correct location..."
if [ -d "$HACS_DOWNLOAD_DIR/packages/CropSteering" ]; then
    cp -r "$HACS_DOWNLOAD_DIR/packages/CropSteering" "$PACKAGES_DIR/"
    echo -e "${GREEN}✓ Package files moved to $PACKAGES_DIR/CropSteering${NC}"
else
    echo -e "${RED}❌ Package files not found in HACS download${NC}"
    exit 1
fi

# Set up AppDaemon files (if AppDaemon exists)
if [ -d "$HA_CONFIG_DIR/appdaemon" ]; then
    echo "🐍 Setting up AppDaemon files..."
    if [ -d "$HACS_DOWNLOAD_DIR/appdaemon" ]; then
        cp -r "$HACS_DOWNLOAD_DIR/appdaemon/"* "$HA_CONFIG_DIR/appdaemon/"
        echo -e "${GREEN}✓ AppDaemon files configured${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  AppDaemon directory not found - advanced features will be disabled${NC}"
fi

# Copy configuration files
echo "⚙️  Setting up configuration files..."
cp "$HACS_DOWNLOAD_DIR/crop_steering.env" "$HA_CONFIG_DIR/crop_steering.env.example"
cp "$HACS_DOWNLOAD_DIR/configure_crop_steering.py" "$HA_CONFIG_DIR/"
chmod +x "$HA_CONFIG_DIR/configure_crop_steering.py"
echo -e "${GREEN}✓ Configuration files copied${NC}"

# Check configuration.yaml
CONFIG_FILE="$HA_CONFIG_DIR/configuration.yaml"
if [ -f "$CONFIG_FILE" ]; then
    if ! grep -q "packages:" "$CONFIG_FILE"; then
        echo -e "${YELLOW}⚠️  Adding packages configuration to configuration.yaml${NC}"
        echo "" >> "$CONFIG_FILE"
        echo "# Crop Steering System" >> "$CONFIG_FILE"
        echo "homeassistant:" >> "$CONFIG_FILE"
        echo "  packages:" >> "$CONFIG_FILE"
        echo "    crop_steering: !include packages/CropSteering/crop_steering_package.yaml" >> "$CONFIG_FILE"
        echo -e "${GREEN}✓ Added package configuration${NC}"
    else
        echo -e "${YELLOW}⚠️  Please manually add this line to your configuration.yaml packages section:${NC}"
        echo "    crop_steering: !include packages/CropSteering/crop_steering_package.yaml"
    fi
fi

# Clean up HACS download directory
echo "🧹 Cleaning up HACS download directory..."
rm -rf "$HACS_DOWNLOAD_DIR"
echo -e "${GREEN}✓ Cleanup complete${NC}"

# Installation complete
echo ""
echo -e "${GREEN}🎉 HACS Installation Complete!${NC}"
echo "================================================================"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Copy and edit your configuration:"
echo "   cp $HA_CONFIG_DIR/crop_steering.env.example $HA_CONFIG_DIR/my_crop_steering.env"
echo "   nano $HA_CONFIG_DIR/my_crop_steering.env"
echo ""
echo "2. Run the configuration script:"
echo "   cd $HA_CONFIG_DIR"
echo "   python configure_crop_steering.py my_crop_steering.env"
echo ""
echo "3. Restart Home Assistant"
echo ""
echo "4. Add the dashboard card to your Home Assistant dashboard:"
echo "   !include packages/CropSteering/cards/crop_steering_dashboard.yaml"
echo ""
echo -e "${GREEN}🌱 Your professional crop steering system is ready!${NC}"