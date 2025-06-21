#!/bin/bash
# Fix AppDaemon scikit-learn installation issue
# This script removes scikit-learn requirements and uses scipy-based models

echo "🔧 Fixing AppDaemon requirements..."

# Create custom AppDaemon requirements without scikit-learn
cat > /config/appdaemon/requirements.txt << EOF
# Advanced AI Crop Steering System - AppDaemon Requirements
# These packages are needed for the AI modules
# Note: scikit-learn is NOT needed - we use scipy-based models

numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0
plotly>=5.0.0
requests>=2.25.0
EOF

echo "✅ Created custom requirements.txt without scikit-learn"

# If running in AppDaemon container, install packages
if [ -f /usr/src/app/appdaemon.py ]; then
    echo "📦 Installing packages in AppDaemon container..."
    pip install --no-cache-dir -r /config/appdaemon/requirements.txt
    echo "✅ Packages installed successfully"
fi

echo "🎉 AppDaemon requirements fixed!"
echo ""
echo "📝 Next steps:"
echo "1. Restart AppDaemon add-on"
echo "2. Check AppDaemon logs for any errors"
echo "3. The system will use scipy-based mathematical models instead of scikit-learn"