# 🌱 Home Assistant Crop Steering System

![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.3.0+-41BDF5?logo=home-assistant&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![YAML](https://img.shields.io/badge/YAML-Configuration-red?logo=yaml&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Professional-grade precision irrigation system for Home Assistant that implements **crop steering principles** to optimize plant growth and yield. Features advanced 4-phase irrigation cycles, real-time sensor monitoring, and intelligent automation.

## 🚀 Key Features

### 🎯 **Core Irrigation System**
- **4-Phase Daily Cycle**: P0 (Morning Dryback) → P1 (Ramp-Up) → P2 (Maintenance) → P3 (Pre-Lights-Off)
- **Precision Control**: Volumetric Water Content (VWC) and Electrical Conductivity (EC) based decisions
- **Multi-Zone Support**: Independent control of up to 3 irrigation zones
- **Safety Systems**: Multiple redundant safety checks prevent over/under-watering
- **Hardware Sequencing**: Proper pump → main line → zone valve startup/shutdown sequences

### 📊 **Advanced Analytics**
- **Real-time Monitoring**: Live VWC, EC, and system status tracking
- **Performance Analytics**: 24-hour efficiency metrics and water usage analysis
- **Dryback Detection**: Automatic peak/valley analysis for optimal timing
- **Trend Analysis**: Historical data tracking and pattern recognition
- **Statistical Validation**: Outlier detection and sensor reliability scoring

### 🧠 **Smart Automation**
- **EC Stacking**: Strategic nutrient accumulation for generative growth
- **Dynamic Thresholds**: EC-based irrigation trigger adjustments
- **Crop Profiles**: Pre-configured settings for Cannabis, Tomato, Lettuce, Basil
- **Growth Stage Detection**: Automatic vegetative/generative mode switching
- **Emergency Prevention**: Automatic drought stress prevention

### 🔧 **Easy Configuration**
- **Simple .env Setup**: Copy-paste your entity IDs into a single file
- **Auto-Configuration**: Python script automatically sets up all entities
- **No Blueprint Complexity**: Skip the tedious blueprint configuration process
- **Validation**: Automatic entity validation and error detection

### 📱 **Professional Dashboard**
- **Unified Interface**: Single comprehensive dashboard for all features
- **Real-time Status**: Live monitoring of all zones and hardware
- **Quick Controls**: Easy mode switching and zone management
- **Tabbed Settings**: Organized phase parameters and EC targets
- **Performance Metrics**: Built-in analytics and efficiency tracking

## 📦 Installation

### Option 1: Quick Install (Recommended)

1. **Download the system:**
   ```bash
   git clone https://github.com/yourusername/HA-Irrigation-Strategy.git
   cd HA-Irrigation-Strategy
   ```

2. **Copy files to Home Assistant:**
   ```bash
   # Copy package files
   cp -r packages/CropSteering/ /config/packages/
   
   # Copy AppDaemon app (optional but recommended)
   cp -r appdaemon/ /config/appdaemon/
   ```

3. **Configure your entities:**
   ```bash
   # Edit the configuration file with your entity IDs
   cp crop_steering.env my_crop_steering.env
   nano my_crop_steering.env
   ```

4. **Auto-configure the system:**
   ```bash
   python configure_crop_steering.py my_crop_steering.env
   ```

5. **Add package to configuration.yaml:**
   ```yaml
   homeassistant:
     packages: 
       crop_steering: !include packages/CropSteering/crop_steering_package.yaml
   ```

6. **Restart Home Assistant**

### Option 2: HACS Install (Coming Soon)

The system will be available as a HACS custom component for even easier installation.

## ⚙️ Configuration

### 🔌 **Hardware Requirements**

**Essential:**
- VWC (moisture) sensors for each zone
- EC (electrical conductivity) sensors for each zone  
- Main irrigation pump with switch control
- Main line valve (opens water flow to grow area)
- Individual zone valves for each irrigation zone

**Optional:**
- Waste/drain valve for system flushing
- Environmental sensors (temperature, humidity, VPD)
- Water level sensors

### 📝 **Quick Configuration**

Edit `crop_steering.env` with your entity IDs:

```bash
# IRRIGATION HARDWARE
PUMP_SWITCH=switch.irrigation_pump
MAIN_LINE_SWITCH=switch.main_line_valve
ZONE_1_SWITCH=switch.zone_1_valve
ZONE_2_SWITCH=switch.zone_2_valve
ZONE_3_SWITCH=switch.zone_3_valve

# SENSORS
ZONE_1_VWC_FRONT=sensor.z1_vwc_front
ZONE_1_VWC_BACK=sensor.z1_vwc_back
ZONE_1_EC_FRONT=sensor.z1_ec_front
ZONE_1_EC_BACK=sensor.z1_ec_back
# ... repeat for other zones

# SYSTEM PREFERENCES
DEFAULT_CROP_TYPE=Cannabis_Hybrid
DEFAULT_STEERING_MODE=Vegetative
SUBSTRATE_VOLUME_LITERS=10.0
```

Then run the configuration script:
```bash
python configure_crop_steering.py
```

## 🎮 Usage

### **Dashboard Access**

Add the dashboard card to your Home Assistant:
```yaml
# Add to your dashboard
- !include packages/CropSteering/cards/crop_steering_dashboard.yaml
```

### **Basic Operation**

1. **Enable Zones**: Turn on zone toggles for active irrigation areas
2. **Select Mode**: Choose Vegetative or Generative steering mode
3. **Monitor Status**: Watch real-time VWC, EC, and phase progression
4. **Adjust Parameters**: Fine-tune settings via the dashboard tabs

### **Advanced Features**

- **EC Stacking**: Enable for strategic nutrient accumulation
- **Crop Profiles**: Select pre-configured crop-specific settings
- **Analytics**: Monitor efficiency and performance metrics
- **Manual Override**: Force phase changes or emergency irrigation

## 📋 System Architecture

### **4-Phase Irrigation Cycle**

```
┌─────────────────────────────────────────────────────────────┐
│                    DAILY IRRIGATION CYCLE                   │
├─────────────────────────────────────────────────────────────┤
│ P0: Morning Dryback  │ P1: Ramp-Up │ P2: Maintenance │ P3: │
│ (Substrate drying)   │ (Progressive│ (EC-based       │Pre- │
│                      │ shot sizes) │ irrigation)     │Off  │
└─────────────────────────────────────────────────────────────┘
```

**P0 - Morning Dryback** (Lights On → Target Reached)
- Controlled substrate drying after lights turn on
- Configurable dryback targets for vegetative vs generative growth
- Safety timeouts prevent excessive drying

**P1 - Ramp-Up Phase** (Rehydration)
- Progressive irrigation shots with increasing sizes
- Gradual substrate rehydration to target VWC
- EC-based transition triggers to P2

**P2 - Maintenance Phase** (All Day)
- EC-adjusted irrigation thresholds
- Steady-state moisture and nutrient management
- Highest activity period for plant metabolism

**P3 - Pre-Lights-Off** (Before Dark Period)
- Controlled final dryback before night
- Emergency irrigation prevention
- Prepares plants for dark period metabolism

### **Safety Systems**

- **Multi-Level Validation**: Entity existence, state verification, range checking
- **Redundant Safety Checks**: Multiple irrigation prevention mechanisms  
- **Exception Handling**: Graceful error recovery prevents system crashes
- **Thread Safety**: Proper synchronization for concurrent operations
- **Hardware Sequencing**: Correct pump/valve startup and shutdown order

## 🔧 Technical Details

### **Supported Hardware**

**VWC Sensors (Athena Compatible):**
- **Range**: 0-100% volumetric water content
- **Athena Targets**: 40-70% operating range with 10-20% drybacks
- **Update Frequency**: Every 1-5 minutes for real-time steering
- **Accuracy**: ±2% for reliable crop steering decisions
- **Calibration**: Substrate-specific calibration for coco coir/rockwool

**EC Sensors (High-Range for Athena):**
- **Range**: 0-10+ mS/cm electrical conductivity (high-range required)
- **Athena Targets**: 3.0 EC feed, 4-9 EC substrate monitoring
- **Temperature Compensation**: Essential for accurate high-EC measurements
- **Calibration**: Regular calibration with high-EC standards (6-9 mS/cm)
- **Resolution**: 0.1 mS/cm minimum for precise steering decisions

**Irrigation Hardware (Athena Precision):**
- **Pump**: Variable flow rate 0.5-10 L/hr for precise shot control
- **Valves**: Fast-response solenoids for accurate timing (24VAC/relay)
- **Timing**: Precise shot duration control (30 seconds to 5 minutes)
- **Pressure**: Consistent pressure delivery for repeatable shot volumes
- **Runoff Collection**: 20-30% runoff monitoring for Athena methodology

### **AppDaemon Integration**

The system includes an advanced AppDaemon app for complex automation:

- **Advanced Logic**: Complex phase transitions and EC stacking
- **Real-time Processing**: Immediate sensor response and calculations
- **Historical Analysis**: Trend analysis and dryback detection  
- **Performance Optimization**: Efficient sensor polling and state management

### **Home Assistant Compatibility**

- **Minimum Version**: Home Assistant 2024.3.0+
- **Template Format**: Modern Home Assistant template syntax
- **Entity Standards**: Proper unique IDs, device classes, and state classes
- **Package Structure**: Clean, organized YAML configuration

## 🌿 Crop Steering Science

### **What is Crop Steering?**

Crop steering is a precision agriculture technique that uses strategic irrigation timing to influence plant physiology:

**Vegetative Steering** (Building Plant Structure):
- Higher moisture levels (shorter drybacks)
- Lower EC concentrations
- Focus on leaf and stem development
- Promotes overall plant size and health

**Generative Steering** (Promoting Flowering/Fruiting):
- Lower moisture levels (longer drybacks)  
- Higher EC concentrations
- Stress triggers reproductive responses
- Maximizes flower/fruit production

### **Key Principles**

1. **Timing is Everything**: When plants receive water matters as much as how much
2. **Stress = Signal**: Controlled stress triggers desired growth responses
3. **EC Management**: Nutrient concentration affects plant hormone balance
4. **Consistency**: Reliable patterns produce predictable plant responses

## 📊 Analytics & Monitoring

### **Performance Metrics**

- **Irrigation Efficiency**: Percentage of shots that achieve target VWC
- **Water Usage**: Total volume tracking with 24-hour and 7-day trends
- **Shot Frequency**: Automated counting and timing analysis
- **EC Stability**: Nutrient level consistency monitoring

### **Dryback Analysis**

- **Peak Detection**: Automatic identification of VWC peaks after irrigation
- **Valley Detection**: Recognition of VWC valleys before next irrigation
- **Duration Tracking**: Time-based dryback analysis
- **Percentage Calculation**: Quantified dryback measurements

### **Historical Data**

- **Trend Analysis**: Long-term pattern recognition
- **Seasonal Adjustment**: Automatic adaptation to changing conditions
- **Performance Baselines**: Establishment of normal operating ranges
- **Anomaly Detection**: Identification of unusual patterns or sensor issues

## 🔒 Safety & Reliability

### **Irrigation Safety**

- **Pump State Verification**: Always check pump status before starting new cycle
- **Maximum Runtime Limits**: Prevent runaway irrigation events
- **Emergency Shutoff**: Manual and automatic emergency stop capabilities
- **Sensor Validation**: Range checking and outlier detection

### **System Reliability**

- **Thread Synchronization**: Prevent race conditions in concurrent operations
- **Memory Management**: Proper resource cleanup and leak prevention
- **Exception Recovery**: Graceful handling of sensor failures and communication errors
- **Redundant Monitoring**: Multiple validation layers for critical operations

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### **Development Setup**

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper testing
4. Submit a pull request with detailed description

### **Reporting Issues**

- Use GitHub Issues for bug reports and feature requests
- Include Home Assistant version, hardware details, and error logs
- Provide configuration files (with sensitive data removed)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Home Assistant community for excellent automation platform
- AppDaemon developers for powerful Python automation capabilities
- Crop steering research community for scientific principles
- Beta testers and contributors for system validation

## 📚 Additional Resources

- [Installation Guide](docs/installation_guide.md) - Detailed setup instructions
- [Advanced Configuration](docs/comprehensive_documentation.md) - In-depth feature documentation
- [Troubleshooting Guide](docs/troubleshooting.md) - Common issues and solutions
- [API Reference](docs/api_reference.md) - Developer documentation

---

## 🌟 **Transform Your Growing Operation**

Experience professional-grade precision irrigation with the power of Home Assistant automation. From hobby grows to commercial operations, this system delivers the control and reliability needed for optimal plant health and maximum yields.

**Ready to get started?** Follow the [Quick Install](#installation) guide and have your crop steering system running in minutes!

---

*Made with ❤️ for the Home Assistant and growing communities*