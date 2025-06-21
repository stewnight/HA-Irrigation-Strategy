# Changelog

All notable changes to the Advanced AI Crop Steering System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2024-12-21

### 🚀 Major Features Added
- **Dynamic Zone Configuration** - Support for 1-6 irrigation zones (previously hardcoded to 3)
- **Interactive Zone Setup Tool** - `zone_configuration_helper.py` for easy zone configuration
- **AppDaemon Compatibility Fix** - `fix_appdaemon_requirements.sh` resolves scikit-learn installation issues
- **Flexible Entity Creation** - Automatic generation of sensors and switches per configured zone

### ✨ New Components
- `zone_config.py` - Zone configuration parser and validator
- `zone_configuration_helper.py` - Interactive setup wizard
- `fix_appdaemon_requirements.sh` - AppDaemon compatibility fix script
- `docs/dynamic_zones_guide.md` - Complete zone configuration documentation
- `services.yaml` - Proper service documentation

### 🔧 Enhancements
- **Config Flow Improvements** - Two setup modes: automatic (from env file) or manual (UI wizard)
- **Service Updates** - Dynamic zone validation in irrigation services
- **Entity Scaling** - All components now create entities per configured zone
- **Error Handling** - Improved validation and graceful error handling
- **Documentation** - Updated all guides for v2.1.0 features

### 🐛 Bug Fixes
- Fixed hardcoded zone iteration in AppDaemon modules
- Resolved entity creation for zones 2+ (previously only zone 1 worked)
- Fixed service validation to accept configured zones instead of hardcoded 1-3
- Removed obsolete package references in config flow
- Fixed sensor averaging to use actual configured sensors

### 🏗️ Architecture Changes
- **Zone Detection** - Dynamic zone discovery from configuration
- **Entity Generation** - Runtime entity creation based on zone count
- **AppDaemon Integration** - Removed hardcoded zone loops
- **Configuration Management** - Centralized zone config through new parser

### 📊 Per-Zone Entities Created
For each configured zone:
- `switch.crop_steering_zone_X_enabled` - Zone enable/disable
- `switch.crop_steering_zone_X_manual_override` - Manual control
- `sensor.crop_steering_vwc_zone_X` - Average VWC for zone
- `sensor.crop_steering_ec_zone_X` - Average EC for zone  
- `sensor.crop_steering_zone_X_status` - Zone operational status
- `sensor.crop_steering_zone_X_last_irrigation` - Last irrigation timestamp

### 🔄 Migration Notes
- Existing 3-zone setups continue working without changes
- New installations can configure any number of zones 1-6
- Zone configuration now centralized in `crop_steering.env`
- Helper scripts automate setup process

### ⚠️ Breaking Changes
- None - fully backward compatible with existing installations

### 🔮 Future Enhancements
- Zone grouping for simultaneous irrigation
- Zone-specific crop profiles
- Individual zone scheduling
- Water usage tracking per zone

---

## [2.0.0] - 2024-12-15

### 🚀 Major Release - Complete System Overhaul
- **New Architecture** - Integration + AppDaemon AI modules (replaced package-based approach)
- **Advanced AI Features** - Machine learning, sensor fusion, dryback detection
- **Professional Dashboard** - Real-time Plotly visualizations
- **Quality Assurance** - Complete code validation and optimization
- **Production Ready** - Comprehensive testing and error handling

### ✨ AI Features
- **Machine Learning Engine** - Predictive irrigation with ensemble models
- **Intelligent Sensor Fusion** - Multi-sensor validation with outlier detection
- **Advanced Dryback Detection** - Peak detection algorithms
- **Intelligent Crop Profiles** - Strain-specific optimization

### 🏗️ Architecture
- **Home Assistant Integration** - Native HA integration with config flow
- **AppDaemon AI Modules** - Advanced machine learning and automation
- **Configuration Management** - File-based hardware configuration
- **Real-time Dashboard** - Professional monitoring interface

### 📚 Documentation
- Complete installation guide for beginners
- AI operation guide
- Dashboard usage guide  
- Troubleshooting documentation

---

## [1.x] - Legacy Versions
Previous package-based implementations. See git history for details.