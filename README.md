# Home Assistant Irrigation Strategy

![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2022.06.0+-41BDF5?logo=home-assistant&logoColor=white)

Advanced irrigation control system for Home Assistant that uses crop steering principles to optimize plant growth and health, with full GUI configuration through blueprints.

## What is Crop Steering?

Crop steering is a precision agriculture technique that strategically manages irrigation to control plant growth. By carefully timing when plants receive water and how much they get, growers can "steer" plants toward vegetative growth (building structure) or generative growth (producing flowers/fruit).

## Key Features

- **Full GUI Configuration:** All entities and parameters can be configured through Home Assistant blueprints with no YAML editing required
- **Four-Phase Daily Cycle:**
  - **P0:** Morning dryback period, allowing substrate to dry to target level
  - **P1:** Ramp-up phase with progressive shot sizes
  - **P2:** Maintenance phase with EC-based irrigation trigger adjustments
  - **P3:** Pre-lights-off period with controlled dryback
- **Smart Adjustments:**
  - Dynamic EC-based threshold adjustments
  - EC stacking for generative growth
  - Configurable vegetative and generative modes
  - Emergency irrigation prevention
  - Multi-zone support
- **Advanced Visualization:**
  - Plotly-based dashboard cards
  - Comprehensive data display
  - Growth phase status tracking

## Quick Install

1. Add to configuration.yaml:
   ```yaml
   homeassistant:
     packages: 
       crop_steering: !include packages/CropSteering/crop_steering_package.yaml
   ```

2. Copy files to your Home Assistant config directory:
   - `packages/CropSteering/` - Package files
   - `blueprints/automation/` - Blueprint files
   - `appdaemon/apps/crop_steering/` - AppDaemon script (optional)

3. Set up through blueprints:
   - Entity Configuration Blueprint - Set up sensors and switches
   - Parameters Configuration Blueprint - Configure all numerical parameters

4. Add dashboard cards from the `cards/` directory

For complete documentation, see the [Installation Guide](docs/installation_guide.md).

## Screenshots

[Screenshots will be added later]

## Requirements

- Home Assistant (2022.6.0 or newer)
- VWC (substrate moisture) and EC (nutrient) sensors
- Irrigation control switches/relays
- AppDaemon add-on (recommended for advanced features)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
