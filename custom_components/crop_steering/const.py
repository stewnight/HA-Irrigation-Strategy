"""Constants for the Crop Steering System integration."""

DOMAIN = "crop_steering"

# Configuration keys
CONF_PUMP_SWITCH = "pump_switch"
CONF_MAIN_LINE_SWITCH = "main_line_switch"
CONF_ZONE_SWITCHES = "zone_switches"
CONF_VWC_SENSORS = "vwc_sensors"
CONF_EC_SENSORS = "ec_sensors"

# Default values (Athena method)
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_SUBSTRATE_VOLUME = 10.0
DEFAULT_DRIPPER_FLOW_RATE = 2.0
DEFAULT_FIELD_CAPACITY = 70.0
DEFAULT_MAX_EC = 9.0
DEFAULT_VEG_DRYBACK_TARGET = 50.0
DEFAULT_GEN_DRYBACK_TARGET = 40.0
DEFAULT_P1_TARGET_VWC = 65.0
DEFAULT_P2_VWC_THRESHOLD = 60.0

# Crop steering phases
PHASES = ["P0", "P1", "P2", "P3", "Manual"]
STEERING_MODES = ["Vegetative", "Generative"]

# Crop types (updated with Athena)
CROP_TYPES = [
    "Cannabis_Athena",
    "Cannabis_Hybrid",
    "Cannabis_Indica", 
    "Cannabis_Sativa",
    "Tomato",
    "Lettuce",
    "Basil",
    "Custom"
]