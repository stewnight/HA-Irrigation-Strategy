# 🛠️ Complete Installation Guide (v2.1.0)

This step-by-step guide will help you install the Advanced AI Crop Steering System with new dynamic zone support. Even if you're new to Home Assistant, we'll walk you through every step!

## 🎯 What You'll Install

- **Crop Steering Integration**: Smart irrigation control with 1-6 dynamic zones
- **AI Modules**: Machine learning for predictive irrigation
- **Dashboard**: Real-time monitoring and analytics
- **Zone Configuration Tools**: Easy setup for any number of zones
- **AppDaemon**: Required for AI features

## 📋 Prerequisites

### Required Home Assistant Add-ons

**YOU MUST INSTALL THESE FIRST:**

1. **AppDaemon 4** (required for AI features)
   - Go to **Settings** → **Add-ons** → **Add-on Store**
   - Search for "AppDaemon 4"
   - Click **INSTALL**
   - Don't start it yet (we'll configure it first)

2. **File Editor** (makes editing files easy)
   - In Add-on Store, search for "File Editor"
   - Click **INSTALL** and **START**
   - Enable "Show in sidebar"

3. **Samba Share** (optional - for easy file access)
   - In Add-on Store, search for "Samba Share"
   - Click **INSTALL** and **START**

### Hardware Requirements

**Essential Hardware:**
- **VWC Sensors**: 1-2 per zone (flexible configuration)
- **EC Sensors**: 1-2 per zone (flexible configuration)
- **Irrigation Pump**: Relay-controlled with flow monitoring capability
- **Main Line Valve**: Solenoid valve for main water line control
- **Zone Valves**: 1-6 individual solenoid valves (you choose how many)
- **Reliable Network**: Stable WiFi/Ethernet for sensor communication

**Recommended Hardware:**
- **Environmental Sensors**: Temperature, humidity, VPD monitoring
- **Flow Meters**: Water usage tracking for each zone
- **Pressure Sensors**: System pressure monitoring
- **pH Sensors**: Water quality monitoring (optional)

### Software Requirements

**Home Assistant Version:**
- Home Assistant >= 2024.3.0 (check in Settings → About)

**Required Add-ons** (install these first!):
- AppDaemon 4
- File Editor (for easy file editing)
- Samba Share (optional, for network file access)

**System Requirements:**
- **Minimum RAM**: 4GB (8GB recommended for AI features)
- **Storage**: 1GB free space for system and AI data
- **CPU**: Any multi-core processor (Raspberry Pi 4+ works fine)

**AI Features Require:**
- Python packages (we'll install these automatically)
- AppDaemon configured and running
- Integration properly set up

## 🚀 Step-by-Step Installation

### Step 1: Fix AppDaemon Requirements (NEW - IMPORTANT!)

**Before anything else, we need to fix a compatibility issue:**

1. **Download the fix script** from your Home Assistant config directory
2. **Run the fix:**
   ```bash
   ./fix_appdaemon_requirements.sh
   ```
3. **This prevents AppDaemon from trying to install scikit-learn** (which causes errors)

> **Why?** The system uses scipy-based mathematical models instead of scikit-learn for better compatibility with Home Assistant OS containers.

### Step 2: Install the Integration via HACS

**1.1: Add Custom Repository**
1. Open **HACS** in Home Assistant sidebar
2. Click **Integrations**
3. Click the **three dots menu (⋮)** in top-right corner
4. Select **"Custom repositories"**
5. Enter these details:
   ```
   Repository: https://github.com/JakeTheRabbit/HA-Irrigation-Strategy
   Category: Integration
   ```
6. Click **"ADD"** and wait for validation

**1.2: Install the Integration**
1. In **HACS** → **Integrations**
2. Search for **"Crop Steering"**
3. Click on **"Crop Steering System"**
4. Click **"DOWNLOAD"**
5. Select latest version and click **"DOWNLOAD"** again
6. **RESTART HOME ASSISTANT** when prompted

### Step 2: Configure AppDaemon (Required for AI)

**⚠️ IMPORTANT:** HACS only installs the basic integration. For AI features, you MUST configure AppDaemon!

**2.1: Create Long-Lived Access Token**
1. Go to **Settings** → **People** → **Users**
2. Click your username
3. Scroll to **"Long-lived access tokens"**
4. Click **"CREATE TOKEN"**
5. Name it "AppDaemon Crop Steering"
6. **COPY THE TOKEN** (you can't see it again!)

**2.2: Configure AppDaemon**
1. Go to **Settings** → **Add-ons** → **AppDaemon 4**
2. Click **Configuration** tab
3. Replace the configuration with:
   ```yaml
   system_packages: []
   python_packages:
     - numpy
     - pandas
     - plotly
     - scikit-learn 
     - scipy
   init_commands: []
   ```
4. Click **SAVE**
5. Go to **Info** tab and click **START**
6. Enable **"Start on boot"** and **"Show in sidebar"**

**2.3: Configure AppDaemon Connection**
1. Open **File Editor** from sidebar
2. Navigate to `/config/appdaemon/appdaemon.yaml`
3. Replace contents with:
   ```yaml
   secrets: /config/secrets.yaml
   appdaemon:
     latitude: 40.8939
     longitude: -74.0455
     elevation: 100
     time_zone: America/New_York
     plugins:
       HASS:
         type: hass
         ha_url: http://homeassistant.local:8123
         token: YOUR_LONG_LIVED_TOKEN_HERE
   http:
     url: http://0.0.0.0:5050
   admin:
   api:
   hadashboard:
   ```
4. Replace `YOUR_LONG_LIVED_TOKEN_HERE` with token from step 2.1
5. Update `time_zone` to your location
6. Click **SAVE**

### Step 3: Configure Your Zones (NEW - Easy Setup!)

**3.1: Download and Run Zone Configuration Helper**
1. Go to: https://github.com/JakeTheRabbit/HA-Irrigation-Strategy
2. Click **"Code"** → **"Download ZIP"**
3. Extract the ZIP file on your computer
4. Using **Samba Share** or **File Editor**:
   - Copy `zone_configuration_helper.py` to `/config/zone_configuration_helper.py`
   - Copy `crop_steering.env` to `/config/crop_steering.env`

**3.2: Run Interactive Zone Setup**
1. Open **Terminal** in Home Assistant (or SSH)
2. Navigate to config directory:
   ```bash
   cd /config
   ```
3. Run the zone configuration helper:
   ```bash
   python3 zone_configuration_helper.py
   ```
4. **Follow the interactive prompts:**
   - Choose number of zones (1-6)
   - Enter entity IDs for zone switches
   - Configure VWC and EC sensors for each zone
   - The script validates everything and updates your config

**3.3: Install AppDaemon AI Modules**
1. Using **Samba Share** or **File Editor**:
   - Copy `appdaemon/apps/apps.yaml` to `/config/appdaemon/apps/apps.yaml`
   - Copy entire `appdaemon/apps/crop_steering/` folder to `/config/appdaemon/apps/crop_steering/`

**3.4: Restart AppDaemon**
1. Go to **Settings** → **Add-ons** → **AppDaemon 4**
2. Click **RESTART**
3. Check **Log** tab for "Master Crop Steering Application" startup message

### Step 4: Add the Integration (Easy!)

**4.1: Add the Integration - Two Methods**

**Method A: Automatic Configuration (Recommended)**
1. **Restart Home Assistant** (Settings → System → Restart)
2. After restart, go to **Settings** → **Devices & Services**  
3. Click **"+ ADD INTEGRATION"** (bottom right)
4. Search for **"Crop Steering"**
5. Click **"Crop Steering System"**
6. **Select "Load from crop_steering.env"**
7. System automatically reads your zone configuration and creates all entities!

**Method B: Manual UI Configuration**
1. Follow steps 1-5 above
2. **Select "Manual Zone Configuration"**
3. Choose number of zones (1-6)
4. Enter switch entity IDs for each zone
5. System creates basic entities (sensors configured separately)

**4.2: Verify Entities Created**
After integration setup, check that entities were created:
1. Go to **Settings** → **Devices & Services** → **Crop Steering System**
2. You should see entities like:
   - `switch.crop_steering_zone_1_enabled`
   - `sensor.crop_steering_vwc_zone_1`
   - `sensor.crop_steering_ec_zone_1`
   - Plus many more for each zone!

**4.3: Test Basic Operation**
1. Go to **Developer Tools** → **Services**
2. Test zone enable: Call `switch.turn_on` with `switch.crop_steering_zone_1_enabled`
3. Check sensors are reading values in **Developer Tools** → **States**

## ⚙️ Final Configuration

### Step 5: Configure Crop Profile and Settings

Now that your zones are set up, configure the system parameters:

1. **Go to your integration settings:**
   - **Settings** → **Devices & Services** → **Crop Steering System**
   - Click **"CONFIGURE"**

2. **Select your crop profile:**
   - Cannabis_Athena (high EC methodology)
   - Cannabis_Hybrid (balanced parameters)
   - Cannabis_Indica/Sativa (strain-specific)
   - Tomato, Lettuce, Custom

3. **Adjust parameters if needed:**
   - Substrate volume per zone
   - Dripper flow rates
   - EC and VWC targets
   - Most defaults work well to start!

### Step 6: Verify Everything is Working

**6.1: Check the Dashboard**
1. Go to **Settings** → **Devices & Services**
2. Find **"Crop Steering System"** and click **CONFIGURE**
3. Enter your sensor entity names:
   ```
   VWC Sensors (Zone 1):
   - sensor.vwc_r1_front
   - sensor.vwc_r1_back
   
   EC Sensors (Zone 1):
   - sensor.ec_r1_front  
   - sensor.ec_r1_back
   
   (Add more zones as needed)
   ```
4. **TIP:** Use the entity names from your .env file

**6.2: Hardware Configuration**
In the integration setup, configure:
```
Pump Switch: switch.your_pump_name
Main Line Valve: switch.your_main_valve  
Zone 1 Valve: switch.your_zone_1_valve
Zone 2 Valve: switch.your_zone_2_valve
(etc.)
```

### Step 7: Verify Installation

**7.1: Check Integration Entities**
1. Go to **Developer Tools** → **States**
2. Filter by `crop_steering`
3. You should see entities like:
   ```
   sensor.crop_steering_system_state
   sensor.crop_steering_current_phase  
   sensor.crop_steering_fused_vwc
   sensor.crop_steering_ml_confidence
   ```

**7.2: Check AppDaemon Status**
1. Go to **Settings** → **Add-ons** → **AppDaemon 4**
2. Click **Log** tab
3. Look for: `"Master Crop Steering Application initialized!"`
4. If you see errors, check the troubleshooting section below

**7.3: Test Hardware (OPTIONAL)**
1. Go to **Developer Tools** → **Services**
2. **CAREFULLY** test your pump:
   - Service: `switch.turn_on`
   - Entity: Your pump entity name
   - Click **CALL SERVICE**
   - **IMMEDIATELY turn it back off!**

## ✅ You're Done!

**Congratulations!** Your Advanced AI Crop Steering System is now installed and ready to use.

### What Happens Next?

1. **Learning Phase** (Week 1-3):
   - AI models start learning your system
   - Irrigation becomes more intelligent over time
   - Monitor the dashboard for improvements

2. **Check Your Dashboard**:
   - Look for `sensor.crop_steering_dashboard_html` entity
   - Add it to your Home Assistant dashboard
   - Watch real-time irrigation analytics!

3. **Monitor Performance**:
   - ML confidence should improve to 80%+ over 2-3 weeks
   - Irrigation efficiency should increase
   - Water usage should optimize automatically

### 🎯 Quick Start Guide

1. **Enable the system**: Turn on `switch.crop_steering_system_enabled`
2. **Monitor sensors**: Check VWC and EC readings are normal
3. **Watch the AI learn**: ML confidence will improve daily
4. **Enjoy automation**: System will irrigate intelligently!

## 🔧 Advanced Configuration (Optional)

### Crop Profile Selection

You already chose this during setup, but you can change it:

**Cannabis Profiles:**
- **Cannabis_Athena**: High-EC Athena methodology (most popular)
- **Cannabis_Indica_Dominant**: Higher moisture, shorter plants  
- **Cannabis_Sativa_Dominant**: Lower moisture, taller plants
- **Cannabis_Balanced_Hybrid**: 50/50 genetics

**Other Crops:**
- **Tomato_Hydroponic**: Continuous production
- **Lettuce_Leafy_Greens**: Low-stress cultivation

### Growth Stage Changes

Update as your plants grow:
- **Seedling**: Gentle parameters for young plants
- **Vegetative**: Aggressive growth phase
- **Early Flower**: Transition to flowering
- **Late Flower**: Maximum generative stress

### Zone Configuration

Adjust zone settings in integration configuration:
- **Zone Volume**: Substrate volume per zone (liters)
- **Substrate Type**: Affects sensor calibration
- **Active Zones**: Enable/disable zones as needed

---

## 🚫 Common Mistakes to Avoid

### ⚠️ DON'T Skip AppDaemon Setup
- **HACS only installs the integration**
- **AI features require AppDaemon configuration**
- **Missing this = no AI, no dashboard, no advanced features**

### ⚠️ DON'T Forget the Long-Lived Token
- AppDaemon needs this to communicate with Home Assistant
- Without it, AI modules won't start
- Create it BEFORE configuring AppDaemon

### ⚠️ DON'T Use Wrong Entity Names
- Use **Developer Tools** → **States** to find exact names
- Copy/paste entity IDs exactly
- Case-sensitive!

### ⚠️ DON'T Test Hardware Carelessly
- **ALWAYS** have manual shutoff available
- **TEST SLOWLY** - start with pump only
- **TURN OFF IMMEDIATELY** after testing
- **NEVER** leave irrigation running unattended during setup


## 🚫 Troubleshooting

### ❌ Integration Not Found in Home Assistant

**Problem:** Can't find "Crop Steering" in Add Integration

**Solution:**
1. **Check HACS installation worked:**
   - File Editor → `/config/custom_components/crop_steering/`
   - Should contain files like `__init__.py`, `manifest.json`
2. **If missing:** Re-download from HACS
3. **Restart Home Assistant** after HACS installation

### ❌ AppDaemon Shows Errors

**Problem:** AppDaemon log shows import errors or Python package errors

**Solution:**
1. **Check AppDaemon Configuration:**
   - Settings → Add-ons → AppDaemon 4 → Configuration
   - Ensure Python packages listed:
     ```yaml
     python_packages:
       - numpy
       - pandas
       - plotly
       - scikit-learn
       - scipy
     ```
2. **Restart AppDaemon** after config changes
3. **Check logs again** for "Master Crop Steering" startup message

### ❌ No AI Features Working

**Problem:** Integration works but no ML predictions, no advanced dashboard

**Likely Cause:** AppDaemon not configured properly

**Solution:**
1. **Verify AppDaemon is running:**
   - Settings → Add-ons → AppDaemon 4 → should show "STARTED"
2. **Check connection to Home Assistant:**
   - AppDaemon log should show "Connected to Home Assistant"
3. **Verify long-lived token is correct**
4. **Check AI files were copied:**
   - File Editor → `/config/appdaemon/apps/crop_steering/`
   - Should contain `.py` files

### ❌ Sensors Not Working

**Problem:** Integration can't find your sensors

**Solution:**
1. **Find exact entity names:**
   - Developer Tools → States
   - Search for your sensor names
   - Copy the EXACT entity_id
2. **Update integration configuration:**
   - Settings → Devices & Services → Crop Steering → Configure
   - Paste exact entity names
3. **Check sensors are online:**
   - Entity should show current value, not "unavailable"

### ❌ Hardware Testing Fails

**Problem:** Pump/valves don't respond to manual tests

**Solution:**
1. **Check entity names exactly match your hardware**
2. **Verify devices are powered and connected**
3. **Test with original Home Assistant controls first**
4. **Check relay wiring and power supply**

### 📞 Need More Help?

**GitHub Issues:** [Report bugs here](https://github.com/JakeTheRabbit/HA-Irrigation-Strategy/issues)

**Include in your report:**
- Home Assistant version
- AppDaemon version  
- Full error logs
- Your hardware setup
- Steps that failed

---

## 🎉 Installation Complete!

**You now have:**
- ✅ Smart irrigation integration
- ✅ AI-powered decision making
- ✅ Real-time monitoring dashboard  
- ✅ Predictive analytics
- ✅ Professional-grade automation

### 📚 Next Steps:
1. **Read the [AI Operation Guide](ai_operation_guide.md)** - Learn how to use your new system
2. **Check the [Dashboard Guide](dashboard_guide.md)** - Understand the monitoring interface
3. **Monitor your first week** - Watch the AI learn your system

### 📞 Support:
- **Problems?** [GitHub Issues](https://github.com/JakeTheRabbit/HA-Irrigation-Strategy/issues)
- **Questions?** [Home Assistant Community](https://community.home-assistant.io/)
- **Advanced Help:** [Troubleshooting Guide](troubleshooting.md)

**Enjoy your intelligent irrigation system!** 🌱🤖