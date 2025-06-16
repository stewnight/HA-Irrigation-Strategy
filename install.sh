#!/bin/bash

# ================================================================
# CROP STEERING SYSTEM - AUTOMATIC INSTALLER
# ================================================================
# This script automatically installs the Crop Steering System
# into your Home Assistant instance.
# ================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default paths
HA_CONFIG_DIR="/config"
APPDAEMON_DIR="/config/appdaemon"

echo -e "${BLUE}🌱 Crop Steering System Installer${NC}"
echo "================================================================"

# Check if running in Home Assistant environment
if [ ! -d "$HA_CONFIG_DIR" ]; then
    echo -e "${YELLOW}⚠️  Home Assistant config directory not found at $HA_CONFIG_DIR${NC}"
    read -p "Enter your Home Assistant config directory path: " HA_CONFIG_DIR
    
    if [ ! -d "$HA_CONFIG_DIR" ]; then
        echo -e "${RED}❌ Directory $HA_CONFIG_DIR does not exist${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Found Home Assistant config directory: $HA_CONFIG_DIR${NC}"

# Create packages directory if it doesn't exist
PACKAGES_DIR="$HA_CONFIG_DIR/packages"
if [ ! -d "$PACKAGES_DIR" ]; then
    echo "📁 Creating packages directory..."
    mkdir -p "$PACKAGES_DIR"
fi

# Copy crop steering package
echo "📦 Installing Crop Steering package..."
cp -r packages/CropSteering "$PACKAGES_DIR/"
echo -e "${GREEN}✓ Package files copied${NC}"

# Install AppDaemon app (optional)
read -p "Do you want to install the AppDaemon app for advanced features? (y/N): " install_appdaemon
if [[ $install_appdaemon =~ ^[Yy]$ ]]; then
    if [ ! -d "$APPDAEMON_DIR" ]; then
        echo "📁 Creating AppDaemon directory..."
        mkdir -p "$APPDAEMON_DIR"
    fi
    
    echo "🐍 Installing AppDaemon app..."
    cp -r appdaemon/* "$APPDAEMON_DIR/"
    echo -e "${GREEN}✓ AppDaemon app installed${NC}"
fi

# Copy configuration template
echo "⚙️  Setting up configuration template..."
cp crop_steering.env "$HA_CONFIG_DIR/crop_steering.env.example"
echo -e "${GREEN}✓ Configuration template copied${NC}"

# Install configuration script
echo "🔧 Installing configuration script..."
cp configure_crop_steering.py "$HA_CONFIG_DIR/"
chmod +x "$HA_CONFIG_DIR/configure_crop_steering.py"
echo -e "${GREEN}✓ Configuration script installed${NC}"

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

# Installation complete
echo ""
echo -e "${GREEN}🎉 Installation Complete!${NC}"
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