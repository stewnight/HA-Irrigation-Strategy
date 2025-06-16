# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

This is a **Home Assistant precision irrigation system** that implements crop steering principles for optimizing plant growth. The system manages a sophisticated four-phase daily irrigation cycle (P0-P3) using VWC (volumetric water content) and EC (electrical conductivity) sensor feedback.

## Architecture

### Core Components
- **Home Assistant Package**: `packages/CropSteering/` - Main YAML configuration and template entities
- **AppDaemon App**: `appdaemon/apps/crop_steering/crop_steering_app.py` - Advanced Python logic for complex irrigation decisions
- **Configuration Blueprints**: `blueprints/automation/` - GUI-driven setup for entities and parameters
- **Dashboard Cards**: `packages/CropSteering/cards/` - Visualization components

### Multi-Layer Design
1. **Configuration Layer**: Blueprints eliminate manual YAML editing
2. **Data Storage Layer**: Input helpers split across 7 domain-specific files
3. **Processing Layer**: Dual YAML templates + AppDaemon Python logic
4. **Hardware Interface**: Multi-zone irrigation with sensor validation

## Key Files Structure

```
packages/CropSteering/
├── crop_steering_package.yaml      # Main package (includes all others)
├── cs_input_numbers.yaml          # Numerical parameters
├── cs_input_selects.yaml          # Dropdown selections
├── cs_input_booleans.yaml         # On/off toggles
├── cs_input_datetimes.yaml        # Time-based settings
├── cs_input_texts.yaml            # Text configurations
├── cs_template_entities.yaml      # Calculated sensors/switches
└── cards/                         # Dashboard components
```

## Development Workflow

### Configuration Management
- **Never hardcode values** - everything must be configurable via Home Assistant UI
- **Blueprint-first approach** - users configure through automation blueprints
- **Domain separation** - input entities split by type for Home Assistant package compatibility

### Making Changes
1. **Input entities**: Modify the appropriate `cs_input_*.yaml` file based on entity type
2. **Template logic**: Edit `cs_template_entities.yaml` for calculated sensors/switches
3. **Advanced logic**: Modify `crop_steering_app.py` for complex Python-based decisions
4. **Configuration**: Update blueprints in `blueprints/automation/` for user-facing setup

### Safety & Validation
- All sensor inputs include validation and fallback logic
- Multiple safety thresholds prevent over/under-watering
- AppDaemon provides advanced features while YAML-only mode works for basic operation

## Irrigation System Logic

### Four-Phase Daily Cycle
- **P0 (Morning Dryback)**: Controlled substrate drying after lights-on
- **P1 (Ramp-Up)**: Progressive irrigation shots for rehydration  
- **P2 (Maintenance)**: EC-adjusted irrigation throughout photoperiod
- **P3 (Pre-Lights-Off)**: Final dryback with emergency prevention

### Advanced Features
- **EC Stacking**: Deliberate nutrient accumulation for generative growth
- **Multi-Zone Control**: Independent zone management with zone-specific sensors
- **Dryback Detection**: Real-time peak/valley analysis using VWC history

## Configuration Requirements

Users must configure two automations from blueprints:
1. **Entity Configuration Blueprint**: Define sensors, pumps, zone valves
2. **Parameters Configuration Blueprint**: Set all numerical parameters and thresholds

## File Relationships

- `crop_steering_package.yaml` includes all other package files
- Blueprint automations populate input helper entities
- Template entities in `cs_template_entities.yaml` reference input helpers
- AppDaemon app reads from input helpers and controls hardware switches
- Dashboard cards display data from template entities and input helpers

## Testing & Validation

This system requires physical hardware (sensors, pumps, valves) for full testing. When making changes:
- Validate YAML syntax with Home Assistant configuration check
- Test AppDaemon logic in Home Assistant logs
- Verify blueprint functionality through Home Assistant automation UI
- Monitor sensor validation and safety threshold logic

## Documentation

Comprehensive documentation exists in `docs/` including installation guide, operational details, and advanced configuration information.