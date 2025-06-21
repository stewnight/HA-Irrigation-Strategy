#!/bin/bash
# Fix AppDaemon scikit-learn installation issue
# Updated for AppDaemon v15+ directory structure

echo "🔧 Fixing AppDaemon requirements for v15+..."

# Check if new AppDaemon directory exists
if [ -d "/addon_configs/a0d7b954_appdaemon" ]; then
    APPDAEMON_DIR="/addon_configs/a0d7b954_appdaemon"
    echo "📁 Using AppDaemon v15+ directory: $APPDAEMON_DIR"
elif [ -d "/config/appdaemon" ]; then
    APPDAEMON_DIR="/config/appdaemon"
    echo "📁 Using legacy AppDaemon directory: $APPDAEMON_DIR"
else
    echo "❌ Error: AppDaemon directory not found!"
    echo "Please install AppDaemon 4 add-on first."
    exit 1
fi

# Create custom AppDaemon requirements without scikit-learn
cat > "$APPDAEMON_DIR/requirements.txt" << EOF
# Advanced AI Crop Steering System - AppDaemon Requirements
# Updated for AppDaemon v15+ compatibility
# Note: scikit-learn is NOT needed - we use scipy-based models

numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0
plotly>=5.0.0
requests>=2.25.0
EOF

echo "✅ Created custom requirements.txt without scikit-learn"
echo "📍 Location: $APPDAEMON_DIR/requirements.txt"

# If running in AppDaemon container, install packages
if [ -f /usr/src/app/appdaemon.py ]; then
    echo "📦 Installing packages in AppDaemon container..."
    pip install --no-cache-dir -r "$APPDAEMON_DIR/requirements.txt"
    echo "✅ Packages installed successfully"
fi

echo "🎉 AppDaemon requirements fixed!"
echo ""
echo "📝 Next steps:"
echo "1. Restart AppDaemon add-on"
echo "2. Check AppDaemon logs for any errors"
echo "3. The system will use scipy-based mathematical models instead of scikit-learn"
echo ""
echo "🔍 AppDaemon v15+ Paths:"
echo "- Config: $APPDAEMON_DIR/appdaemon.yaml"
echo "- Apps: $APPDAEMON_DIR/apps/"
echo "- Samba: \\\\YOUR_HA_IP\\addon_configs\\a0d7b954_appdaemon"