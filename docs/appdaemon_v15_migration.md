# AppDaemon v15+ Migration Guide

## 🚨 Important: Directory Structure Changed

AppDaemon v15+ introduced a new directory structure that affects the Crop Steering System installation. This guide helps you migrate to the new paths.

## 📂 Directory Changes

### Old Paths (AppDaemon v14 and earlier):
```
/config/appdaemon/
├── appdaemon.yaml
├── apps/
│   ├── apps.yaml
│   └── crop_steering/
└── requirements.txt
```

### New Paths (AppDaemon v15+):
```
/addon_configs/a0d7b954_appdaemon/
├── appdaemon.yaml
├── apps/
│   ├── apps.yaml
│   └── crop_steering/
└── requirements.txt
```

## 🔄 Migration Steps

### Step 1: Locate Your Files

**Check which directory structure you have:**
```bash
# Check for new structure
ls -la /addon_configs/a0d7b954_appdaemon/

# Check for old structure  
ls -la /config/appdaemon/
```

### Step 2: Access Methods

#### **Samba Share Access:**
- **Old:** `\\YOUR_HA_IP\config\appdaemon`
- **New:** `\\YOUR_HA_IP\addon_configs\a0d7b954_appdaemon`

#### **SSH/Terminal Access:**
- **Old:** `/config/appdaemon/`
- **New:** `/addon_configs/a0d7b954_appdaemon/`

### Step 3: Migrate Crop Steering Files

If upgrading from old to new structure:

```bash
# Create new directory structure
mkdir -p /addon_configs/a0d7b954_appdaemon/apps

# Copy configuration files
cp /config/appdaemon/appdaemon.yaml /addon_configs/a0d7b954_appdaemon/
cp /config/appdaemon/apps/apps.yaml /addon_configs/a0d7b954_appdaemon/apps/

# Copy crop steering modules
cp -r /config/appdaemon/apps/crop_steering /addon_configs/a0d7b954_appdaemon/apps/

# Copy requirements if exists
cp /config/appdaemon/requirements.txt /addon_configs/a0d7b954_appdaemon/
```

### Step 4: Update Configuration

Edit `/addon_configs/a0d7b954_appdaemon/appdaemon.yaml`:

```yaml
secrets: /homeassistant/secrets.yaml
appdaemon:
  latitude: YOUR_LATITUDE
  longitude: YOUR_LONGITUDE 
  elevation: YOUR_ELEVATION
  time_zone: YOUR_TIMEZONE
  app_dir: /homeassistant/addon_configs/a0d7b954_appdaemon/apps  # Updated path
  plugins:
    HASS:
      type: hass
      ha_url: http://homeassistant.local:8123
      token: YOUR_LONG_LIVED_TOKEN
http:
  url: http://0.0.0.0:5050
admin:
api:
hadashboard:
```

### Step 5: Fix Requirements

Run the updated fix script:
```bash
./fix_appdaemon_requirements.sh
```

This script now automatically detects v15+ paths.

## 🔧 Troubleshooting

### Connection Issues

If AppDaemon shows "Disconnected from Home Assistant":

1. **Check token** in `appdaemon.yaml`
2. **Verify HA URL** (try `http://homeassistant.local:8123` or `http://YOUR_HA_IP:8123`)
3. **Restart AppDaemon** after config changes

### File Access Issues

If you can't find the addon_configs directory:

1. **Enable Samba Share** add-on
2. **Use VSCode** add-on for direct file editing
3. **SSH access** with Terminal add-on

### Module Loading Issues

If crop steering modules don't load:

1. **Check file paths** in apps directory
2. **Verify apps.yaml** configuration
3. **Check AppDaemon logs** for import errors

## 📝 Configuration File Templates

### appdaemon.yaml (v15+ compatible):
```yaml
secrets: /homeassistant/secrets.yaml
appdaemon:
  latitude: 40.8939
  longitude: -74.0455
  elevation: 100
  time_zone: America/New_York
  app_dir: /homeassistant/addon_configs/a0d7b954_appdaemon/apps
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

### apps.yaml (unchanged):
```yaml
# Master Crop Steering Application
master_crop_steering:
  module: crop_steering.master_crop_steering_app
  class: MasterCropSteeringApp
  dependencies:
    - crop_steering_dashboard
  log: crop_steering_master
  log_level: INFO

# Advanced Dashboard Application  
crop_steering_dashboard:
  module: crop_steering.advanced_crop_steering_dashboard
  class: AdvancedCropSteeringDashboard
  log: crop_steering_dashboard
  log_level: INFO

# Global Python modules required by all apps
global_modules:
  - requests
  - numpy
  - pandas
  - plotly
  - scipy
```

## ✅ Verification

After migration, verify everything works:

1. **AppDaemon connects** to Home Assistant (no connection warnings)
2. **Modules load** successfully (check logs for "Master Crop Steering Application")
3. **Dashboard accessible** at `http://YOUR_HA_IP:5050`
4. **Crop steering entities** appear in Home Assistant

## 🆘 Need Help?

If you encounter issues:

1. Check [Installation Guide](installation_guide.md) for updated steps
2. Review [Troubleshooting Guide](troubleshooting.md)
3. Post issues on [GitHub](https://github.com/JakeTheRabbit/HA-Irrigation-Strategy/issues)