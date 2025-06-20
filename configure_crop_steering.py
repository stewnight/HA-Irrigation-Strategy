#!/usr/bin/env python3
"""
Configuration Script for AI-Powered Crop Steering System
Validates and processes crop_steering.env configuration file
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional

def load_env_file(env_path: str) -> Dict[str, str]:
    """Load and parse environment file."""
    config = {}
    
    if not os.path.exists(env_path):
        print(f"❌ Configuration file not found: {env_path}")
        return config
    
    print(f"📄 Loading configuration from: {env_path}")
    
    with open(env_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
                
            # Parse KEY=value format
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                
                if value:  # Only store non-empty values
                    config[key] = value
    
    return config

def validate_entities(config: Dict[str, str]) -> List[str]:
    """Validate entity configurations."""
    errors = []
    required_patterns = {
        'PUMP_MASTER': r'^(switch\.|input_boolean\.)',
        'IRRIGATION_MAIN_LINE': r'^(switch\.|input_boolean\.)',
        'IRRIGATION_ZONE_': r'^(switch\.|input_boolean\.)',
        'VWC_SENSOR_': r'^sensor\.',
        'EC_SENSOR_': r'^sensor\.',
        'TEMPERATURE_SENSOR': r'^sensor\.',
        'HUMIDITY_SENSOR': r'^sensor\.',
        'VPD_SENSOR': r'^sensor\.'
    }
    
    print("\n🔍 Validating entity configurations...")
    
    for key, value in config.items():
        for pattern, regex in required_patterns.items():
            if key.startswith(pattern):
                if not re.match(regex, value):
                    errors.append(f"Invalid entity format: {key}={value} (should match {regex})")
                else:
                    print(f"✅ {key}: {value}")
    
    return errors

def validate_numeric_values(config: Dict[str, str]) -> List[str]:
    """Validate numeric configuration values."""
    errors = []
    numeric_configs = {
        'SUBSTRATE_VOLUME_LITERS': (1, 100),
        'DRIPPER_FLOW_RATE_LPH': (0.1, 10),
        'FIELD_CAPACITY_VWC': (50, 90),
        'MAX_EC_THRESHOLD': (5, 15),
        'VEG_DRYBACK_TARGET': (30, 70),
        'GEN_DRYBACK_TARGET': (20, 60),
        'P1_TARGET_VWC': (50, 80),
        'P2_VWC_THRESHOLD': (40, 70)
    }
    
    print("\n📊 Validating numeric configurations...")
    
    for key, (min_val, max_val) in numeric_configs.items():
        if key in config:
            try:
                value = float(config[key])
                if min_val <= value <= max_val:
                    print(f"✅ {key}: {value}")
                else:
                    errors.append(f"{key}={value} out of range [{min_val}, {max_val}]")
            except ValueError:
                errors.append(f"{key}={config[key]} is not a valid number")
    
    return errors

def check_completeness(config: Dict[str, str]) -> List[str]:
    """Check configuration completeness."""
    warnings = []
    
    # Essential entities
    essential = [
        'PUMP_MASTER', 'IRRIGATION_MAIN_LINE',
        'VWC_SENSOR_Z1_FRONT', 'EC_SENSOR_Z1_FRONT',
        'TEMPERATURE_SENSOR', 'HUMIDITY_SENSOR'
    ]
    
    print("\n🎯 Checking essential configurations...")
    
    missing = []
    for key in essential:
        if key not in config:
            missing.append(key)
        else:
            print(f"✅ {key}: configured")
    
    if missing:
        warnings.append(f"Missing essential configurations: {', '.join(missing)}")
    
    # Zone completeness
    zones = set()
    for key in config:
        if key.startswith(('VWC_SENSOR_Z', 'EC_SENSOR_Z', 'IRRIGATION_ZONE_')):
            zone_match = re.search(r'Z(\d+)', key)
            if zone_match:
                zones.add(int(zone_match.group(1)))
    
    print(f"\n🌱 Configured zones: {sorted(zones)}")
    
    for zone in sorted(zones):
        zone_entities = [
            f'VWC_SENSOR_Z{zone}_FRONT',
            f'EC_SENSOR_Z{zone}_FRONT',
            f'IRRIGATION_ZONE_{zone}'
        ]
        
        incomplete = []
        for entity in zone_entities:
            if entity not in config:
                incomplete.append(entity)
        
        if incomplete:
            warnings.append(f"Zone {zone} incomplete: missing {', '.join(incomplete)}")
    
    return warnings

def generate_summary(config: Dict[str, str]) -> None:
    """Generate configuration summary."""
    print("\n" + "="*60)
    print("📋 CONFIGURATION SUMMARY")
    print("="*60)
    
    # Count entities by type
    counts = {
        'Switches': len([k for k in config if k.startswith(('PUMP_', 'IRRIGATION_'))]),
        'VWC Sensors': len([k for k in config if k.startswith('VWC_SENSOR_')]),
        'EC Sensors': len([k for k in config if k.startswith('EC_SENSOR_')]),
        'Environmental': len([k for k in config if k.endswith(('_SENSOR', '_HUMIDITY', '_VPD'))]),
        'Parameters': len([k for k in config if any(p in k for p in ['TARGET', 'THRESHOLD', 'VOLUME', 'RATE'])])
    }
    
    for entity_type, count in counts.items():
        print(f"{entity_type:15}: {count:2d} configured")
    
    print(f"\nTotal configuration entries: {len(config)}")

def main():
    """Main configuration validation function."""
    print("🚀 AI-Powered Crop Steering Configuration Validator")
    print("="*55)
    
    # Get config file path
    if len(sys.argv) > 1:
        env_file = sys.argv[1]
    else:
        env_file = "crop_steering.env"
    
    # Load configuration
    config = load_env_file(env_file)
    if not config:
        sys.exit(1)
    
    # Validate configuration
    errors = []
    warnings = []
    
    errors.extend(validate_entities(config))
    errors.extend(validate_numeric_values(config))
    warnings.extend(check_completeness(config))
    
    # Generate summary
    generate_summary(config)
    
    # Report results
    print("\n" + "="*60)
    print("🎯 VALIDATION RESULTS")
    print("="*60)
    
    if errors:
        print(f"\n❌ ERRORS FOUND ({len(errors)}):")
        for error in errors:
            print(f"  • {error}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  • {warning}")
    
    if not errors and not warnings:
        print("\n✅ Configuration validation PASSED!")
        print("🎉 Your crop steering system is ready to use!")
    elif not errors:
        print("\n✅ Configuration validation PASSED with warnings")
        print("💡 Consider addressing warnings for optimal performance")
    else:
        print(f"\n❌ Configuration validation FAILED")
        print("🔧 Please fix the errors above before proceeding")
        sys.exit(1)
    
    print("\n📚 Next steps:")
    print("  1. Start Home Assistant")
    print("  2. Add 'Crop Steering System' integration")
    print("  3. Install AppDaemon modules")
    print("  4. Monitor dashboard for AI learning progress")
    print("\nHappy growing! 🌱")

if __name__ == "__main__":
    main()