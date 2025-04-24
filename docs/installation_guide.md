# Crop Steering Package - Installation & Setup Guide

This advanced irrigation control system uses crop steering principles to optimize plant growth through substrate moisture (VWC) and nutrient (EC) management. The system automates the complex decision-making involved in crop steering by managing a four-phase daily irrigation cycle.

## Quick Installation

1. Add this to your configuration.yaml:
   ```yaml
   homeassistant:
     packages: 
       crop_steering: !include packages/CropSteering/crop_steering_package.yaml
   ```

2. Restart Home Assistant

3. Set up two automations from the blueprints:
   - **Entity Configuration Blueprint** - Define your sensors and valves
   - **Parameters Configuration Blueprint** - Configure all numerical parameters

## Detailed Setup Instructions

### Step 1: Configure Entities

The Entity Configuration Blueprint lets you define all sensors and switches through the Home Assistant UI rather than editing YAML files.

1. Go to **Configuration** → **Automations & Scenes**
2. Click **+ Add Automation** → **Create new automation**
3. Click **Create new automation from blueprint**
4. Find and select **Crop Steering - Entity Configuration**
5. Configure the following:
   - VWC/moisture sensors (select all applicable sensors)
   - EC/nutrient sensors (select all applicable sensors)
   - Irrigation pump/valve control
   - Zone valves (in order - Zone 1, Zone 2, Zone 3)
   - Optional zone-specific sensors for detailed monitoring
6. Click **Save**

### Step 2: Configure Parameters

The Parameters Configuration Blueprint lets you set all numerical parameters through the UI.

1. Go to **Configuration** → **Automations & Scenes**
2. Click **+ Add Automation** → **Create new automation**
3. Click **Create new automation from blueprint**
4. Find and select **Crop Steering - Parameters Configuration**
5. Configure parameters for:
   - Substrate properties (size, water capacity, etc.)
   - Phase 0 (dryback) settings
   - Phase 1 (ramp-up) settings
   - Phase 2 (maintenance) settings
   - Phase 3 (overnight dryback) settings
   - EC targets for each phase and growth mode
   - Light schedule
   - EC stacking (advanced)
   - Sensor validation thresholds
6. Click **Save**

### Step 3: Add Dashboard Cards

Several Lovelace dashboard cards are provided in the `cards/` directory:

- **crop_steering_dashboard_card.yaml** - Complete card with all details
- **crop_steering_dashboard_card_simple.yaml** - Simplified version
- **crop_steering_dashboard_card_plotly.yaml** - Advanced visualization with Plotly

To add a card:
1. Go to your dashboard
2. Click the menu (three dots) → **Edit Dashboard**
3. Click **+ Add Card** → **Manual**
4. Copy/paste the content from the desired card YAML file
5. Click **Save**

## System Overview

### Four-Phase Daily Cycle

The crop steering system operates in four daily phases:

1. **P0 (Morning Dryback)**: 
   - Begins at lights-on
   - Allows substrate to dry to target level
   - Creates proper root zone environment

2. **P1 (Ramp-Up Phase)**:
   - Progressive shot sizes
   - Rehydrates substrate to optimal level
   - Prepares for nutrient uptake

3. **P2 (Maintenance Phase)**:
   - Main daily irrigation phase
   - Dynamic EC-based irrigation threshold adjustments
   - Maintains optimal moisture for nutrient uptake

4. **P3 (Pre-Lights-Off)**:
   - Controlled dryback before lights off
   - Prevents overnight saturation
   - Optional emergency irrigation threshold

### Growth Modes

The system supports two growth steering modes:

- **Vegetative**: More frequent irrigation with lower EC targets
- **Generative**: Less frequent irrigation with higher EC targets and more pronounced dryback

### Multi-Zone Support

Each irrigation zone can be controlled independently, with zone-specific sensors for detailed monitoring and control.

## Troubleshooting

### Common Issues

1. **Sensors Not Reporting**: Ensure your sensors are properly connected and reporting values. Check the values in Developer Tools → States.

2. **Irrigation Not Triggering**: 
   - Verify your pump and valve entities are correctly configured
   - Check phase conditions and thresholds
   - Make sure your shot size calculations are appropriate for your substrate volume

3. **EC Stacking Issues**:
   - Ensure EC sensors are accurate
   - Check target EC values for each phase
   - Adjust stacking ratio if necessary

### Getting Support

For detailed technical questions or feature requests, visit the GitHub repository:
https://github.com/JakeTheRabbit/HA-Irrigation-Strategy

## Advanced Features

### EC Stacking

EC stacking is an advanced technique to promote generative growth by allowing EC to rise above target levels. This is managed automatically when enabled.

### AppDaemon Integration (Optional)

For enhanced functionality, the system can work with an AppDaemon script. See the `appdaemon/apps/crop_steering` directory for details.
