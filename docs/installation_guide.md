# 🛠️ Complete Installation Guide

This comprehensive guide covers the complete installation of the Advanced AI Crop Steering System from initial requirements through final testing.

## 📋 Prerequisites

### Hardware Requirements

**Essential Hardware:**
- **VWC Sensors**: 2+ per zone (minimum 6 total for 3 zones)
- **EC Sensors**: 2+ per zone (minimum 6 total for 3 zones)
- **Irrigation Pump**: Relay-controlled with flow monitoring capability
- **Main Line Valve**: Solenoid valve for main water line control
- **Zone Valves**: Individual solenoid valves for each irrigation zone
- **Reliable Network**: Stable WiFi/Ethernet for sensor communication

**Recommended Hardware:**
- **Environmental Sensors**: Temperature, humidity, VPD monitoring
- **Flow Meters**: Water usage tracking for each zone
- **Pressure Sensors**: System pressure monitoring
- **pH Sensors**: Water quality monitoring (optional)

### Software Requirements

**Core Dependencies:**
```bash
# Python packages (required for AI features)
numpy>=1.21.0
pandas>=1.3.0
plotly>=5.0.0
scikit-learn>=1.0.0
scipy>=1.7.0

# Home Assistant
Home Assistant >= 2024.3.0
AppDaemon >= 4.2.0 (for AI features)
```

**System Requirements:**
- **Minimum RAM**: 4GB (8GB recommended for AI features)
- **Storage**: 500MB for system files, 2GB+ for data storage
- **CPU**: Multi-core processor recommended for ML operations
- **Python**: 3.8+ with pip package manager

## 🚀 Installation Methods

### Option 1: HACS Installation (Recommended)

This is the easiest method for most users.

#### Step 1: Add Custom Repository

1. **Open HACS in Home Assistant:**
   - Navigate to **HACS** → **Integrations**
   - Click the **three dots menu (⋮)** in the top right corner
   - Select **"Custom repositories"**

2. **Add the repository:**
   ```
   Repository URL: https://github.com/JakeTheRabbit/HA-Irrigation-Strategy
   Category: Integration
   ```
   - Click **"ADD"**
   - Wait for HACS to validate (this may take a few minutes)

#### Step 2: Install Integration

1. **Find the integration:**
   - Go to **HACS** → **Integrations**
   - Search for **"Advanced Crop Steering System"** or **"Crop Steering"**
   - Click on the integration

2. **Download and install:**
   - Click **"Download"**
   - Select the latest version
   - Click **"Download"** again
   - **Restart Home Assistant** when prompted

#### Step 3: Install Python Dependencies

```bash
# SSH into your Home Assistant system
# For Home Assistant OS:
ssh root@homeassistant.local

# Install required packages
pip install numpy pandas plotly scikit-learn scipy

# For Home Assistant Supervised/Container:
docker exec -it homeassistant bash
pip install numpy pandas plotly scikit-learn scipy
```

#### Step 4: Install AppDaemon Apps

```bash
# Copy AppDaemon configuration
cd /config
wget https://raw.githubusercontent.com/JakeTheRabbit/HA-Irrigation-Strategy/main/appdaemon/apps/apps.yaml
mv apps.yaml /config/appdaemon/apps/

# Download and extract AppDaemon modules
wget https://github.com/JakeTheRabbit/HA-Irrigation-Strategy/archive/main.zip
unzip main.zip
cp -r HA-Irrigation-Strategy-main/appdaemon/apps/crop_steering /config/appdaemon/apps/
rm -rf HA-Irrigation-Strategy-main main.zip
```

### Option 2: Manual Installation

For advanced users who prefer manual control.

#### Step 1: Download System

```bash
# Clone the repository
git clone https://github.com/JakeTheRabbit/HA-Irrigation-Strategy.git
cd HA-Irrigation-Strategy

# Or download as ZIP
wget https://github.com/JakeTheRabbit/HA-Irrigation-Strategy/archive/main.zip
unzip main.zip
cd HA-Irrigation-Strategy-main
```

#### Step 2: Install Integration Files

```bash
# Copy integration to Home Assistant
cp -r custom_components/crop_steering /config/custom_components/

# Set proper permissions
chmod -R 755 /config/custom_components/crop_steering
chown -R homeassistant:homeassistant /config/custom_components/crop_steering
```

#### Step 3: Install AppDaemon Apps

```bash
# Copy AppDaemon configuration
cp appdaemon/apps/apps.yaml /config/appdaemon/apps/
cp -r appdaemon/apps/crop_steering /config/appdaemon/apps/

# Set proper permissions
chmod -R 755 /config/appdaemon/apps/crop_steering
chown -R homeassistant:homeassistant /config/appdaemon/apps/
```

#### Step 4: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Or install individually
pip install numpy pandas plotly scikit-learn scipy
```

### Option 3: Docker Installation

For containerized deployments.

#### Step 1: Create Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  homeassistant:
    container_name: homeassistant
    image: ghcr.io/home-assistant/home-assistant:stable
    volumes:
      - /path/to/config:/config
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    privileged: true
    network_mode: host
    
  appdaemon:
    container_name: appdaemon
    image: acockburn/appdaemon:latest
    volumes:
      - /path/to/config/appdaemon:/conf
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    depends_on:
      - homeassistant
    environment:
      - HA_URL=http://localhost:8123
      - TOKEN=your_long_lived_access_token
```

#### Step 2: Install System

```bash
# Start containers
docker-compose up -d

# Install integration
docker exec homeassistant bash -c "
cd /config &&
wget https://github.com/JakeTheRabbit/HA-Irrigation-Strategy/archive/main.zip &&
unzip main.zip &&
cp -r HA-Irrigation-Strategy-main/custom_components/crop_steering custom_components/ &&
rm -rf HA-Irrigation-Strategy-main main.zip
"

# Install AppDaemon apps
docker exec appdaemon bash -c "
cd /conf &&
wget https://github.com/JakeTheRabbit/HA-Irrigation-Strategy/archive/main.zip &&
unzip main.zip &&
cp -r HA-Irrigation-Strategy-main/appdaemon/apps/* apps/ &&
rm -rf HA-Irrigation-Strategy-main main.zip
"

# Install Python dependencies
docker exec appdaemon pip install numpy pandas plotly scikit-learn scipy
```

## ⚙️ Configuration

### Step 1: Add Integration

1. **Restart Home Assistant** after installation
2. **Go to Settings** → **Devices & Services**
3. **Click "Add Integration"**
4. **Search for "Crop Steering"** or "Advanced Crop Steering System"
5. **Click to add the integration**

### Step 2: Configure Sensors

Configure your sensor entities:

```yaml
# Example configuration
VWC Sensors (Zone 1):
- sensor.vwc_r1_front
- sensor.vwc_r1_back

VWC Sensors (Zone 2):
- sensor.vwc_r2_front
- sensor.vwc_r2_back

VWC Sensors (Zone 3):
- sensor.vwc_r3_front
- sensor.vwc_r3_back

EC Sensors (Zone 1):
- sensor.ec_r1_front
- sensor.ec_r1_back

EC Sensors (Zone 2):
- sensor.ec_r2_front
- sensor.ec_r2_back

EC Sensors (Zone 3):
- sensor.ec_r3_front
- sensor.ec_r3_back
```

### Step 3: Configure Hardware

Configure your irrigation hardware:

```yaml
# Hardware configuration
Irrigation Pump:
- switch.f1_irrigation_pump_master_switch

Main Line Valve:
- switch.espoe_irrigation_relay_1_2

Zone Valves:
- Zone 1: switch.f1_irrigation_relays_relay_1
- Zone 2: switch.f1_irrigation_relays_relay_2
- Zone 3: switch.f1_irrigation_relays_relay_3

Optional Environmental:
- Temperature: sensor.grow_room_temperature
- Humidity: sensor.grow_room_humidity
- VPD: sensor.grow_room_vpd
```

### Step 4: Configure AppDaemon

1. **Edit AppDaemon configuration:**
   ```yaml
   # /config/appdaemon/apps/apps.yaml
   master_crop_steering:
     module: crop_steering.master_crop_steering_app
     class: MasterCropSteeringApp
     dependencies:
       - crop_steering_dashboard
     log: crop_steering_master

   crop_steering_dashboard:
     module: crop_steering.advanced_crop_steering_dashboard
     class: AdvancedCropSteeringDashboard
     log: crop_steering_dashboard
   ```

2. **Create AppDaemon secrets (if needed):**
   ```yaml
   # /config/appdaemon/secrets.yaml
   ha_url: http://homeassistant.local:8123
   ha_token: your_long_lived_access_token
   ```

3. **Restart AppDaemon**

## 🔧 Initial Configuration

### Step 1: Select Crop Profile

1. **Go to integration settings**
2. **Choose crop profile:**
   - **Cannabis_Athena**: High-EC Athena methodology
   - **Cannabis_Indica_Dominant**: Higher moisture, shorter plants
   - **Cannabis_Sativa_Dominant**: Lower moisture, taller plants
   - **Cannabis_Balanced_Hybrid**: 50/50 genetics
   - **Tomato_Hydroponic**: Continuous production
   - **Lettuce_Leafy_Greens**: Low-stress cultivation

### Step 2: Set Growth Stage

Configure current growth stage:
- **Seedling**: Young plants, gentle parameters
- **Vegetative**: Aggressive growth, higher moisture
- **Early Flower**: Transition to flowering
- **Late Flower**: Maximum generative stress

### Step 3: Configure Zones

Enable and configure active zones:
```yaml
Zone Configuration:
- Zone 1: Active (Main canopy area)
- Zone 2: Active (Secondary growth area)
- Zone 3: Inactive (Not currently used)

Substrate Volume (per zone):
- 10 liters (adjust based on your setup)

Substrate Type:
- Coco Coir (affects calibration)
```

## 🧪 Testing & Validation

### Step 1: Sensor Validation

Test all sensors are working:

```bash
# Check sensor status
# Go to Developer Tools > States
# Filter by your sensor entities

# Example expected values:
sensor.vwc_r1_front: 45-70%
sensor.ec_r1_front: 2.0-6.0 mS/cm
sensor.grow_room_temperature: 20-30°C
```

### Step 2: Hardware Testing

Test irrigation hardware:

1. **Manual Hardware Test:**
   ```yaml
   # Test pump
   service: switch.turn_on
   target:
     entity_id: switch.f1_irrigation_pump_master_switch
   
   # Test main line (with pump running)
   service: switch.turn_on
   target:
     entity_id: switch.espoe_irrigation_relay_1_2
   
   # Test zone valve (with pump and main line on)
   service: switch.turn_on
   target:
     entity_id: switch.f1_irrigation_relays_relay_1
   ```

2. **Verify sequence:**
   - Pump starts first
   - Main line opens
   - Zone valve opens
   - Water flows correctly
   - All valves close in reverse order

### Step 3: AI System Testing

Verify AI modules are working:

```bash
# Check AppDaemon logs
tail -f /config/appdaemon/logs/crop_steering_master.log

# Expected startup messages:
# "Master Crop Steering Application with Advanced AI Features initialized!"
# "Advanced AI modules initialized successfully"
# "Intelligent Crop Profiles initialized with X base profiles"
```

### Step 4: Integration Testing

Verify integration entities:

```yaml
# Check these entities exist and have values:
sensor.crop_steering_system_state: active
sensor.crop_steering_current_phase: P2
sensor.crop_steering_fused_vwc: 45-70%
sensor.crop_steering_ml_confidence: 0.3-0.5 (initially)
sensor.crop_steering_sensor_health: improving
```

## 📊 Monitoring Setup

### Step 1: Dashboard Creation

Create monitoring dashboard:

```yaml
# Add to your dashboard
type: entities
title: Crop Steering AI System
entities:
  - sensor.crop_steering_system_state
  - sensor.crop_steering_current_phase
  - sensor.crop_steering_ml_irrigation_need
  - sensor.crop_steering_fused_vwc
  - sensor.crop_steering_dryback_percentage
  - sensor.crop_steering_sensor_health
```

### Step 2: Alerts Configuration

Set up critical alerts:

```yaml
# automation.yaml
- id: crop_steering_emergency
  alias: Crop Steering Emergency Alert
  trigger:
    - platform: numeric_state
      entity_id: sensor.crop_steering_fused_vwc
      below: 35
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "🚨 Crop Steering Emergency"
        message: "Critical VWC level: {{ trigger.to_state.state }}%"
        data:
          priority: high

- id: crop_steering_ml_confidence_low
  alias: ML Confidence Low
  trigger:
    - platform: numeric_state
      entity_id: sensor.crop_steering_ml_confidence
      below: 0.3
      for: "01:00:00"
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "⚠️ ML Confidence Low"
        message: "ML model confidence below 30%"
```

### Step 3: Historical Data

Configure data retention:

```yaml
# configuration.yaml
recorder:
  include:
    entities:
      - sensor.crop_steering_fused_vwc
      - sensor.crop_steering_fused_ec
      - sensor.crop_steering_dryback_percentage
      - sensor.crop_steering_ml_irrigation_need
      - sensor.crop_steering_irrigation_efficiency
      - sensor.crop_steering_sensor_health

influxdb:
  host: localhost
  port: 8086
  database: crop_steering
  include:
    entities:
      - sensor.crop_steering_fused_vwc
      - sensor.crop_steering_ml_confidence
      - sensor.crop_steering_irrigation_efficiency
```

## 🔧 Troubleshooting Installation

### Common Issues

#### Integration Not Found

**Problem**: Can't find integration in HACS or HA
**Solution**:
```bash
# Check integration files exist
ls -la /config/custom_components/crop_steering/

# Should show:
# __init__.py
# manifest.json
# config_flow.py
# sensor.py
# number.py
# switch.py
# etc.

# Restart Home Assistant if files are present
```

#### Python Dependencies Missing

**Problem**: AI features not working, import errors in logs
**Solution**:
```bash
# Install missing packages
pip install numpy pandas plotly scikit-learn scipy

# For Home Assistant OS/Supervised:
docker exec homeassistant pip install numpy pandas plotly scikit-learn scipy

# Restart AppDaemon after installation
```

#### AppDaemon Apps Not Loading

**Problem**: AI modules not starting, no AppDaemon entities
**Solution**:
```bash
# Check AppDaemon logs
tail -f /config/appdaemon/logs/appdaemon.log

# Common issues:
# 1. Missing dependencies -> install Python packages
# 2. File permissions -> fix with chmod/chown
# 3. Configuration errors -> check apps.yaml syntax

# Fix permissions
chmod -R 755 /config/appdaemon/apps/crop_steering
chown -R homeassistant:homeassistant /config/appdaemon/apps/
```

#### Sensor Configuration Issues

**Problem**: Sensor fusion not working, no fused values
**Solution**:
```bash
# Check sensor entities exist and have valid states
# Go to Developer Tools > States
# Filter by your sensor names

# Common issues:
# 1. Wrong entity names -> update configuration
# 2. Sensors offline -> check hardware
# 3. Invalid sensor values -> calibrate sensors
```

### Performance Issues

#### Slow AI Processing

**Problem**: Long delays in decision making, high CPU usage
**Solution**:
```bash
# Reduce update frequencies
# In AppDaemon app configuration:
update_interval = 60  # Increase from 30 seconds
ml_prediction_interval = 120  # Increase from 60 seconds

# Reduce ML model complexity
retrain_frequency = 100  # Increase from 50
```

#### Memory Usage High

**Problem**: High RAM usage, system becoming slow
**Solution**:
```bash
# Reduce data history windows
history_window = 500  # Reduce from 1000
max_data_points = 1440  # Reduce from 2880

# Clear old training data periodically
ml_predictor.reset_models()  # If needed
```

## 📈 Post-Installation Optimization

### Week 1: Initial Monitoring

- **Monitor sensor fusion reliability**
- **Check ML model initial learning**
- **Verify irrigation hardware operation**
- **Track system stability**

### Week 2: Parameter Tuning

- **Adjust sensor fusion thresholds**
- **Optimize ML prediction intervals**
- **Fine-tune crop profile parameters**
- **Configure alerts and notifications**

### Week 3+: Performance Optimization

- **Analyze ML model performance**
- **Optimize irrigation efficiency**
- **Custom crop profile development**
- **Advanced feature utilization**

## 📞 Support Resources

### Documentation
- [AI Operation Guide](ai_operation_guide.md)
- [Dashboard Usage](dashboard_guide.md)
- [Troubleshooting Guide](troubleshooting.md)

### Community Support
- **GitHub Issues**: [Report problems](https://github.com/JakeTheRabbit/HA-Irrigation-Strategy/issues)
- **Home Assistant Forum**: Community discussions
- **AppDaemon Forum**: Technical AppDaemon questions

### Logs and Diagnostics
- **Home Assistant Logs**: `/config/home-assistant.log`
- **AppDaemon Logs**: `/config/appdaemon/logs/`
- **Integration Logs**: Filter by `crop_steering` in HA logs
- **System Status**: Check integration device page

---

**Installation Complete!** 🎉

Your Advanced AI Crop Steering System is now ready to transform your growing operation with intelligent automation and professional-grade analytics.