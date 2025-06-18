# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

This is an **Advanced AI Crop Steering System** for Home Assistant that uses machine learning, sensor fusion, and intelligent automation to optimize precision irrigation. The system implements a sophisticated 4-phase irrigation cycle (P0-P3) with real-time AI decision making.

## Current Architecture (v2.0)

### Core Components
- **Home Assistant Integration**: `custom_components/crop_steering/` - Main HA integration with UI configuration
- **AI AppDaemon Modules**: `appdaemon/apps/crop_steering/` - Advanced machine learning and automation
- **Configuration File**: `crop_steering.env` - Hardware and sensor configuration
- **Documentation**: `docs/` - Complete user guides and operation manuals

### AI-Powered Design
1. **Integration Layer**: Home Assistant custom integration with config flow
2. **AI Processing Layer**: AppDaemon modules with ML prediction, sensor fusion, dryback detection
3. **Configuration Layer**: File-based hardware configuration (crop_steering.env)
4. **Dashboard Layer**: Real-time AI analytics with Plotly visualizations

## Key Files Structure

```
custom_components/crop_steering/     # Home Assistant Integration
├── __init__.py                     # Integration setup
├── config_flow.py                  # Setup wizard
├── sensor.py                       # Integration sensors
├── number.py                       # Configuration parameters
├── switch.py                       # Control switches
├── select.py                       # Selection entities
└── services.py                     # Integration services

appdaemon/apps/crop_steering/       # AI Modules
├── master_crop_steering_app.py     # Main AI coordinator
├── ml_irrigation_predictor.py      # Machine learning engine
├── intelligent_sensor_fusion.py    # Multi-sensor validation
├── advanced_dryback_detection.py   # Peak detection algorithms
├── intelligent_crop_profiles.py    # Strain-specific optimization
└── advanced_crop_steering_dashboard.py # Real-time analytics
```

## Development Workflow

### Configuration Management
- **UI-first approach** - all configuration through Home Assistant integration setup
- **File-based hardware config** - sensor and hardware entities defined in crop_steering.env
- **No manual YAML editing** - users configure through integration config flow

### Making Changes
1. **Integration entities**: Modify files in `custom_components/crop_steering/`
2. **AI logic**: Edit AppDaemon modules in `appdaemon/apps/crop_steering/`
3. **Hardware config**: Update `crop_steering.env` for sensor/hardware entities
4. **Documentation**: Update guides in `docs/` directory

### Safety & Validation
- AI-powered sensor validation with outlier detection
- Multi-layer safety systems with emergency AI response
- Thread-safe AppDaemon operation with proper synchronization
- Comprehensive error handling and graceful degradation

## AI Irrigation System Logic

### Four-Phase AI-Optimized Cycle
- **P0 (Morning Dryback)**: AI-predicted optimal drying duration
- **P1 (Ramp-Up)**: ML-guided progressive rehydration
- **P2 (Maintenance)**: Intelligent EC-based irrigation decisions
- **P3 (Pre-Lights-Off)**: Predictive final dryback management

### Advanced AI Features
- **Machine Learning**: Random Forest + Neural Network ensemble prediction
- **Sensor Fusion**: IQR-based outlier detection with Kalman filtering
- **Dryback Detection**: Multi-scale peak detection algorithms
- **Adaptive Profiles**: Strain-specific parameters with auto-learning
- **Real-time Analytics**: Professional Plotly dashboard with confidence bands

## Configuration Requirements

Users configure through Home Assistant integration:
1. **Add Integration**: Search "Crop Steering" in Devices & Services
2. **Configure Hardware**: Enter sensor and irrigation hardware entity names
3. **Select Crop Profile**: Choose plant type and growth stage
4. **Setup AppDaemon**: Install AI modules for advanced features

## System Architecture

### Integration Flow
- Home Assistant integration provides entities and configuration
- AppDaemon reads integration entities and controls hardware
- AI modules process sensor data and make irrigation decisions
- Dashboard displays real-time analytics and system status

### AI Module Coordination
- `master_crop_steering_app.py` coordinates all AI modules
- Individual modules handle specific AI functions (ML, fusion, profiles)
- Thread-safe operation ensures reliable concurrent processing
- Real-time dashboard provides professional monitoring interface

## Testing & Validation

This system requires physical hardware (sensors, pumps, valves) for full testing. When making changes:
- Test integration setup through Home Assistant UI
- Verify AppDaemon modules in AppDaemon logs
- Monitor AI learning progression and accuracy metrics
- Validate sensor fusion and outlier detection performance

## Documentation

Complete documentation in `docs/`:
- `installation_guide.md` - Step-by-step setup for beginners
- `ai_operation_guide.md` - AI system operation and monitoring
- `dashboard_guide.md` - Analytics dashboard usage
- `troubleshooting.md` - Problem resolution and maintenance

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

# IMPORTANT: Current System Status
This system has been completely overhauled from the original package-based approach to a modern AI-powered integration:
- NO packages/ directory exists anymore
- NO blueprints/ directory exists anymore  
- NO old dashboard YAML cards exist
- The system now uses: Integration + AppDaemon AI modules + crop_steering.env configuration
- Dashboard is dynamically generated by AI modules, not static YAML files
- All configuration is done through Home Assistant integration UI, not manual YAML editing