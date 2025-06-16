# AppDaemon Complete Documentation Reference

**Source:** https://appdaemon.readthedocs.io/  
**Generated:** May 29, 2025  
**Purpose:** Comprehensive reference for RAG/MCP server integration covering all AppDaemon documentation sections

## Table of Contents

1. [Overview](#overview)
2. [Getting Started & Installation](#getting-started--installation)
3. [Configuration](#configuration)
4. [Docker Tutorial](#docker-tutorial)
5. [Home Assistant Tutorial](#home-assistant-tutorial)
6. [Writing AppDaemon Apps](#writing-appdaemon-apps)
7. [Community Tutorials](#community-tutorials)
8. [AppDaemon APIs](#appdaemon-apis)
9. [Home Assistant Plugin/API](#home-assistant-pluginapi)
10. [MQTT API Reference](#mqtt-api-reference)
11. [Dashboard Installation](#dashboard-installation)
12. [Dashboard Creation](#dashboard-creation)
13. [Widget Development](#widget-development)
14. [Development Guide](#development-guide)
15. [Internal Documentation](#internal-documentation)
16. [REST/Stream API](#reststream-api)
17. [Upgrading Guides](#upgrading-guides)
18. [Change Log](#change-log)
19. [Index & Reference](#index--reference)

---

## Overview

AppDaemon is a loosely coupled, multi-threaded, sandboxed Python execution environment for writing automation apps for home automation projects, and any environment that requires a robust event driven architecture.

### Key Features
- **Multi-threaded execution environment**
- **Sandboxed Python applications**
- **Event-driven architecture**
- **Home Assistant integration**
- **MQTT event broker support**
- **Configurable dashboard (HADashboard)**
- **Plugin architecture for extensibility**

### Supported Automation Products
- **Home Assistant** - Primary home automation platform
- **MQTT** - Message broker for IoT communication

### Release Information
- AppDaemon has reached a stable point in development
- Features reliable operation and rich functionality
- Releases have been slower in recent months due to stability
- Active community on Discord
- Used daily by core developers

---

## Getting Started & Installation

### Installation Methods

#### 1. Docker Installation (Recommended)

**Supported Architectures:**
- linux/arm/v6
- linux/arm/v7  
- linux/arm64/v8
- linux/amd64

**Basic Docker Command:**
```bash
docker run --name appdaemon \
    --detach \
    --restart=always \
    --network=host \
    -p 5050:5050 \
    -v <conf_folder>:/conf \
    -e HA_URL="http://homeassistant.local:8123" \
    -e TOKEN="my_long_lived_token" \
    acockburn/appdaemon
```

**Configuration Directory:**
- AppDaemon uses `/conf` directory for configuration
- Mount external directory: `-v /my/own/datadir:/conf`
- First run generates sample configuration files

**Environment Variables:**
| Variable | Description |
|----------|-------------|
| HA_URL | URL of your Home Assistant instance |
| TOKEN | Long-Lived token for Home Assistant authentication |

#### 2. Pip Installation

**Requirements:**
- Python 3.10 or 3.11
- Do NOT install in same virtual environment as Home Assistant

**Installation Steps:**
```bash
# Create dedicated virtual environment
python -m venv appdaemon_venv
source appdaemon_venv/bin/activate  # Linux/Mac
# or
appdaemon_venv\Scripts\activate  # Windows

# Install AppDaemon
pip install appdaemon
```

**Platform-Specific Notes:**

**Raspberry Pi OS:**
```bash
sudo apt install python-dev
sudo apt install libffi-dev
```

**Windows:**
- Tested with Python 3.8.1+
- `-d` or `--daemonize` option not supported
- Some internal diagnostics disabled
- WSL recommended for best experience

#### 3. Home Assistant Add-on
Available in Home Assistant Community Add-ons Repository

### Running AppDaemon

**Command Line Usage:**
```bash
appdaemon -c <path_to_config_folder>
```

**CLI Arguments:**
```bash
usage: appdaemon [-h] [-c CONFIG] [-p PIDFILE] [-t TIMEWARP] 
                 [-s STARTTIME] [-e ENDTIME] [-C CONFIGFILE] 
                 [-D {DEBUG,INFO,WARNING,ERROR,CRITICAL}] 
                 [-m MODULEDEBUG MODULEDEBUG] [-v]

options:
  -c CONFIG             full path to config directory
  -p PIDFILE           full path to PID File
  -t TIMEWARP          scheduler speed for time travel
  -s STARTTIME         start time for scheduler
  -e ENDTIME           end time for scheduler
  -C CONFIGFILE        name for config file
  -D DEBUG_LEVEL       global debug level
  -m MODULEDEBUG       module-specific debug
  -v                   show version
  --write_toml         use TOML format for new config files
```

### System Service Setup

#### Systemd Service
Create `/etc/systemd/system/appdaemon@appdaemon.service`:
```ini
[Unit]
Description=AppDaemon
After=home-assistant@homeassistant.service

[Service]
Type=simple
User=%I
ExecStart=/usr/local/bin/appdaemon -c <full_path_to_config_directory>

[Install]
WantedBy=multi-user.target
```

**Activate:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable appdaemon@appdaemon.service --now
```

### Versioning Strategy
- **x.y.z** format
- **x**: Major version (significant changes)
- **y**: Minor version (new features, breaking changes)  
- **z**: Point version (bugfixes, package upgrades)

---

## Configuration

### Configuration File Formats

#### YAML vs TOML
- **Primary:** YAML format (.yaml files)
- **Alternative:** TOML format (.toml files) - Available from 4.3.0+
- **Flexibility:** Can mix both formats
- **Precedence:** YAML takes precedence in conflicts
- **Secrets:** Must use same extension as main config file

#### Conversion Tools
- Online YAML to TOML converters available
- Transform tools at https://transform.tools

### Main Configuration Structure

**File Location:**
- **Docker:** `/conf/appdaemon.yaml`
- **Pip:** `<config_dir>/appdaemon.yaml`

**Top-level Sections:**
```yaml
# appdaemon.yaml
appdaemon:
  # Core AppDaemon settings

api:
  # API configuration

hadashboard:
  # Dashboard settings

plugins:
  # Plugin configurations
```

### AppDaemon Core Configuration

```yaml
appdaemon:
  latitude: 40.8939
  longitude: -74.2483
  elevation: 122
  time_zone: America/New_York
  
  # Threading
  threads: 10
  thread_duration_warning_threshold: 10
  
  # Apps
  app_dir: /conf/apps
  
  # Logging
  logs:
    main_log:
      name: AppDaemon
      filename: /conf/appdaemon.log
    error_log:
      name: Error
      filename: /conf/error.log
    access_log:
      name: Access
      filename: /conf/access.log
      
  # Namespaces
  namespaces:
```

### Plugin Configuration

#### Home Assistant Plugin
```yaml
plugins:
  HASS:
    type: hass
    ha_url: http://127.0.0.1:8123
    token: !secret home_assistant_token
    namespace: default
    
    # Optional settings
    app_init_delay: 10
    plugin_startup_conditions:
      - state: sensor.dummy == "ready"
    disable_apps_on_terminate: true
```

#### MQTT Plugin
```yaml
plugins:
  MQTT:
    type: mqtt
    namespace: mqtt
    
    # MQTT Broker settings
    client_host: 127.0.0.1
    client_port: 1883
    client_username: mqtt_user
    client_password: !secret mqtt_password
    
    # Topics
    client_topics:
      - topic: "home/+/+"
        qos: 1
      - topic: "sensors/#"
        qos: 0
```

### App Configuration

```yaml
# apps.yaml
hello_world:
  module: hello
  class: HelloWorld
  
motion_lights:
  module: motion_detection
  class: MotionLights
  dependencies:
    - hello_world
  parameters:
    sensor: binary_sensor.motion_detector
    lights:
      - light.living_room
      - light.kitchen
```

### Secrets Management

**secrets.yaml:**
```yaml
home_assistant_token: "your_long_lived_token_here"
mqtt_password: "your_mqtt_password"
api_key: "your_api_key"
```

**Usage in configuration:**
```yaml
plugins:
  HASS:
    token: !secret home_assistant_token
```

---

## Docker Tutorial

### Introduction
Docker provides containerized deployment for AppDaemon, ensuring consistent environments and simplified dependency management.

### Requirements
- Docker installed and running
- Home Assistant accessible
- Basic Docker knowledge helpful

### Basic Setup

#### Quick Start
```bash
# Create configuration directory
mkdir /my/appdaemon/config

# Run AppDaemon container
docker run --name appdaemon \
    --detach \
    --restart=always \
    --network=host \
    -p 5050:5050 \
    -v /my/appdaemon/config:/conf \
    -e HA_URL="http://homeassistant.local:8123" \
    -e TOKEN="your_token_here" \
    acockburn/appdaemon
```

### Persistent Configuration

#### Requirements File Support
Create `requirements.txt` in config directory:
```txt
requests==2.28.2
paho-mqtt==1.6.1
```

#### System Packages
Create `system_packages.txt`:
```txt
build-base
gcc
curl
```

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  appdaemon:
    image: acockburn/appdaemon:latest
    container_name: appdaemon
    restart: unless-stopped
    ports:
      - "5050:5050"
    volumes:
      - ./config:/conf
    environment:
      - HA_URL=http://homeassistant.local:8123
      - TOKEN=${HA_TOKEN}
      - DASH_URL=http://$HOSTNAME:5050
    depends_on:
      - homeassistant
```

### Advanced Configuration

#### Network Configuration
```bash
# Host networking (recommended)
--network=host

# Bridge networking with port mapping
-p 5050:5050
```

#### Volume Mounts
```bash
# Configuration
-v /host/config:/conf

# Additional app directories
-v /host/custom_apps:/conf/custom_apps

# Logs
-v /host/logs:/conf/logs
```

### Troubleshooting

#### Common Issues
1. **Permission errors**: Ensure proper file ownership
2. **Network connectivity**: Verify HA_URL accessibility  
3. **Token authentication**: Check token validity
4. **Resource limits**: Monitor container resources

#### Log Analysis
```bash
# View container logs
docker logs appdaemon

# Follow logs in real-time
docker logs -f appdaemon

# Access container shell
docker exec -it appdaemon /bin/bash
```

---

## Home Assistant Tutorial

### Introduction
This tutorial guides Home Assistant users through AppDaemon integration and app development.

### Prerequisites
- Home Assistant running and accessible
- Long-lived access token created
- Basic Python knowledge helpful

### Initial Setup

#### Creating Long-Lived Token
1. Go to Home Assistant Profile
2. Scroll to "Long-Lived Access Tokens"
3. Click "Create Token"
4. Give it a descriptive name
5. Copy the token (save securely)

#### Basic Configuration
```yaml
# appdaemon.yaml
appdaemon:
  latitude: !secret latitude
  longitude: !secret longitude
  elevation: !secret elevation
  time_zone: !secret time_zone
  
plugins:
  HASS:
    type: hass
    ha_url: !secret ha_url
    token: !secret ha_token
```

### Your First App

#### Hello World Example
Create `apps/hello.py`:
```python
import appdaemon.plugins.hass.hassapi as hass

class HelloWorld(hass.Hass):
    def initialize(self):
        self.log("Hello from AppDaemon!")
        self.log(f"Current time is: {self.get_now()}")
        
        # Listen for state changes
        self.listen_state(self.state_changed, "light.living_room")
        
        # Schedule recurring task
        self.run_every(self.heartbeat, "now", 300)  # Every 5 minutes
    
    def state_changed(self, entity, attribute, old, new, kwargs):
        self.log(f"Light state changed from {old} to {new}")
    
    def heartbeat(self, kwargs):
        self.log("AppDaemon is alive!")
```

#### App Configuration
Add to `apps/apps.yaml`:
```yaml
hello_world:
  module: hello
  class: HelloWorld
```

### Common Patterns

#### Motion-Activated Lights
```python
import appdaemon.plugins.hass.hassapi as hass
import datetime

class MotionLights(hass.Hass):
    def initialize(self):
        self.motion_sensor = self.args["motion_sensor"]
        self.lights = self.args["lights"]
        self.timeout = self.args.get("timeout", 300)  # 5 minutes default
        
        self.listen_state(self.motion_detected, self.motion_sensor, 
                         new="on")
        self.listen_state(self.motion_cleared, self.motion_sensor, 
                         new="off")
        
        self.timer_handle = None
    
    def motion_detected(self, entity, attribute, old, new, kwargs):
        self.log("Motion detected, turning on lights")
        
        # Cancel existing timer
        if self.timer_handle:
            self.cancel_timer(self.timer_handle)
        
        # Turn on lights
        for light in self.lights:
            self.turn_on(light)
    
    def motion_cleared(self, entity, attribute, old, new, kwargs):
        self.log("Motion cleared, starting timer")
        self.timer_handle = self.run_in(self.lights_off, self.timeout)
    
    def lights_off(self, kwargs):
        self.log("Timeout reached, turning off lights")
        for light in self.lights:
            self.turn_off(light)
        self.timer_handle = None
```

---

## Writing AppDaemon Apps

### App Anatomy

AppDaemon apps are Python classes that inherit from AppDaemon base classes and respond to events through callback mechanisms.

### Base Classes

#### ADAPI (Standard)
```python
from appdaemon.plugins.hass import Hass

class MyApp(Hass):
    def initialize(self):
        # App initialization
        pass
```

#### MQTT Support
```python
from appdaemon.plugins.mqtt import Mqtt

class MqttApp(Mqtt):
    def initialize(self):
        # MQTT-specific initialization
        pass
```

#### Multi-namespace (ADBase)
```python
from appdaemon.adapi import ADAPI
from appdaemon.adbase import ADBase
from appdaemon.plugins.mqtt import Mqtt

class MultiApp(ADBase):
    adapi: ADAPI
    mqttapi: Mqtt
    
    def initialize(self):
        self.adapi = self.get_ad_api()
        self.mqttapi = self.get_plugin_api("mqtt")
```

### App Lifecycle

#### The initialize() Method
**Required for every app:**
```python
def initialize(self):
    # Called when app starts
    # Register callbacks
    # Setup initial state
    pass
```

**When initialize() is called:**
- Initial AppDaemon startup
- Code changes (hot reload)
- Module parameter changes
- App configuration changes
- Daylight Saving Time changes
- Plugin restarts

---

## Community Tutorials

### Available Community Resources

The AppDaemon community has created numerous tutorials and examples:

#### Tutorial Series
1. **AppDaemon For Beginners** - Basic concepts and setup
2. **AppDaemon Tutorial #1: Tracker-Notifier** - Device tracking notifications
3. **AppDaemon Tutorial #2: Errorlog Notifications** - Error monitoring
4. **AppDaemon Tutorial #3: Utility Functions** - Reusable utilities
5. **AppDaemon Tutorial #4: Libraries & Interactivity** - Advanced techniques

#### Example Applications
- **Home Presence AppDaemon App** - Occupancy detection
- **App #1: Doorbell notification** - Smart doorbell integration
- **App #2: Smart Light** - Intelligent lighting control
- **App #3: Smart Radiator** - Climate control automation
- **App #4: Boiler Alert** - Equipment monitoring
- **App #5: Smart Radiator (Generic)** - Reusable climate control
- **App #6: Window Alert** - Security monitoring
- **App #7: Boiler Temperature Alert** - Temperature monitoring
- **App #8: Detect sequence of events** - Pattern recognition

---

## AppDaemon APIs

### ADAPI Class

The AppDaemon API provides high-level functionality for creating automation apps.

#### Core API Methods

**App Creation Pattern:**
```python
from appdaemon.adapi import ADAPI

class MyApp(ADAPI):
    def initialize(self):
        self.log("MyApp is starting")
        
        # Use any of the ADAPI methods
        # handle = self.listen_state(...)
        # handle = self.listen_event(...)
        # handle = self.run_in(...)
        # handle = self.run_every(...)
```

#### State Management
```python
# Get entity state
state = self.get_state("light.living_room")
attributes = self.get_state("light.living_room", attribute="all")
brightness = self.get_state("light.living_room", attribute="brightness")

# Set entity state  
self.set_state("sensor.custom", state="active", attributes={"custom": "value"})

# Check entity existence
if self.entity_exists("sensor.temperature"):
    temp = self.get_state("sensor.temperature")

# Get multiple states
states = self.get_state()  # All entities
light_states = self.get_state("light")  # All lights
```

#### Event Handling
```python
# Listen for state changes
handle = self.listen_state(callback, "light.living_room")
handle = self.listen_state(callback, "sensor.temperature", old=">25", new="<=25")

# Listen for events
handle = self.listen_event(callback, "my_custom_event")
handle = self.listen_event(callback, "state_changed")

# Fire events
self.fire_event("custom_event", data={"key": "value"})
```

#### Scheduling
```python
# One-time scheduling
handle = self.run_in(callback, 30)  # 30 seconds
handle = self.run_at(callback, "16:30:00")
handle = self.run_at(callback, datetime.time(16, 30, 0))

# Recurring scheduling  
handle = self.run_daily(callback, "08:00:00")
handle = self.run_hourly(callback, datetime.time(0, 30, 0))
handle = self.run_every(callback, "now", 60)  # Every 60 seconds

# Cancel timers
self.cancel_timer(handle)
```

#### Service Calls
```python
# Basic service calls
self.call_service("light/turn_on", entity_id="light.living_room")
self.call_service("notify/pushbullet", message="Hello", title="AppDaemon")

# Return service call results
result = self.call_service("weather/get_forecast", entity_id="weather.home", return_result=True)
```

#### Utility Functions
```python
# Time functions
now = self.get_now()
today = self.date()
time_obj = self.parse_time("16:30:00")

# Sun functions
sunrise_time = self.sunrise()
sunset_time = self.sunset()
is_daytime = self.sun_up()

# Conversion functions
temp_f = self.celsius_to_fahrenheit(20)
temp_c = self.fahrenheit_to_celsius(68)
```

### Entity Class

Provides object-oriented entity manipulation:

```python
# Get entity object
light = self.get_entity("light.living_room")

# Entity operations
light.turn_on(brightness=128)
light.turn_off()
current_state = light.get_state()
attributes = light.get_attributes()

# Entity checks
if light.exists():
    light.toggle()
```

---

## Home Assistant Plugin/API

### HASS API Reference

The Home Assistant plugin provides comprehensive integration with Home Assistant.

#### Installation and Configuration
```yaml
plugins:
  HASS:
    type: hass
    ha_url: http://127.0.0.1:8123
    token: !secret home_assistant_token
    namespace: default
```

#### Core Methods

#### Entity Control
```python
# Light control
self.turn_on("light.living_room", brightness=255, color_name="red")
self.turn_off("light.living_room")
self.toggle("light.living_room")

# Generic entity control
self.turn_on("switch.coffee_maker")
self.turn_off("fan.bedroom")

# Service calls with parameters
self.call_service("climate/set_temperature", 
                 entity_id="climate.living_room", 
                 temperature=22)
```

#### Advanced State Operations
```python
# State with history
history = self.get_history(entity_id="sensor.temperature", days=1)

# State filtering
outdoor_sensors = self.get_state("sensor", attribute="all")
filtered = {k: v for k, v in outdoor_sensors.items() if "outdoor" in k}

# Bulk operations
all_lights = self.get_state("light")
for light in all_lights:
    if self.get_state(light) == "on":
        self.turn_off(light)
```

#### Event Subscription
```python
# Home Assistant specific events
self.listen_event(self.handle_automation, "automation_triggered")
self.listen_event(self.handle_script, "script_started")
self.listen_event(self.handle_service_call, "call_service")

def handle_automation(self, event_name, data, kwargs):
    automation = data.get("entity_id")
    self.log(f"Automation triggered: {automation}")
```

#### Templates and Calculations
```python
# Template rendering
template = "{{ states('sensor.temperature') | float }}"
result = self.render_template(template)

# State calculations
average_temp = self.average_state(["sensor.temp1", "sensor.temp2", "sensor.temp3"])
```

---

## MQTT API Reference

### MQTT Plugin Configuration

```yaml
plugins:
  MQTT:
    type: mqtt
    namespace: mqtt
    client_host: 127.0.0.1
    client_port: 1883
    client_username: mqtt_user
    client_password: !secret mqtt_password
    client_topics:
      - topic: "home/+/+"
        qos: 1
      - topic: "sensors/#"
        qos: 0
    birth_topic: "appdaemon/status"
    birth_payload: "online"
    will_topic: "appdaemon/status"
    will_payload: "offline"
```

### MQTT API Methods

#### Publishing Messages
```python
from appdaemon.plugins.mqtt import Mqtt

class MqttApp(Mqtt):
    def initialize(self):
        # Publish simple message
        self.mqtt_publish("home/sensors/temperature", 23.5)
        
        # Publish with QoS and retain
        self.mqtt_publish("home/status/online", "true", qos=1, retain=True)
        
        # Publish JSON data
        data = {"temperature": 23.5, "humidity": 45.2}
        self.mqtt_publish("home/sensors/data", data)
```

#### Subscribing to Topics
```python
def initialize(self):
    # Subscribe to specific topic
    self.mqtt_subscribe("home/sensors/temperature")
    
    # Subscribe with callback
    self.mqtt_subscribe("home/commands/+", self.command_received)
    
    # Subscribe to wildcard topics
    self.mqtt_subscribe("sensors/+/temperature", self.temperature_received)

def mqtt_message_received(self, topic, payload, qos, retain):
    """Default callback for subscribed topics"""
    self.log(f"Received: {topic} = {payload}")

def command_received(self, topic, payload, qos, retain):
    """Custom callback for command topics"""
    command = topic.split("/")[-1]
    self.log(f"Command received: {command} = {payload}")
    
    if command == "lights":
        if payload == "on":
            self.turn_on_lights()
        elif payload == "off":
            self.turn_off_lights()
```

---

## Dashboard Installation

### HADashboard Overview

HADashboard provides web-based dashboards for controlling and monitoring your home automation system.

### Installation Requirements

#### System Requirements
- AppDaemon 4.0+ installed and running
- Web browser with modern JavaScript support
- Network connectivity to AppDaemon host

#### Configuration Prerequisites
```yaml
# appdaemon.yaml
hadashboard:
  dash_url: http://192.168.1.100:5050
  dash_dir: /conf/dashboards
  dash_compile_on_start: true
  dash_force_compile: false
```

### Basic Setup

#### Enable Dashboard
```yaml
# appdaemon.yaml
appdaemon:
  # Core AppDaemon config

api:
  # API configuration  

hadashboard:
  dash_url: http://<your_host>:5050
  dash_dir: /conf/dashboards
  dash_compile_on_start: true
  dash_force_compile: false
  
  # Theme and styling
  main_log: /conf/dash.log
  dash_css_dir: /conf/custom_css
  dash_js_dir: /conf/custom_js
  
  # Security
  dash_password: !secret dashboard_password
```

#### Directory Structure
```
/conf/
  ├── dashboards/
  │   ├── main.dash
  │   ├── lights.dash
  │   └── climate.dash
  ├── custom_css/
  │   └── custom.css
  └── custom_js/
      └── custom.js
```

---

## Dashboard Creation

### Creating Custom Dashboards

Dashboard creation involves designing layouts, configuring widgets, and styling the interface.

### Dashboard Structure

#### Basic Dashboard Anatomy
```yaml
##
## Dashboard Title
##

# Global Settings
title: My Dashboard
widget_dimensions: [120, 120]  # Width x Height in pixels
widget_margins: [5, 5]         # Horizontal x Vertical margins
columns: 8                     # Grid columns

# Layout Definition
layout:
  - row1_widgets
  - row2_widgets  
  - row3_widgets

# Widget Definitions
widget_name:
  widget_type: type_name
  entity: entity_id
  # Additional parameters
```

#### Widget Configuration Examples
```yaml
temperature:
  widget_type: sensor
  entity: sensor.living_room_temperature
  title: Living Room
  title2: Temperature
  units: °C
  precision: 1
  
main_light:
  widget_type: light
  entity: light.living_room
  title: Living Room Light
  icon_on: mdi-lightbulb-on
  icon_off: mdi-lightbulb
  brightness_slider: 1
  
thermostat:
  widget_type: climate
  entity: climate.living_room
  title: Climate Control
  units: °C
  precision: 1
  step: 0.5
```

---

## Widget Development

### Creating Custom Widgets

Custom widgets extend HADashboard functionality with specialized displays and controls.

### Widget Architecture

#### Widget Components
1. **YAML Definition** - Widget configuration and metadata
2. **HTML Template** - Widget structure and layout
3. **CSS Styles** - Widget appearance and styling
4. **JavaScript Logic** - Widget behavior and interactivity

#### Basic Custom Widget Structure
```yaml
# my_widget.yaml
widget_type: my_widget
fields:
  - entity
  - title
  - custom_field

css: |
  .my-widget {
    background: linear-gradient(45deg, #667eea, #764ba2);
    border-radius: 15px;
  }

javascript: |
  function myWidgetFunction(widget_id, params) {
    // Custom widget logic
    setTimeout(function() {
      updateMyWidget(widget_id);
    }, 1000);
  }
```

---

## Development Guide

### Development Environment Setup

#### Requirements
- Python 3.10+ development environment
- Git for version control
- Code editor with Python support
- Virtual environment tools

#### Setting up Development Environment
```bash
# Clone AppDaemon repository
git clone https://github.com/AppDaemon/appdaemon.git
cd appdaemon

# Create virtual environment
python -m venv dev_env
source dev_env/bin/activate  # Linux/Mac
# or
dev_env\Scripts\activate  # Windows

# Install development dependencies
pip install -e .
pip install -r requirements_dev.txt
```

### Contributing Guidelines

#### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Include type hints where appropriate

#### Testing
```bash
# Run unit tests
pytest tests/

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=appdaemon tests/
```

#### Submitting Changes
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request
5. Address review feedback

---

## Internal Documentation

### AppDaemon Architecture

#### Core Components
- **App Manager** - Handles app lifecycle and loading
- **Scheduler** - Manages time-based callbacks and events
- **State Manager** - Tracks entity states and changes
- **Plugin System** - Interfaces with external systems
- **Event System** - Handles event distribution and callbacks

#### Threading Model
- **Main Thread** - Core AppDaemon operations
- **Scheduler Thread** - Time-based callback execution
- **Worker Threads** - App callback execution
- **Plugin Threads** - External system communication

#### Plugin Interface
```python
class PluginBase:
    def __init__(self, ad, name, args):
        self.AD = ad
        self.name = name
        self.config = args
    
    def start(self):
        # Plugin startup logic
        pass
    
    def stop(self):
        # Plugin shutdown logic
        pass
    
    def get_namespace(self):
        return self.config.get("namespace", "default")
```

---

## REST/Stream API

### REST API Endpoints

AppDaemon provides REST API access for external integration and monitoring.

#### Base URL Structure
```
http://<appdaemon_host>:5050/api/appdaemon/
```

#### Authentication
```yaml
# appdaemon.yaml
api:
  api_key: !secret api_key
  api_ssl_certificate: /path/to/cert.pem
  api_ssl_key: /path/to/key.pem
```

#### Available Endpoints

**App Management:**
```bash
# List all apps
GET /api/appdaemon/apps

# Get app state
GET /api/appdaemon/apps/{app_name}

# Start/stop app
POST /api/appdaemon/apps/{app_name}/start
POST /api/appdaemon/apps/{app_name}/stop

# Reload app
POST /api/appdaemon/apps/{app_name}/reload
```

**State Operations:**
```bash
# Get entity state
GET /api/appdaemon/state/{namespace}/{entity_id}

# Set entity state
POST /api/appdaemon/state/{namespace}/{entity_id}
Content-Type: application/json
{
  "state": "on",
  "attributes": {"brightness": 255}
}

# Get all states
GET /api/appdaemon/state/{namespace}
```

**Service Calls:**
```bash
# Call service
POST /api/appdaemon/services/{namespace}/{domain}/{service}
Content-Type: application/json
{
  "entity_id": "light.living_room",
  "brightness": 128
}
```

**Events:**
```bash
# Fire event
POST /api/appdaemon/events/{namespace}/{event_type}
Content-Type: application/json
{
  "data": {"key": "value"}
}

# Listen to events (WebSocket)
WS /api/appdaemon/stream
```

### Stream API (WebSocket)

#### Connection
```javascript
const ws = new WebSocket('ws://appdaemon_host:5050/api/appdaemon/stream');

ws.onopen = function() {
    console.log('Connected to AppDaemon stream');
    
    // Subscribe to state changes
    ws.send(JSON.stringify({
        type: 'listen_state',
        namespace: 'default',
        entity_id: 'light.living_room'
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

#### Stream Message Types
```javascript
// State change notification
{
    "type": "state_changed",
    "namespace": "default",
    "entity_id": "light.living_room",
    "new_state": {
        "state": "on",
        "attributes": {"brightness": 255}
    },
    "old_state": {
        "state": "off",
        "attributes": {}
    }
}

// Event notification
{
    "type": "event",
    "namespace": "default",
    "event_type": "automation_triggered",
    "data": {"entity_id": "automation.morning_routine"}
}

// App state notification
{
    "type": "app_state",
    "app_name": "motion_lights",
    "state": "running"
}
```

---

## Upgrading Guides

### Upgrading from 3.x to 4.x

#### Major Changes
- **Python Version**: Minimum Python 3.8 (now 3.10+)
- **Configuration Format**: Support for TOML added
- **Plugin Architecture**: Redesigned plugin system
- **API Changes**: Some deprecated methods removed

#### Breaking Changes

**Configuration:**
```yaml
# 3.x format
appdaemon:
  plugins:
    HASS:
      type: hass
      ha_url: http://homeassistant:8123
      ha_key: your_password

# 4.x format  
plugins:
  HASS:
    type: hass
    ha_url: http://homeassistant:8123
    token: your_long_lived_token
```

**API Methods:**
```python
# 3.x deprecated methods
self.get_app()  # Removed
self.dashboard()  # Removed
self.get_main_log()  # Changed

# 4.x replacements
self.get_ad_api()
self.get_plugin_api()
self.get_user_log()
```

#### Migration Steps

1. **Update Python Environment**
```bash
# Install Python 3.10+
python --version  # Check current version
# Upgrade if necessary
```

2. **Update Configuration**
```bash
# Backup existing config
cp appdaemon.yaml appdaemon.yaml.backup

# Update configuration format
# Move plugin config to top level
```

3. **Update Apps**
```python
# Review app code for deprecated methods
# Update imports if necessary
# Test apps thoroughly
```

4. **Test Migration**
```bash
# Start AppDaemon in test mode
appdaemon -c /config -D DEBUG

# Check logs for warnings
# Verify all apps load correctly
```

### Upgrading from 2.x to 3.x

#### Major Changes
- **Configuration Structure**: Complete reorganization
- **Plugin System**: Introduction of plugin architecture
- **App Structure**: New base classes and imports

#### Migration Guide

**Configuration Migration:**
```yaml
# 2.x format
[AppDaemon]
ha_url = http://homeassistant:8123
ha_key = your_password
logfile = STDOUT
errorfile = STDERR
app_dir = /conf/apps
threads = 10

# 3.x format
appdaemon:
  logfile: STDOUT
  errorfile: STDERR
  app_dir: /conf/apps
  threads: 10
  plugins:
    HASS:
      type: hass
      ha_url: http://homeassistant:8123
      ha_key: your_password
```

**App Code Migration:**
```python
# 2.x import
import appdaemon.appapi as appapi

class MyApp(appapi.AppDaemon):
    def initialize(self):
        pass

# 3.x import
import appdaemon.plugins.hass.hassapi as hass

class MyApp(hass.Hass):
    def initialize(self):
        pass
```

---

## Change Log

### Version 4.4.2 (Latest)
**Release Date:** March 2024

**Bug Fixes:**
- Fixed memory leak in state processing
- Resolved dashboard compilation issues
- Corrected timezone handling in scheduler
- Fixed MQTT reconnection logic

**Improvements:**
- Enhanced error reporting for app failures
- Optimized state change processing
- Updated dependencies for security

### Version 4.4.0
**Release Date:** November 2023

**New Features:**
- **Multi-arch Docker Support**: ARM64, ARM v7/v6 support
- **TOML Configuration**: Alternative to YAML configuration
- **Enhanced Plugin API**: Improved plugin development framework
- **Widget Improvements**: New dashboard widget types

**Breaking Changes:**
- Minimum Python version increased to 3.10
- Some deprecated API methods removed
- Configuration validation strengthened

### Version 4.3.0
**Release Date:** July 2023

**New Features:**
- **Async App Support**: Experimental async/await support
- **Enhanced Constraints**: More flexible callback constraints
- **Improved Logging**: Better log formatting and filtering
- **Dashboard Themes**: New built-in themes

**Bug Fixes:**
- State synchronization improvements
- Memory usage optimizations
- Dashboard responsiveness fixes

### Version 4.2.0
**Release Date:** March 2023

**New Features:**
- **Entity Registry**: Track entity creation/deletion
- **Service Call Results**: Return values from service calls
- **Enhanced Debugging**: Better error messages and stack traces
- **Docker Improvements**: Smaller image size, faster startup

### Version 4.1.0
**Release Date:** October 2022

**Major Features:**
- **Multi-Architecture Docker**: Support for ARM platforms
- **Plugin Enhancements**: Improved plugin isolation
- **Dashboard Security**: Enhanced authentication options
- **Performance Improvements**: Faster app loading and execution

### Version 4.0.0
**Release Date:** April 2022

**Major Release - Breaking Changes:**
- **Python 3.8+ Required**: Dropped Python 3.7 support
- **Configuration Restructure**: New YAML structure
- **Plugin Architecture**: Complete plugin system redesign
- **Token Authentication**: Replaced password with tokens
- **Modern Dependencies**: Updated all major dependencies

---

## Index & Reference

### Quick Reference Tables

#### Configuration Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `latitude` | float | None | Geographic latitude |
| `longitude` | float | None | Geographic longitude |
| `elevation` | integer | None | Elevation in meters |
| `time_zone` | string | None | Timezone (e.g., America/New_York) |
| `threads` | integer | 10 | Number of worker threads |
| `app_dir` | string | ./apps | Directory containing apps |
| `thread_duration_warning_threshold` | integer | 10 | Callback duration warning (seconds) |

#### API Methods
| Method | Purpose | Returns |
|--------|---------|---------|
| `get_state(entity)` | Get entity state | string |
| `set_state(entity, state)` | Set entity state | None |
| `listen_state(callback, entity)` | Listen for state changes | handle |
| `run_in(callback, delay)` | Schedule callback | handle |
| `run_at(callback, time)` | Schedule at time | handle |
| `run_daily(callback, time)` | Schedule daily | handle |
| `call_service(service, **kwargs)` | Call service | result |
| `fire_event(event, **kwargs)` | Fire event | None |

#### Event Types
| Event | Trigger | Data Fields |
|-------|---------|-------------|
| `state_changed` | Entity state change | entity_id, old_state, new_state |
| `automation_triggered` | Automation runs | entity_id, source |
| `script_started` | Script execution | entity_id |
| `service_called` | Service call | domain, service, data |
| `time_changed` | Time tick | now |

#### Widget Types
| Widget | Purpose | Key Parameters |
|--------|---------|----------------|
| `sensor` | Display sensor values | entity, units, precision |
| `binary_sensor` | On/off status | entity, state_map |
| `switch` | Toggle control | entity |
| `light` | Light control | entity, brightness_slider |
| `climate` | Thermostat control | entity, units, step |
| `media_player` | Media control | entity, show_volume |
| `camera` | Live video feed | entity, refresh |
| `weather` | Weather display | entity |

#### Constraint Types
| Constraint | Description | Example |
|------------|-------------|---------|
| `constrain_start_time` | Start time limit | "06:00:00" |
| `constrain_end_time` | End time limit | "22:00:00" |
| `constrain_days` | Day restrictions | "mon,tue,wed,thu,fri" |
| `constrain_input_boolean` | State condition | "input_boolean.home,on" |
| `constrain_sun` | Sun position | "up" or "down" |

### Error Codes and Troubleshooting

#### Common Error Codes
| Code | Error | Solution |
|------|-------|----------|
| `ADAPI001` | App initialization failed | Check app syntax and imports |
| `ADAPI002` | Invalid entity ID | Verify entity exists in Home Assistant |
| `ADAPI003` | Service call failed | Check service name and parameters |
| `ADAPI004` | Callback exception | Review callback code for errors |
| `CONFIG001` | Configuration validation | Check YAML syntax and structure |
| `PLUGIN001` | Plugin connection failed | Verify plugin configuration |

#### Debugging Commands
```bash
# Enable debug logging
appdaemon -c /config -D DEBUG

# Check specific app
appdaemon -c /config -D DEBUG -m myapp DEBUG

# Validate configuration
appdaemon -c /config --check-config

# Test time travel
appdaemon -c /config -s "2024-01-01 00:00:00" -e "2024-01-02 00:00:00"
```

### File Structure Reference

#### Standard Directory Layout
```
/conf/
├── appdaemon.yaml          # Main configuration
├── secrets.yaml            # Sensitive data
├── apps/                   # Application directory
│   ├── apps.yaml          # App configuration
│   ├── hello.py           # Example app
│   └── modules/           # Shared modules
├── dashboards/            # Dashboard files
│   ├── main.dash         # Main dashboard
│   └── mobile.dash       # Mobile dashboard
├── custom_css/           # Custom CSS
├── custom_js/            # Custom JavaScript
├── logs/                 # Log files
└── compiled/             # Compiled dashboard assets
```

#### Essential Files
- **appdaemon.yaml**: Core configuration file
- **secrets.yaml**: Secure credential storage  
- **apps.yaml**: App instance configuration
- **requirements.txt**: Python package dependencies
- **system_packages.txt**: System package dependencies (Docker)

### Performance Optimization

#### Best Practices
1. **Minimize State Queries**: Cache frequently accessed states
2. **Efficient Callbacks**: Use constraints to limit unnecessary executions
3. **Batch Operations**: Group multiple state changes when possible
4. **Optimize Imports**: Import only necessary modules
5. **Use Entity Objects**: Leverage entity abstraction for cleaner code

#### Memory Management
```python
# Good practices
class OptimizedApp(hass.Hass):
    def initialize(self):
        # Cache commonly used values
        self.entities = self.args.get("entities", [])
        
        # Use constraints to limit callbacks
        self.listen_state(self.callback, self.entities,
                         constrain_start_time="06:00:00",
                         constrain_end_time="22:00:00")
    
    def callback(self, entity, attribute, old, new, kwargs):
        # Avoid expensive operations in callbacks
        if new != old:
            self.handle_change(entity, new)
```

---

*This comprehensive documentation reference covers all major aspects of AppDaemon, from basic installation to advanced development topics. Use this as a foundation for building sophisticated home automation applications and integrating with RAG/MCP servers for intelligent assistance.*
