#!/usr/bin/env python3
"""
Crop Steering System Configuration Script

This script reads crop_steering.env and automatically configures
all Home Assistant input helpers for the crop steering system.

Usage:
    python configure_crop_steering.py [config_file]

If no config file is specified, it looks for crop_steering.env
"""
import os
import sys
import json
import requests
from typing import Dict, Any, Optional

class CropSteeringConfigurator:
    def __init__(self, ha_url: str, ha_token: str):
        """Initialize configurator with Home Assistant connection details."""
        self.ha_url = ha_url.rstrip('/')
        self.ha_token = ha_token
        self.headers = {
            'Authorization': f'Bearer {ha_token}',
            'Content-Type': 'application/json'
        }
        
    def load_env_config(self, env_file: str = 'crop_steering.env') -> Dict[str, str]:
        """Load configuration from .env file."""
        config = {}
        if not os.path.exists(env_file):
            raise FileNotFoundError(f"Configuration file {env_file} not found")
            
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        
        return config
    
    def validate_entity(self, entity_id: str) -> bool:
        """Check if entity exists in Home Assistant."""
        if not entity_id:
            return True  # Empty entities are valid (means not used)
            
        url = f"{self.ha_url}/api/states/{entity_id}"
        try:
            response = requests.get(url, headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            print(f"Warning: Could not validate entity {entity_id}: {e}")
            return False
    
    def set_input_helper(self, entity_id: str, value: str) -> bool:
        """Set value of an input helper entity."""
        domain = entity_id.split('.')[0]
        service_map = {
            'input_text': 'input_text/set_value',
            'input_number': 'input_number/set_value',
            'input_boolean': 'input_boolean/turn_on' if value.lower() in ['true', '1', 'on'] else 'input_boolean/turn_off',
            'input_select': 'input_select/select_option'
        }
        
        service = service_map.get(domain)
        if not service:
            print(f"Warning: Unknown input helper type: {domain}")
            return False
            
        data = {'entity_id': entity_id}
        
        if domain == 'input_boolean':
            # Boolean services don't need value parameter
            pass
        elif domain == 'input_select':
            data['option'] = value
        else:
            data['value'] = value
            
        url = f"{self.ha_url}/api/services/{service}"
        try:
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 200:
                print(f"✓ Set {entity_id} = {value}")
                return True
            else:
                print(f"✗ Failed to set {entity_id}: {response.status_code} {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error setting {entity_id}: {e}")
            return False
    
    def configure_system(self, config: Dict[str, str]) -> None:
        """Configure the entire crop steering system."""
        print("🌱 Configuring Crop Steering System")
        print("=" * 50)
        
        # Validate critical entities first
        print("\n📋 Validating entities...")
        critical_entities = ['PUMP_SWITCH', 'MAIN_LINE_SWITCH', 'ZONE_1_SWITCH']
        for key in critical_entities:
            entity = config.get(key, '')
            if entity and not self.validate_entity(entity):
                print(f"⚠️  Warning: Critical entity {key}={entity} not found in Home Assistant")
        
        # Configuration mappings
        print("\n🔧 Configuring irrigation hardware...")
        hardware_mappings = {
            'input_text.cs_config_pump_switch_entity': config.get('PUMP_SWITCH', ''),
            'input_text.cs_config_main_line_switch_entity': config.get('MAIN_LINE_SWITCH', ''),
            'input_text.cs_config_zone_1_switch_entity': config.get('ZONE_1_SWITCH', ''),
            'input_text.cs_config_zone_2_switch_entity': config.get('ZONE_2_SWITCH', ''),
            'input_text.cs_config_zone_3_switch_entity': config.get('ZONE_3_SWITCH', ''),
            'input_text.cs_config_waste_switch_entity': config.get('WASTE_SWITCH', ''),
        }
        
        for entity_id, value in hardware_mappings.items():
            self.set_input_helper(entity_id, value)
        
        print("\n📊 Configuring sensors...")
        sensor_mappings = {
            # Zone 1 sensors
            'input_text.cs_config_z1_vwc_front': config.get('ZONE_1_VWC_FRONT', ''),
            'input_text.cs_config_z1_vwc_back': config.get('ZONE_1_VWC_BACK', ''),
            'input_text.cs_config_z1_ec_front': config.get('ZONE_1_EC_FRONT', ''),
            'input_text.cs_config_z1_ec_back': config.get('ZONE_1_EC_BACK', ''),
            # Zone 2 sensors
            'input_text.cs_config_z2_vwc_front': config.get('ZONE_2_VWC_FRONT', ''),
            'input_text.cs_config_z2_vwc_back': config.get('ZONE_2_VWC_BACK', ''),
            'input_text.cs_config_z2_ec_front': config.get('ZONE_2_EC_FRONT', ''),
            'input_text.cs_config_z2_ec_back': config.get('ZONE_2_EC_BACK', ''),
            # Zone 3 sensors
            'input_text.cs_config_z3_vwc_front': config.get('ZONE_3_VWC_FRONT', ''),
            'input_text.cs_config_z3_vwc_back': config.get('ZONE_3_VWC_BACK', ''),
            'input_text.cs_config_z3_ec_front': config.get('ZONE_3_EC_FRONT', ''),
            'input_text.cs_config_z3_ec_back': config.get('ZONE_3_EC_BACK', ''),
        }
        
        for entity_id, value in sensor_mappings.items():
            self.set_input_helper(entity_id, value)
        
        print("\n⚙️  Configuring system parameters...")
        parameter_mappings = {
            # System preferences
            'input_select.cs_crop_type_profile': config.get('DEFAULT_CROP_TYPE', 'Cannabis_Hybrid').replace('_', ' - '),
            'input_select.cs_steering_mode': config.get('DEFAULT_STEERING_MODE', 'Vegetative'),
            
            # Feature toggles
            'input_boolean.cs_ec_stacking_enabled': config.get('ENABLE_EC_STACKING', 'false'),
            
            # Substrate properties
            'input_number.cs_substrate_volume': config.get('SUBSTRATE_VOLUME_LITERS', '10.0'),
            'input_number.cs_dripper_flow_rate': config.get('DRIPPER_FLOW_RATE_LPH', '2.0'),
            'input_number.cs_substrate_field_capacity': config.get('SUBSTRATE_FIELD_CAPACITY', '40'),
            'input_number.cs_substrate_max_ec': config.get('SUBSTRATE_MAX_EC', '7.0'),
            
            # P0 parameters
            'input_number.cs_p0_veg_dryback_target': config.get('P0_VEG_DRYBACK_TARGET', '22'),
            'input_number.cs_p0_gen_dryback_target': config.get('P0_GEN_DRYBACK_TARGET', '18'),
            'input_number.cs_p0_min_wait_time': config.get('P0_MIN_WAIT_TIME', '30'),
            'input_number.cs_p0_max_wait_time': config.get('P0_MAX_WAIT_TIME', '120'),
            
            # P1 parameters
            'input_number.cs_p1_initial_shot_size_percent': config.get('P1_INITIAL_SHOT_SIZE_PERCENT', '2.0'),
            'input_number.cs_p1_shot_size_increment_percent': config.get('P1_SHOT_SIZE_INCREMENT', '0.5'),
            'input_number.cs_p1_max_shot_size_percent': config.get('P1_MAX_SHOT_SIZE_PERCENT', '10.0'),
            'input_number.cs_p1_time_between_shots': config.get('P1_TIME_BETWEEN_SHOTS', '15'),
            'input_number.cs_p1_target_vwc': config.get('P1_TARGET_VWC', '30'),
            'input_number.cs_p1_max_shots': config.get('P1_MAX_SHOTS', '6'),
            'input_number.cs_p1_min_shots': config.get('P1_MIN_SHOTS', '3'),
            
            # P2 parameters
            'input_number.cs_p2_shot_size_percent': config.get('P2_SHOT_SIZE_PERCENT', '5.0'),
            'input_number.cs_p2_vwc_threshold': config.get('P2_VWC_THRESHOLD', '25'),
            'input_number.cs_p2_ec_high_threshold': config.get('P2_EC_HIGH_THRESHOLD', '1.2'),
            'input_number.cs_p2_ec_low_threshold': config.get('P2_EC_LOW_THRESHOLD', '0.8'),
            
            # P3 parameters
            'input_number.cs_p3_veg_last_irrigation': config.get('P3_VEG_LAST_IRRIGATION', '120'),
            'input_number.cs_p3_gen_last_irrigation': config.get('P3_GEN_LAST_IRRIGATION', '180'),
            'input_number.cs_p3_emergency_vwc_threshold': config.get('P3_EMERGENCY_VWC_THRESHOLD', '15'),
            'input_number.cs_p3_emergency_shot_size_percent': config.get('P3_EMERGENCY_SHOT_SIZE_PERCENT', '2.0'),
            
            # EC targets
            'input_number.cs_ec_target_veg_p0': config.get('EC_TARGET_VEG_P0', '1.6'),
            'input_number.cs_ec_target_veg_p1': config.get('EC_TARGET_VEG_P1', '1.6'),
            'input_number.cs_ec_target_veg_p2': config.get('EC_TARGET_VEG_P2', '1.6'),
            'input_number.cs_ec_target_veg_p3': config.get('EC_TARGET_VEG_P3', '1.6'),
            'input_number.cs_ec_target_gen_p0': config.get('EC_TARGET_GEN_P0', '3.0'),
            'input_number.cs_ec_target_gen_p1': config.get('EC_TARGET_GEN_P1', '3.5'),
            'input_number.cs_ec_target_gen_p2': config.get('EC_TARGET_GEN_P2', '4.0'),
            'input_number.cs_ec_target_gen_p3': config.get('EC_TARGET_GEN_P3', '3.5'),
        }
        
        for entity_id, value in parameter_mappings.items():
            self.set_input_helper(entity_id, value)
        
        # Auto-enable zones with configured sensors
        print("\n🔌 Auto-enabling zones with sensors...")
        zone_configs = [
            ('input_boolean.cs_zone_1_enabled', ['ZONE_1_VWC_FRONT', 'ZONE_1_VWC_BACK', 'ZONE_1_EC_FRONT', 'ZONE_1_EC_BACK']),
            ('input_boolean.cs_zone_2_enabled', ['ZONE_2_VWC_FRONT', 'ZONE_2_VWC_BACK', 'ZONE_2_EC_FRONT', 'ZONE_2_EC_BACK']),
            ('input_boolean.cs_zone_3_enabled', ['ZONE_3_VWC_FRONT', 'ZONE_3_VWC_BACK', 'ZONE_3_EC_FRONT', 'ZONE_3_EC_BACK'])
        ]
        
        for zone_entity, sensor_keys in zone_configs:
            has_sensors = any(config.get(key, '') for key in sensor_keys)
            zone_switch = config.get(zone_entity.replace('cs_zone_', 'ZONE_').replace('_enabled', '_SWITCH'), '')
            
            if has_sensors and zone_switch:
                self.set_input_helper(zone_entity, 'true')
                print(f"✓ Enabled {zone_entity} (has sensors and switch)")
            else:
                self.set_input_helper(zone_entity, 'false')
        
        print("\n✅ Configuration complete!")
        print("\n📋 Next steps:")
        print("1. Restart Home Assistant to load all changes")
        print("2. Check the Crop Steering dashboard")
        print("3. Verify all entities are working correctly")
        print("4. Enable AppDaemon app if using advanced features")

def main():
    # Get configuration file from command line or use default
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'crop_steering.env'
    
    # Get Home Assistant connection details from environment or prompt
    ha_url = os.getenv('HA_URL') or input("Home Assistant URL (e.g., http://homeassistant.local:8123): ").strip()
    ha_token = os.getenv('HA_TOKEN') or input("Home Assistant Long-Lived Access Token: ").strip()
    
    if not ha_url or not ha_token:
        print("❌ Home Assistant URL and token are required")
        print("\nTo get a token:")
        print("1. Go to your Home Assistant profile")
        print("2. Scroll to 'Long-Lived Access Tokens'")
        print("3. Click 'Create Token'")
        print("4. Copy the token and run this script again")
        sys.exit(1)
    
    try:
        configurator = CropSteeringConfigurator(ha_url, ha_token)
        config = configurator.load_env_config(config_file)
        configurator.configure_system(config)
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()