# Crop Steering System: Complete Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [System Architecture](#system-architecture)
3. [Component Relationships](#component-relationships)
4. [Data Flow Map](#data-flow-map)
5. [Logic Flow by Phase](#logic-flow-by-phase)
   - [P0: Pre-Irrigation Dry Back](#p0-pre-irrigation-dry-back)
   - [P1: Ramp-Up Phase](#p1-ramp-up-phase)
   - [P2: Maintenance Phase](#p2-maintenance-phase)
   - [P3: Overnight Dry Back](#p3-overnight-dry-back)
6. [Zone Control Logic](#zone-control-logic)
7. [EC Adjustment Logic](#ec-adjustment-logic)
8. [Dryback Detection System](#dryback-detection-system)
9. [Configuration Blueprint System](#configuration-blueprint-system)
10. [EC Stacking Automation](#ec-stacking-automation)
11. [Dashboard Integration](#dashboard-integration)
12. [Complete Entity Relationship Map](#complete-entity-relationship-map)
13. [Troubleshooting Guide](#troubleshooting-guide)

## System Overview

The Crop Steering system is designed to manage irrigation for growing operations using principles of precision agriculture. It implements a four-phase approach to irrigation control, with each phase optimized for different periods in the plant's daily growth cycle.

### Core Principles

1. **Precision Irrigation**: Deliver exactly the right amount of water at the right time
2. **EC Management**: Balance nutrient concentration through irrigation timing and duration
3. **Dryback Control**: Monitor and manage substrate moisture levels through calculated dry periods
4. **Zone-Specific Control**: Manage multiple growing zones with individual sensors and controls
5. **Growth Mode Switching**: Toggle between vegetative and generative modes with appropriate parameter adjustments

### System Goals

- Maximize root zone oxygen levels
- Prevent over-saturation or excessive dryness
- Maintain optimal EC levels in the root zone
- Create appropriate stress for vegetative or generative growth
- Ensure reliable, automated irrigation control

## System Architecture

```mermaid
graph TB
    subgraph "User Interface"
        BLUEPRINT1["Entity Setup Blueprint"]
        BLUEPRINT2["Parameters Blueprint"]
        DASHBOARD["Dashboards & Cards"]
    end

    subgraph "Data Storage"
        CONFIG["Configuration Helpers<br>(input_text)"]
        PARAMS["Parameter Helpers<br>(input_number, input_select)"]
        ZONES["Zone Control Helpers<br>(input_boolean)"]
    end

    subgraph "Processing Layer"
        YAML["YAML-based Processing<br>(Templates, Automations)"]
        APPDAEMON["AppDaemon App<br>(Advanced Logic)"]
    end

    subgraph "Sensor Layer"
        VWC["VWC Sensors"]
        EC["EC Sensors"]
    end

    subgraph "Actuator Layer"
        PUMP["Pump/Main Valve"]
        ZONES_V["Zone Valves"]
        WASTE["Waste/Drain Valve"]
    end

    BLUEPRINT1-->CONFIG
    BLUEPRINT2-->PARAMS
    CONFIG-->YAML
    CONFIG-->APPDAEMON
    PARAMS-->YAML
    PARAMS-->APPDAEMON
    ZONES-->YAML
    ZONES-->APPDAEMON
    VWC-->YAML
    VWC-->APPDAEMON
    EC-->YAML
    EC-->APPDAEMON
    YAML-->PUMP
    YAML-->ZONES_V
    YAML-->WASTE
    APPDAEMON-->PUMP
    APPDAEMON-->ZONES_V
    APPDAEMON-->WASTE
    YAML-->DASHBOARD
    APPDAEMON-->DASHBOARD
```

The architecture follows a layered approach with clear separation between:
- User configuration (blueprints)
- Data storage (Home Assistant helpers)
- Processing (YAML templates and AppDaemon)
- Sensors and actuators (physical devices)

## Component Relationships

```mermaid
flowchart TB
    subgraph "YAML Package Files"
        PKG["crop_steering_package.yaml<br>(Main Package)"]
        VARS["crop_steering_variables.yaml<br>(Helpers & Parameters)"]
        SENS["crop_steering_improved_sensors.yaml<br>(Template Sensors)"]
        AGG["crop_steering_aggregation_sensors.yaml<br>(Sensor Aggregation)"]
        AUTO["crop_steering_improved_automations.yaml<br>(Phase Control & Irrigation)"]
        ZONE["crop_steering_zone_controls.yaml<br>(Multi-Zone Support)"]
        DRY["crop_steering_dryback_tracking.yaml<br>(Dryback Detection)"]
    end

    subgraph "Blueprints"
        ENT["crop_steering_entity_setup_blueprint.yaml<br>(Entity Configuration)"]
        PARAM["crop_steering_parameters_blueprint.yaml<br>(Parameter Configuration)"]
    end

    subgraph "AppDaemon"
        PYAPP["crop_steering_app.py<br>(AppDaemon Application)"]
        APPCONFIG["apps.yaml<br>(AppDaemon Configuration)"]
    end

    subgraph "Dashboard"
        CARDS["Dashboard Cards<br>(Visualization & Control)"]
    end

    PKG --> VARS
    PKG --> SENS
    PKG --> AGG
    PKG --> AUTO
    PKG --> ZONE
    PKG --> DRY

    ENT --> VARS
    PARAM --> VARS

    VARS --> PYAPP
    SENS --> PYAPP
    AGG --> PYAPP
    AUTO --> PYAPP
    ZONE --> PYAPP
    DRY --> PYAPP

    APPCONFIG --> PYAPP

    VARS --> CARDS
    SENS --> CARDS
    AGG --> CARDS
    AUTO --> CARDS
    ZONE --> CARDS
    DRY --> CARDS
    PYAPP --> CARDS
```

## Data Flow Map

```mermaid
graph LR
    subgraph "Inputs"
        VWC_IN["VWC Sensors"]
        EC_IN["EC Sensors"]
        USER_IN["User Configuration<br>(Blueprints)"]
    end

    subgraph "Processing"
        AGG_PROC["Sensor Aggregation<br>(Avg, Min, Max)"]
        VALID_PROC["Sensor Validation<br>(Range Checks)"]
        DRYBACK_PROC["Dryback Detection<br>(Peak/Valley)"]
        PHASE_PROC["Phase Transition Logic"]
        IRR_PROC["Irrigation Control Logic"]
        ZONE_PROC["Zone Selection Logic"]
        DURATION_PROC["Shot Duration Calculation"]
    end

    subgraph "Intermediate Values"
        AGG_VWC["Aggregated VWC"]
        AGG_EC["Aggregated EC"]
        EC_RATIO["EC Ratio"]
        VWC_THRESHOLD["VWC Threshold"]
        DRYBACK_STATE["Dryback State"]
        SHOT_SIZE["Shot Size"]
        SHOT_DURATION["Shot Duration"]
    end

    subgraph "Outputs"
        PUMP_OUT["Pump Control"]
        ZONES_OUT["Zone Valve Control"]
        WASTE_OUT["Waste Valve Control"]
        VISUAL_OUT["Dashboard Visuals"]
        HISTORY_OUT["Dryback History"]
        NOTIFICATION_OUT["Notifications"]
    end

    VWC_IN-->VALID_PROC
    EC_IN-->VALID_PROC
    VALID_PROC-->AGG_PROC
    AGG_PROC-->AGG_VWC
    AGG_PROC-->AGG_EC
    AGG_VWC-->DRYBACK_PROC
    AGG_VWC-->PHASE_PROC
    AGG_VWC-->IRR_PROC
    AGG_VWC-->ZONE_PROC
    AGG_EC-->EC_RATIO
    USER_IN-->PHASE_PROC
    USER_IN-->IRR_PROC
    USER_IN-->ZONE_PROC
    USER_IN-->DURATION_PROC
    EC_RATIO-->VWC_THRESHOLD
    VWC_THRESHOLD-->IRR_PROC
    DRYBACK_PROC-->DRYBACK_STATE
    DRYBACK_STATE-->HISTORY_OUT
    DRYBACK_STATE-->VISUAL_OUT
    PHASE_PROC-->SHOT_SIZE
    SHOT_SIZE-->DURATION_PROC
    DURATION_PROC-->SHOT_DURATION
    SHOT_DURATION-->IRR_PROC
    ZONE_PROC-->ZONES_OUT
    IRR_PROC-->PUMP_OUT
    IRR_PROC-->WASTE_OUT
    IRR_PROC-->NOTIFICATION_OUT
    PHASE_PROC-->NOTIFICATION_OUT
```

## Logic Flow by Phase

### P0: Pre-Irrigation Dry Back

```mermaid
flowchart TD
    START[Lights Turn On] --> RESET[Reset Shot Counters<br>Reset Dryback State]
    RESET --> SET_P0[Set Phase to P0]
    SET_P0 --> MONITOR_VWC[Monitor VWC]

    MONITOR_VWC --> CHECK_MIN{Elapsed Time ≥<br>Min Wait Time?}
    CHECK_MIN -- No --> MONITOR_VWC
    CHECK_MIN -- Yes --> CHECK_TARGET{VWC ≤ Target<br>Dryback?}

    CHECK_TARGET -- Yes --> TRANSITION_P1[Transition to P1<br>Send Notification]

    CHECK_TARGET -- No --> CHECK_MAX{Elapsed Time ≥<br>Max Wait Time?}
    CHECK_MAX -- No --> MONITOR_VWC
    CHECK_MAX -- Yes --> TRANSITION_P1

    subgraph "Parameter Selection"
        PARAMS[Choose Parameters<br>Based on Mode]
        MODE_CHECK{Current Mode?}
        MODE_CHECK -- Vegetative --> VEG_PARAMS[Use Veg Parameters:<br>- p0_veg_dryback_target<br>- ec_target_veg_p0]
        MODE_CHECK -- Generative --> GEN_PARAMS[Use Gen Parameters:<br>- p0_gen_dryback_target<br>- ec_target_gen_p0]
        PARAMS --> MODE_CHECK
        VEG_PARAMS --> UPDATE_TARGETS[Update Dynamic Targets]
        GEN_PARAMS --> UPDATE_TARGETS
    end

    SET_P0 --> PARAMS
```

### P1: Ramp-Up Phase

```mermaid
flowchart TD
    START[Enter P1 Phase] --> INIT[Initialize Shot Count]
    INIT --> CALC_FIRST[Calculate Initial<br>Shot Size & Duration]
    CALC_FIRST --> CHECK_TIMING{Time for<br>Next Shot?}

    CHECK_TIMING -- No --> CHECK_TIMING
    CHECK_TIMING -- Yes --> CHECK_COUNT{Shot Count <br>Max Shots?}

    CHECK_COUNT -- No --> RUN_SHOT[Run Irrigation Shot]
    CHECK_COUNT -- Yes --> TRANSITION_P2[Transition to P2<br>Send Notification]

    RUN_SHOT --> PUMP_ON[Turn On Pump]
    PUMP_ON --> WAIT[Wait Calculated Duration]
    WAIT --> PUMP_OFF[Turn Off Pump]
    PUMP_OFF --> INCREMENT[Increment Shot Count]
    INCREMENT --> CALC_NEXT[Calculate Next<br>Shot Size & Duration]
    CALC_NEXT --> CHECK_TIMING

    RUN_SHOT --> MONITOR_VWC[Monitor VWC]
    MONITOR_VWC --> CHECK_VWC{VWC ≥ Target<br>& Min Shots Met?}
    CHECK_VWC -- Yes --> TRANSITION_P2
    CHECK_VWC -- No --> CHECK_EC{EC ≤ Flush Target<br>& VWC ≥ Target<br>& Min Shots Met?}
    CHECK_EC -- Yes --> TRANSITION_P2
    CHECK_EC -- No --> CONTINUE[Continue P1 Process]
    CONTINUE --> CHECK_TIMING

    subgraph "Shot Size Calculation"
        CALC[Calculate Current Shot Size]
        SIZE_FORMULA["Shot Size = Initial + (Increment × Shot Count)"]
        MAX_CHECK{Calculated Size > Max Size?}
        MAX_CHECK -- Yes --> USE_MAX[Use Maximum Shot Size]
        MAX_CHECK -- No --> USE_CALC[Use Calculated Shot Size]
        CALC --> SIZE_FORMULA
        SIZE_FORMULA --> MAX_CHECK
    end

    CALC_FIRST --> CALC
    CALC_NEXT --> CALC
```

### P2: Maintenance Phase

```mermaid
flowchart TD
    START[Enter P2 Phase] --> INIT[Initialize P2 Settings]
    INIT --> CALC_THRESHOLD[Calculate EC-Adjusted<br>VWC Threshold]
    CALC_THRESHOLD --> MONITOR_VWC[Monitor VWC]

    MONITOR_VWC --> CHECK_VWC{VWC < Adjusted<br>Threshold?}
    CHECK_VWC -- No --> P3_TIME_CHECK{Time to<br>Transition to P3?}
    P3_TIME_CHECK -- No --> MONITOR_VWC
    P3_TIME_CHECK -- Yes --> TRANSITION_P3[Transition to P3<br>Send Notification]

    CHECK_VWC -- Yes --> CHECK_MAX_EC{EC > Max Safe EC?}
    CHECK_MAX_EC -- Yes --> SKIP_HIGH_EC["Skip Irrigation\n(High EC Safety)"]
    SKIP_HIGH_EC --> MONITOR_VWC
    CHECK_MAX_EC -- No --> CHECK_PUMP{"Pump\nAlready On?"}
    CHECK_PUMP -- Yes --> MONITOR_VWC
    CHECK_PUMP -- No --> RUN_SHOT[Start Irrigation]

    RUN_SHOT --> PUMP_ON[Turn On Pump]
    PUMP_ON --> WAIT[Wait Calculated Duration]
    WAIT --> PUMP_OFF[Turn Off Pump]
    PUMP_OFF --> INCREMENT[Increment P2 Shot Count]
    INCREMENT --> MONITOR_VWC

    MONITOR_VWC --> CHECK_CAPACITY{VWC ≥ Field<br>Capacity?}
    CHECK_CAPACITY -- Yes --> STOP_EARLY[Stop Irrigation<br>Turn Off Pump]
    STOP_EARLY --> MONITOR_VWC

    subgraph "EC Adjustment Logic"
        CALC_ADJ[Calculate EC-Adjusted VWC Threshold]
        CHECK_RATIO{EC Ratio?}
        CHECK_RATIO -- > High Threshold --> HIGH_ADJ[Increase VWC Threshold<br>by High EC Adjustment]
        CHECK_RATIO -- < Low Threshold --> LOW_ADJ[Decrease VWC Threshold<br>by Low EC Adjustment]
        CHECK_RATIO -- Between Thresholds --> NO_ADJ[Use Base VWC Threshold]
        CALC_ADJ --> CHECK_RATIO
        HIGH_ADJ --> APPLY_STACKING
        LOW_ADJ --> APPLY_STACKING
        NO_ADJ --> APPLY_STACKING
        APPLY_STACKING{EC Stacking Active?}
        APPLY_STACKING -- Yes --> STACK_ADJ[Apply Stacking<br>VWC Reduction]
    APPLY_STACKING -- No --> FINAL_THRESHOLD["Final Adjusted Threshold"]
    STACK_ADJ --> FINAL_THRESHOLD
    end

    CALC_THRESHOLD --> CALC_ADJ

    subgraph "Zone-Specific Logic (Simplified for Diagram)"
        ZONE_CHECK["Check Each Zone's VWC"]
        ZONE_ACTIVE{"Any Active Zone\nBelow Threshold?"}
        ZONE_ACTIVE -- Yes --> SELECTED_ZONES["Update Active Zones\nfor Irrigation"]
        ZONE_ACTIVE -- No --> SKIP_IRR["Skip Irrigation"]
        ZONE_CHECK --> ZONE_ACTIVE
    end

    CHECK_VWC -- Yes --> ZONE_CHECK # Check zones if VWC is low enough
    SELECTED_ZONES --> CHECK_MAX_EC # If zones selected, proceed
```

### P3: Overnight Dry Back

```mermaid
flowchart TD
    START[Enter P3 Phase] --> INIT[Initialize P3 Settings]
    INIT --> MONITOR_VWC[Monitor Minimum VWC]

    MONITOR_VWC --> CHECK_VWC{Min VWC < Emergency<br>Threshold?}
    CHECK_VWC -- No --> LIGHTS_ON_CHECK{Lights On Time<br>Reached?}
    LIGHTS_ON_CHECK -- No --> MONITOR_VWC
    LIGHTS_ON_CHECK -- Yes --> TRANSITION_P0[Transition to P0<br>New Day Cycle]

    CHECK_VWC -- Yes --> CHECK_PUMP{"Pump\nAlready On?"}
    CHECK_PUMP -- Yes --> MONITOR_VWC
    CHECK_PUMP -- No --> RUN_EMERGENCY["Run Emergency Irrigation"]

    RUN_EMERGENCY --> PUMP_ON[Turn On Pump]
    PUMP_ON --> WAIT[Wait Emergency<br>Shot Duration]
    WAIT --> PUMP_OFF[Turn Off Pump]
    PUMP_OFF --> INCREMENT[Increment P3 Shot Count]
    INCREMENT --> NOTIFY[Send Emergency<br>Irrigation Notification]
    NOTIFY --> MONITOR_VWC

    subgraph "P3 Start Time Calculation"
        CALC_START[Calculate P3 Start Time]
        MODE_CHECK{Current Mode?}
        MODE_CHECK -- Vegetative --> VEG_TIME[Lights Off Time -<br>p3_veg_last_irrigation]
        MODE_CHECK -- Generative --> GEN_TIME[Lights Off Time -<br>p3_gen_last_irrigation]
        CALC_START --> MODE_CHECK
    end

    subgraph "Zone-Specific Logic (Simplified for Diagram)"
        ZONE_CHECK_EM["Check Each Zone's VWC"]
        ZONE_ACTIVE_EM{"Any Active Zone\nBelow Emergency\nThreshold?"}
        ZONE_ACTIVE_EM -- Yes --> SELECTED_ZONES_EM["Update Active Zones\nfor Emergency Irrigation"]
        ZONE_ACTIVE_EM -- No --> SKIP_IRR_EM["Skip Irrigation"]
        ZONE_CHECK_EM --> ZONE_ACTIVE_EM
    end

    CHECK_VWC -- Yes --> ZONE_CHECK_EM # Check zones if VWC is low enough
    SELECTED_ZONES_EM --> RUN_EMERGENCY # If zones selected, proceed
```

## Zone Control Logic

```mermaid
graph TD
    START[Zone Control System] --> CONFIG[Configure Zone Sensors Through Blueprint]
    CONFIG --> ZONE_ENABLE[Set Zone Enable Status Using Input Booleans]
    ZONE_ENABLE --> MONITOR[Monitor Zone-Specific VWC and EC]

    MONITOR --> ZONE_AGGREGATION[Calculate Per-Zone VWC and EC Averages]
    ZONE_AGGREGATION --> COMPARE[Compare Each Zone's VWC to Phase-Specific Threshold]

    COMPARE --> DECISION{Any Zone Needs Irrigation?}
    DECISION -- No --> MONITOR
    DECISION -- Yes --> SELECT[Select Which Zones Need Irrigation]

    SELECT --> UPDATE_SELECTOR[Update Active Zones Selector]
    UPDATE_SELECTOR --> PUMP_ON[Turn On Main Pump]
    PUMP_ON --> OPEN_VALVES[Open Valves for Selected Zones Only]
    OPEN_VALVES --> WAIT[Wait for Shot Duration]
    WAIT --> CLOSE_VALVES[Close All Zone Valves]
    CLOSE_VALVES --> PUMP_OFF[Turn Off Main Pump]
    PUMP_OFF --> MONITOR

    subgraph "Zone Selection Options"
        OPTIONS[Zone Selection Options]
        OPT1[All Zones]
        OPT2[Zone 1 Only]
        OPT3[Zone 2 Only]
        OPT4[Zone 3 Only]
        OPT5[Zones 1-2]
        OPT6[Zones 1-3]
        OPT7[Zones 2-3]
        OPT8[No Zones]
        OPTIONS-->OPT1
        OPTIONS-->OPT2
        OPTIONS-->OPT3
        OPTIONS-->OPT4
        OPTIONS-->OPT5
        OPTIONS-->OPT6
        OPTIONS-->OPT7
        OPTIONS-->OPT8
    end

    UPDATE_SELECTOR-->OPTIONS
```

## EC Adjustment Logic

```mermaid
graph TD
    START[EC Adjustment System] --> CURRENT_EC[Get Current Avg EC]
    CURRENT_EC --> TARGET_EC[Determine Target EC Based on Phase and Mode]

    TARGET_EC --> CALC_RATIO[Calculate EC Ratio Current/Target]
    CALC_RATIO --> RATIO_CHECK{EC Ratio Value?}

    RATIO_CHECK -- ">High Threshold" --> HIGH_EC[Use High EC Adjustment Value]
    RATIO_CHECK -- "<Low Threshold" --> LOW_EC[Use Low EC Adjustment Value]
    RATIO_CHECK -- "Between Thresholds" --> NORMAL_EC[Use No EC Adjustment]

    HIGH_EC --> ADJUST_THRESHOLD
    LOW_EC --> ADJUST_THRESHOLD
    NORMAL_EC --> ADJUST_THRESHOLD
    ADJUST_THRESHOLD[Adjust VWC Threshold] --> USE_ADJUSTED[Use Adjusted Threshold for Irrigation Decisions]

    subgraph "EC Ratio Effects"
        EFFECTS[EC Ratio Effects]
        HIGH_EFFECT[High EC Ratio: More frequent irrigation]
        NORMAL_EFFECT[Normal EC Ratio: Normal frequency]
        LOW_EFFECT[Low EC Ratio: Less frequent irrigation]

        EFFECTS-->HIGH_EFFECT
        EFFECTS-->NORMAL_EFFECT
        EFFECTS-->LOW_EFFECT
    end

    subgraph "Target EC Selection"
        SELECT[EC Target Selection]
        PHASE{Current Phase}
        MODE{Current Mode}

        PHASE-->P0[P0]
        PHASE-->P1[P1]
        PHASE-->P2[P2]
        PHASE-->P3[P3]

        P0-->MODE
        P1-->MODE
        P2-->MODE
        P3-->MODE

        MODE -- "Vegetative" --> VEG_TARGETS[Vegetative EC Targets]
        MODE -- "Generative" --> GEN_TARGETS[Generative EC Targets]
    end

    TARGET_EC --> SELECT
```

## Dryback Detection System

```mermaid
graph TD
    START[Dryback Detection System] --> COLLECT[Collect VWC Readings]
    COLLECT --> HISTORY[Maintain Short History of VWC Values]

    HISTORY --> TREND_CHECK{VWC Trend?}
    TREND_CHECK -- Decreasing --> POTENTIAL_PEAK[Identify Potential Peak VWC]
    TREND_CHECK -- Increasing --> POTENTIAL_VALLEY[Identify Potential Valley VWC]
    TREND_CHECK -- Stable --> CONTINUE[Continue Monitoring]

    POTENTIAL_PEAK --> THRESHOLD_CHECK_P{Decrease > Peak Detection Threshold?}
    THRESHOLD_CHECK_P -- No --> CONTINUE
    THRESHOLD_CHECK_P -- Yes --> RECORD_PEAK[Record Peak VWC and Timestamp]
    RECORD_PEAK --> SET_IN_PROGRESS[Set Dryback In Progress = True]

    POTENTIAL_VALLEY --> IN_PROGRESS{Dryback In Progress?}
    IN_PROGRESS -- No --> CONTINUE
    IN_PROGRESS -- Yes --> THRESHOLD_CHECK_V{Increase > Valley Detection Threshold?}

    THRESHOLD_CHECK_V -- No --> CONTINUE
    THRESHOLD_CHECK_V -- Yes --> RECORD_VALLEY[Record Valley VWC and Timestamp]
    RECORD_VALLEY --> CALC_DURATION[Calculate Dryback Duration]
    CALC_DURATION --> CALC_PERCENTAGE[Calculate Dryback Percentage]

    CALC_PERCENTAGE --> MIN_CHECK{Meets Minimum Duration & Percentage?}
    MIN_CHECK -- No --> RESET[Reset Dryback In Progress = False]
    MIN_CHECK -- Yes --> LOG_DRYBACK[Log Completed Dryback to History]
    LOG_DRYBACK --> RESET

    RESET --> CONTINUE

    subgraph "Real-time Dryback Calculations"
        REAL_TIME[Real-time During Dryback]
        RT_PERC[Calculate Current Dryback Percentage]
        RT_DUR[Calculate Current Dryback Duration]
        REAL_TIME --> RT_PERC
        REAL_TIME --> RT_DUR
    end

    SET_IN_PROGRESS --> REAL_TIME
```

## Configuration Blueprint System

```mermaid
graph TD
    START[Configure Crop Steering] --> ENTITY_BP[Entity Setup Blueprint]
    START --> PARAM_BP[Parameters Blueprint]

    ENTITY_BP --> SENSOR_CONFIG[Configure VWC & EC Sensors]
    ENTITY_BP --> SWITCH_CONFIG[Configure Pump & Zone Valves]
    ENTITY_BP --> ZONE_CONFIG[Configure Zone-Specific Sensors]

    SENSOR_CONFIG --> UPDATE_HELPERS[Update Input Text Helpers with Entity Configuration]
    SWITCH_CONFIG --> UPDATE_HELPERS
    ZONE_CONFIG --> UPDATE_HELPERS

    PARAM_BP --> SUBSTRATE_PARAMS[Set Substrate Parameters]
    PARAM_BP --> PHASE_PARAMS[Set Phase-Specific Parameters]
    PARAM_BP --> EC_PARAMS[Set EC Target Parameters]
    PARAM_BP --> TIMING_PARAMS[Set Timing Parameters]
    PARAM_BP --> VALIDATION_PARAMS[Set Sensor Validation Parameters]

    SUBSTRATE_PARAMS --> UPDATE_NUMBERS[Update Input Number Helpers with Parameter Values]
    PHASE_PARAMS --> UPDATE_NUMBERS
    EC_PARAMS --> UPDATE_NUMBERS
    TIMING_PARAMS --> UPDATE_NUMBERS
    VALIDATION_PARAMS --> UPDATE_NUMBERS

    UPDATE_HELPERS --> RELOAD_CONFIG[Reload Configuration for Processing Layer]
    UPDATE_NUMBERS --> RELOAD_CONFIG

    RELOAD_CONFIG --> YAML_UPDATE[Update YAML Template Calculations]
    RELOAD_CONFIG --> APPDAEMON_UPDATE[Update AppDaemon Calculations]

    YAML_UPDATE --> SYSTEM_READY[Crop Steering System Ready for Operation]
    APPDAEMON_UPDATE --> SYSTEM_READY
```

## EC Stacking Automation

This feature allows for the deliberate accumulation of EC in the substrate during specific phases, typically early flower, to promote generative growth.

### How it Works (AppDaemon Implementation)

1.  **Enable Feature**: Toggle `input_boolean.cs_ec_stacking_enabled` to `on`.
2.  **Configure Active Phases**: Set `input_text.cs_ec_stacking_active_phases` to a comma-separated list of phases where stacking should occur (e.g., "P1,P2" or just "P2").
3.  **Set Target Ratio**: Define the desired EC ratio (Substrate EC / Target EC) using `input_number.cs_ec_stacking_target_ratio`. A value of 1.5 means you want the substrate EC to be 50% higher than the normal target for that phase.
4.  **Set VWC Reduction**: Configure `input_number.cs_ec_stacking_vwc_reduction`. This value (in %) reduces the VWC threshold that triggers irrigation during P2.

### Logic

- When EC Stacking is enabled AND the current phase is one of the active phases AND the current EC Ratio is *below* the target stacking ratio:
    - The AppDaemon script will subtract the `cs_ec_stacking_vwc_reduction` value from the calculated P2 VWC irrigation threshold.
    - This makes the system wait for the substrate to dry out slightly more before triggering irrigation, allowing EC to accumulate or "stack".
- **Safety Override**: Irrigation is always skipped if the average substrate EC exceeds the `cs_substrate_max_ec` value, regardless of stacking settings.

```mermaid
graph TD
    START[Check P2 Irrigation Trigger] --> STACK_ENABLED{EC Stacking Enabled?}
    STACK_ENABLED -- No --> EC_ADJUST[Use Standard EC-Adjusted Threshold]
    STACK_ENABLED -- Yes --> PHASE_ACTIVE{Current Phase in Active List?}
    PHASE_ACTIVE -- No --> EC_ADJUST
    PHASE_ACTIVE -- Yes --> RATIO_CHECK{Current EC Ratio < Stacking Target Ratio?}
    RATIO_CHECK -- No --> EC_ADJUST
    RATIO_CHECK -- Yes --> APPLY_REDUCTION["Reduce VWC Threshold\nby Stacking Reduction %"]
    APPLY_REDUCTION --> SAFETY_CHECK{"Final Threshold >\nCritical VWC?"}
    SAFETY_CHECK -- No --> USE_CRITICAL["Use Critical VWC\nas Threshold"]
    SAFETY_CHECK -- Yes --> USE_STACK_ADJUSTED["Use Stacking-Adjusted\nThreshold"]
    EC_ADJUST --> COMPARE_VWC["Compare Avg VWC\nto Threshold"]
    USE_CRITICAL --> COMPARE_VWC
    USE_STACK_ADJUSTED --> COMPARE_VWC
    COMPARE_VWC --> DECIDE{"VWC < Threshold?"}
    DECIDE -- Yes --> CHECK_MAX_EC_STACK{"EC < Max Safe EC?"}
    DECIDE -- No --> WAIT["Wait"]
    CHECK_MAX_EC_STACK -- Yes --> TRIGGER_IRR["Trigger P2 Irrigation"]
    CHECK_MAX_EC_STACK -- No --> SKIP_IRR_STACK["Skip Irrigation\n(High EC)"]
```

## Dashboard Integration

```mermaid
flowchart TD
    START[Dashboard Components] --> CARDS[Select Dashboard Card Type]

    CARDS --> SIMPLE[Simple Status Card]
    CARDS --> IMPROVED[Improved Control Card]
    CARDS --> PLOTLY[Advanced Plotly Card]

    SIMPLE --> SHOW_SIMPLE[Display Current Phase<br>Basic Status & Controls]
    IMPROVED --> SHOW_IMPROVED[Display Phase Info<br>VWC/EC Levels<br>Zone Controls]
    PLOTLY --> SHOW_PLOTLY[Display Interactive Graphs<br>Historical Data<br>Dryback Analysis]

    SHOW_SIMPLE & SHOW_IMPROVED & SHOW_PLOTLY --> ADD_TO_DASHBOARD[Add Cards to Dashboard]

    ADD_TO_DASHBOARD --> LAYOUT[Arrange Dashboard Layout]
    LAYOUT --> MULTI_CARD[Multi-Card Dashboard<br>with Tabs for Different Views]

    MULTI_CARD --> VIEW_DATA[View Real-Time<br>Crop Steering Data]
    VIEW_DATA --> INTERACT[Interact with System<br>Update Settings<br>Control Zones]
```

## Complete Entity Relationship Map

This diagram shows how all entities in the system relate to each other, focusing on the most important connections.

```mermaid
flowchart TB
    classDef input fill:#f9f,stroke:#333,stroke-width:2px
    classDef helper fill:#bbf,stroke:#333,stroke-width:2px
    classDef sensor fill:#bfb,stroke:#333,stroke-width:2px
    classDef switch fill:#ff9,stroke:#333,stroke-width:2px
    classDef automation fill:#f90,stroke:#333,stroke-width:2px

    %% Input Entities (Physical Sensors)
    InputVWC["Raw VWC Sensors"]:::input
    InputEC["Raw EC Sensors"]:::input
    InputZoneVWC["Zone VWC Sensors"]:::input
    InputZoneEC["Zone EC Sensors"]:::input

    %% Helper Entities (User Configuration & State)
    PhaseSelect["input_select.cs_crop_steering_phase"]:::helper
    ModeSelect["input_select.cs_steering_mode"]:::helper
    ZonesSelect["input_select.active_irrigation_zones"]:::helper
    P1ShotCount["input_number.cs_p1_shot_count"]:::helper
    P2ShotCount["input_number.cs_p2_shot_count"]:::helper
    P3ShotCount["input_number.cs_p3_shot_count"]:::helper
    ZoneEnabledBooleans["Zone Enable\nInput Booleans"]:::helper
    ECStackingEnabled["input_boolean.cs_ec_stacking_enabled"]:::helper
    ECStackingParams["EC Stacking Parameters\n(input_number, input_text)"]:::helper
    ConfigHelpers["Config Helpers\n(input_text storing blueprint selections)"]:::helper
    ParamHelpers["Parameter Helpers\n(input_numbers storing blueprint selections)"]:::helper

    %% Sensor Entities (Calculated/Template)
    AvgVWC["sensor.cs_configured_avg_vwc"]:::sensor
    AvgEC["sensor.cs_configured_avg_ec"]:::sensor
    MinVWC["sensor.cs_configured_min_vwc"]:::sensor
    MaxVWC["sensor.cs_configured_max_vwc"]:::sensor
    ECRatio["sensor.cs_ec_ratio"]:::sensor
    AdjustedThreshold["sensor.cs_p2_vwc_threshold_ec_adjusted"]:::sensor
    ZoneVWCSensors["Zone VWC Sensors (Template)"]:::sensor
    ZoneECSensors["Zone EC Sensors (Template)"]:::sensor
    ShotDurations["Shot Duration Sensors"]:::sensor
    DrybackSensors["Dryback Status Sensors"]:::sensor

    %% Switch Entities (Actuators)
    PumpSwitch["switch.cs_configured_pump_switch"]:::switch
    ZoneValves["Zone Valve Switches (Template)"]:::switch
    WasteValve["Waste Valve Switch (Template)"]:::switch

    %% Automations (Logic Controllers)
    PhaseTransition["Phase Transition Automations"]:::automation
    IrrigationControl["Irrigation Control Automations"]:::automation
    ZoneControl["Zone Control Automations"]:::automation
    DrybackDetection["Dryback Detection Logic"]:::automation
    BlueprintEntity["Entity Setup Blueprint Automation"]:::automation
    BlueprintParam["Parameter Setup Blueprint Automation"]:::automation

    %% Connections
    BlueprintEntity --> ConfigHelpers
    BlueprintParam --> ParamHelpers

    ConfigHelpers --> AvgVWC
    ConfigHelpers --> AvgEC
    ConfigHelpers --> MinVWC
    ConfigHelpers --> MaxVWC
    ConfigHelpers --> PumpSwitch
    ConfigHelpers --> ZoneValves
    ConfigHelpers --> WasteValve
    ConfigHelpers --> ZoneVWCSensors
    ConfigHelpers --> ZoneECSensors

    ParamHelpers --> PhaseTransition
    ParamHelpers --> IrrigationControl
    ParamHelpers --> ZoneControl
    ParamHelpers --> DrybackDetection
    ParamHelpers --> AdjustedThreshold
    ParamHelpers --> ShotDurations

    InputVWC --> ConfigHelpers
    InputEC --> ConfigHelpers
    InputZoneVWC --> ConfigHelpers
    InputZoneEC --> ConfigHelpers

    AvgVWC --> PhaseTransition
    AvgVWC --> IrrigationControl
    AvgVWC --> DrybackDetection
    AvgEC --> ECRatio
    MinVWC --> IrrigationControl
    ECRatio --> AdjustedThreshold
    AdjustedThreshold --> IrrigationControl
    ZoneVWCSensors --> ZoneControl
    ShotDurations --> IrrigationControl

    PhaseSelect --> PhaseTransition
    PhaseSelect --> IrrigationControl
    ModeSelect --> PhaseTransition
    ZonesSelect --> ZoneControl
    P1ShotCount --> IrrigationControl
    P2ShotCount --> IrrigationControl
    P3ShotCount --> IrrigationControl
    ZoneEnabledBooleans --> ZoneControl
    ECStackingEnabled --> IrrigationControl
    ECStackingParams --> IrrigationControl

    PhaseTransition --> PhaseSelect
    IrrigationControl --> PumpSwitch
    ZoneControl --> ZoneValves
    IrrigationControl --> WasteValve
    DrybackDetection --> DrybackSensors
    ZoneControl --> ZonesSelect
```

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Irrigation Not Triggering

```mermaid
flowchart TD
    START[Irrigation Not Triggering] --> CHECK_PHASE{Current Phase?}

    CHECK_PHASE -- P0 --> P0_NORMAL["P0 doesn't trigger irrigation<br>This is normal"]

    CHECK_PHASE -- P1 --> P1_INTERVAL{Check P1<br>Time Interval}
    P1_INTERVAL -- "Not time yet" --> P1_WAIT["Wait for next interval<br>(p1_time_between_shots)"]
    P1_INTERVAL -- "Time OK" --> P1_COUNT{Check P1<br>Shot Count}
    P1_COUNT -- "≥ Max Shots" --> P1_MAX["P1 shots complete.<br>Check why not in P2"]
    P1_COUNT -- "< Max Shots" --> P1_CHECK_SENSORS["Check VWC Sensors"]

    CHECK_PHASE -- P2 --> CHECK_MAX_EC{EC > Max Safe EC?}
    CHECK_MAX_EC -- Yes --> SKIP_HIGH_EC["Irrigation Skipped<br>(High EC Safety)"]
    CHECK_MAX_EC -- No --> CHECK_VWC{Is VWC < Threshold?}
    CHECK_VWC -- No --> CHECK_ZONES["Check Individual Zone VWC"]
    CHECK_VWC -- Yes --> CHECK_PUMP{Is Pump<br>Already Running?}
    CHECK_PUMP -- Yes --> WAIT_PUMP["Wait for current<br>shot to complete"]
    CHECK_PUMP -- No --> CHECK_ENTITIES["Check Entity Configuration"]

    CHECK_PHASE -- P3 --> CHECK_EMERGENCY{Is Min VWC < Emergency<br>Threshold?}
    CHECK_EMERGENCY -- No --> P3_NORMAL["No emergency irrigation needed.<br>This is normal for P3"]
    CHECK_EMERGENCY -- Yes --> CHECK_ENTITIES

    CHECK_ENTITIES --> ENTITY_LIST["Check Entity Configuration:<br>1. Blueprint configuration<br>2. Helper entity values<br>3. Entity availability/state<br>4. Pump & valve states<br>5. Shot duration calculation"]
```

#### 2. Phase Not Progressing

```mermaid
flowchart TD
    START[Phase Not Progressing] --> CHECK_PHASE{Stuck in<br>Which Phase?}

    CHECK_PHASE -- P0 --> CHECK_P0_TIME{Minimum<br>Wait Time<br>Elapsed?}
    CHECK_P0_TIME -- No --> WAIT_MIN["Wait for minimum time<br>(p0_min_wait_time)"]
    CHECK_P0_TIME -- Yes --> CHECK_P0_VWC{VWC ≤<br>Target?}
    CHECK_P0_VWC -- No --> CHECK_P0_MAX{Maximum<br>Wait Time<br>Elapsed?}
    CHECK_P0_MAX -- No --> WAIT_MAX["Wait for maximum time<br>(p0_max_wait_time)"]
    CHECK_P0_MAX -- Yes --> P0_ISSUE["Check P0->P1 Automation:<br>1. Sensor availability<br>2. Correct dynamic dryback target<br>3. Max wait time setting"]
    CHECK_P0_VWC -- Yes --> P0_ISSUE

    CHECK_PHASE -- P1 --> CHECK_P1_SHOTS{Maximum<br>Shots<br>Reached?}
    CHECK_P1_SHOTS -- No --> CHECK_P1_VWC{VWC ≥<br>Target?}
    CHECK_P1_VWC -- No --> CHECK_P1_EC{EC ≤ Flush Target<br>& VWC ≥ Target<br>& Min Shots Met?}
    CHECK_P1_EC -- No --> CONTINUE_P1["Continue P1 shots<br>This is normal"]
    CHECK_P1_EC -- Yes --> P1_ISSUE["Check P1->P2 Automation:<br>1. Shot count accuracy<br>2. VWC/EC sensor readings<br>3. Target VWC/EC settings"]
    CHECK_P1_VWC -- Yes --> CHECK_P1_MIN{Minimum<br>Shots<br>Reached?}
    CHECK_P1_MIN -- No --> CONTINUE_P1
    CHECK_P1_MIN -- Yes --> P1_ISSUE
    CHECK_P1_SHOTS -- Yes --> P1_ISSUE

    CHECK_PHASE -- P2 --> CHECK_P3_TIME{P3 Start<br>Time<br>Reached?}
    CHECK_P3_TIME -- No --> CONTINUE_P2["Continue P2 maintenance<br>This is normal"]
    CHECK_P3_TIME -- Yes --> P2_ISSUE["Check P2->P3 Automation:<br>1. P3 start time calculation<br>2. Time-based trigger<br>3. Manual phase override"]

    CHECK_PHASE -- P3 --> CHECK_LIGHTS{Lights<br>On Time<br>Reached?}
    CHECK_LIGHTS -- No --> CONTINUE_P3["Continue P3 dryback<br>This is normal"]
    CHECK_LIGHTS -- Yes --> P3_ISSUE["Check P3->P0 Automation:<br>1. Lights on time setting<br>2. Daily trigger<br>3. Manual phase override"]
```

#### 3. Dryback Detection Issues

```mermaid
flowchart TD
    START[Dryback Detection Issues] --> CHECK_DISPLAY{What's Displayed?}

    CHECK_DISPLAY -- "No drybacks<br>detected" --> CHECK_DATA{Is VWC<br>data valid?}
    CHECK_DATA -- No --> SENSOR_ISSUES["Fix VWC Sensors:<br>1. Check availability<br>2. Validate readings<br>3. Ensure proper aggregation"]
    CHECK_DATA -- Yes --> CHECK_THRESHOLDS{Detection<br>thresholds<br>too high?}
    CHECK_THRESHOLDS -- Yes --> LOWER_THRESHOLDS["Lower Detection Thresholds:<br>1. Decrease peak threshold<br>2. Decrease valley threshold"]
    CHECK_THRESHOLDS -- No --> CHECK_SETTINGS["Check Dryback Settings:<br>1. Minimum duration<br>2. Minimum percentage<br>3. VWC history logging"]

    CHECK_DISPLAY -- "False<br>peaks/valleys" --> CHECK_NOISE{Sensor<br>noise<br>issues?}
    CHECK_NOISE -- Yes --> REDUCE_NOISE["Reduce Sensor Noise:<br>1. Filter sensors<br>2. Use averaging<br>3. Increase thresholds"]
    CHECK_NOISE -- No --> CHECK_THRESHOLDS_LOW{Detection<br>thresholds<br>too low?}
    CHECK_THRESHOLDS_LOW -- Yes --> INCREASE_THRESHOLDS["Increase Detection Thresholds:<br>1. Increase peak threshold<br>2. Increase valley threshold"]
    CHECK_THRESHOLDS_LOW -- No --> CHECK_IRRIGATION{Irrigation<br>pattern<br>issues?}
    CHECK_IRRIGATION -- Yes --> ADJUST_IRRIGATION["Adjust Irrigation Pattern:<br>1. Less frequent shots<br>2. More drying time<br>3. Different shot sizes"]

    CHECK_DISPLAY -- "Missing<br>dryback logs" --> CHECK_MINS{Meet min<br>duration &<br>percentage?}
    CHECK_MINS -- No --> ADJUST_MINS["Adjust Minimum Requirements:<br>1. Decrease min duration<br>2. Decrease min percentage"]
    CHECK_MINS -- Yes --> CHECK_LOGGING["Check Logging System:<br>1. Helper entity configuration<br>2. JSON format issues<br>3. Character limits<br>4. Storage capacity"]
```

### Parameter Troubleshooting Table

| Parameter Type | Common Issues | Potential Solutions |
|----------------|--------------|---------------------|
| VWC Settings | • Thresholds too high/low<br>• Substrate params incorrect | • Calibrate to substrate<br>• Test with different values |
| EC Settings | • Targets not matching nutrient solution<br>• Ratio thresholds too tight/loose | • Match EC target to nutrient soln<br>• Adjust ratio thresholds for sensitivity |
| Shot Sizes | • Too large/small<br>• Increment too aggressive | • Base on substrate volume<br>• Start small and increase conservatively |
| Timing | • Lights schedule incorrect<br>• P3 transition too early/late | • Verify actual light timing<br>• Adjust P3 timing offsets |
| Duration | • Shot duration too short/long<br>• Flow rate incorrect | • Verify actual flow rate<br>• Adjust substrate volume value |
| EC Stacking | • Stacking not activating<br>• Stacking too aggressive | • Check enable toggle & active phases<br>• Verify EC ratio < target ratio<br>• Adjust target ratio or VWC reduction |

## Final Implementation Notes

1. **Start Simple**: Begin with conservative parameters and a single zone before expanding.

2. **Calibration Period**: Allow 3-7 days for full calibration of parameters to your specific environment.

3. **Monitoring Priority**: Focus on:
   - Average VWC trend over time
   - EC stability and ratio
   - Dryback percentage achieved
   - Shot timing and frequency

4. **Season Adjustments**: Be prepared to adjust parameters as:
   - Plants mature
   - Environmental conditions change
   - Growth objectives shift

5. **Safety Mechanisms**: The system includes several safety features:
   - Sensor validation filters
   - Field capacity cutoff
   - P3 emergency irrigation
   - Zone-specific monitoring
   - Max EC irrigation cutoff

6. **Data Analysis**: Use the plotly graphs to analyze:
   - VWC curves
   - EC trends
   - Irrigation timing
   - Dryback patterns

7. **Documentation**: Keep records of:
   - Parameter changes
   - Growth responses
   - Unusual events
   - Seasonal adjustments

For additional support, refer to the installation guide and system analysis documents.
