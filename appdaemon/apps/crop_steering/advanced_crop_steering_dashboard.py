"""
Advanced Crop Steering Dashboard for AppDaemon
Athena-style real-time graphs and comprehensive system monitoring
Integrates all advanced modules: dryback detection, sensor fusion, ML prediction, crop profiles
"""

import appdaemon.plugins.hass.hassapi as hass
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

# Import our advanced modules
from .advanced_dryback_detection import AdvancedDrybackDetector
from .intelligent_sensor_fusion import IntelligentSensorFusion
from .ml_irrigation_predictor import SimplifiedIrrigationPredictor, MLIrrigationPredictor
from .intelligent_crop_profiles import IntelligentCropProfiles

_LOGGER = logging.getLogger(__name__)


class AdvancedCropSteeringDashboard(hass.Hass):
    """
    Advanced crop steering dashboard with Athena-style real-time monitoring.
    
    Features:
    - Real-time VWC/EC trending graphs (Athena style)
    - Dryback detection visualization with peak/valley markers
    - ML irrigation predictions and recommendations
    - Sensor fusion health monitoring
    - Crop profile performance tracking
    - Environmental correlation analysis
    - Phase transition timeline
    - Water efficiency analytics
    """

    def initialize(self):
        """Initialize the advanced dashboard system."""
        
        # Configuration
        self.sensor_entities = self._load_sensor_config()
        self.update_interval = 30  # Update every 30 seconds
        self.graph_history_hours = 24  # 24 hours of data
        self.max_data_points = 2880  # 24h * 60min / 0.5min = 2880 points
        
        # Initialize advanced modules
        self.dryback_detector = AdvancedDrybackDetector(
            window_size=200,
            min_peak_distance=10,
            noise_threshold=0.5
        )
        
        self.sensor_fusion = IntelligentSensorFusion(
            outlier_multiplier=1.5,
            min_sensors_required=2,
            history_window=500
        )
        
        self.ml_predictor = MLIrrigationPredictor(
            history_window=1000,
            prediction_horizon=120,
            update_frequency=50
        )
        
        self.crop_profiles = IntelligentCropProfiles()
        
        # Data storage for dashboard
        self.dashboard_data = {
            'vwc_history': [],
            'ec_history': [],
            'dryback_history': [],
            'phase_history': [],
            'irrigation_events': [],
            'ml_predictions': [],
            'sensor_health': {},
            'performance_metrics': {}
        }
        
        # Dashboard configuration
        self.dashboard_config = {
            'title': 'Advanced Crop Steering - Athena Style',
            'theme': 'plotly_dark',
            'colors': {
                'primary': '#00cc96',
                'secondary': '#ff6692', 
                'accent': '#ffa15a',
                'background': '#2f3136',
                'grid': '#4a4a4a'
            }
        }
        
        # Set up listeners and timers
        self._setup_listeners()
        self._setup_timers()
        
        # Initialize crop profile
        self._initialize_crop_profile()
        
        self.log("🚀 Advanced Crop Steering Dashboard initialized!")

    def _load_sensor_config(self) -> Dict:
        """Load sensor configuration from environment."""
        return {
            'vwc_sensors': [
                'sensor.vwc_r1_front', 'sensor.vwc_r1_back',
                'sensor.vwc_r2_front', 'sensor.vwc_r2_back',
                'sensor.vwc_r3_front', 'sensor.vwc_r3_back'
            ],
            'ec_sensors': [
                'sensor.ec_r1_front', 'sensor.ec_r1_back',
                'sensor.ec_r2_front', 'sensor.ec_r2_back',
                'sensor.ec_r3_front', 'sensor.ec_r3_back'
            ],
            'environmental': {
                'temperature': 'sensor.grow_room_temperature',
                'humidity': 'sensor.grow_room_humidity',
                'vpd': 'sensor.grow_room_vpd'
            },
            'system': {
                'current_phase': 'select.crop_steering_irrigation_phase',
                'steering_mode': 'select.crop_steering_steering_mode',
                'system_enabled': 'switch.crop_steering_system_enabled'
            }
        }

    def _setup_listeners(self):
        """Set up Home Assistant entity listeners."""
        
        # Listen to all VWC sensors
        for sensor in self.sensor_entities['vwc_sensors']:
            self.listen_state(self._on_vwc_update, sensor)
        
        # Listen to all EC sensors
        for sensor in self.sensor_entities['ec_sensors']:
            self.listen_state(self._on_ec_update, sensor)
        
        # Listen to system state changes
        for sensor in self.sensor_entities['system'].values():
            self.listen_state(self._on_system_update, sensor)
        
        # Listen to irrigation events
        self.listen_event(self._on_irrigation_event, 'crop_steering_irrigation_shot')
        self.listen_event(self._on_phase_transition, 'crop_steering_phase_transition')

    def _setup_timers(self):
        """Set up periodic update timers."""
        
        # Main dashboard update
        self.run_every(self._update_dashboard, 'now', self.update_interval)
        
        # ML model training and prediction updates
        self.run_every(self._update_ml_predictions, 'now+5', 60)  # Every minute
        
        # Sensor health monitoring
        self.run_every(self._monitor_sensor_health, 'now+10', 120)  # Every 2 minutes
        
        # Performance analytics
        self.run_every(self._update_performance_metrics, 'now+15', 300)  # Every 5 minutes

    def _initialize_crop_profile(self):
        """Initialize crop profile based on current configuration."""
        
        # Try to get current crop type from HA
        crop_type_entity = 'select.crop_steering_crop_type'
        current_crop = self.get_state(crop_type_entity, default='Cannabis_Athena')
        
        # Select profile
        profile_result = self.crop_profiles.select_profile(current_crop, 'vegetative')
        
        if profile_result['status'] == 'success':
            self.log(f"✅ Initialized crop profile: {current_crop}")
        else:
            self.log(f"⚠️ Failed to initialize crop profile: {profile_result.get('message', 'Unknown error')}")

    async def _on_vwc_update(self, entity, attribute, old, new, kwargs):
        """Handle VWC sensor updates."""
        try:
            if new == 'unavailable' or new == 'unknown':
                return
            
            vwc_value = float(new)
            timestamp = datetime.now()
            
            # Add to sensor fusion
            fusion_result = self.sensor_fusion.add_sensor_reading(
                entity, vwc_value, timestamp, 'vwc'
            )
            
            # Add to dryback detector (using fused value if available)
            if fusion_result['fused_value'] is not None:
                dryback_result = self.dryback_detector.add_vwc_reading(
                    fusion_result['fused_value'], timestamp
                )
                
                # Store dryback data
                self.dashboard_data['dryback_history'].append({
                    'timestamp': timestamp.isoformat(),
                    'dryback_percentage': dryback_result['dryback_percentage'],
                    'dryback_in_progress': dryback_result['dryback_in_progress'],
                    'confidence': dryback_result['confidence_score']
                })
            
            # Update dashboard VWC history
            self.dashboard_data['vwc_history'].append({
                'timestamp': timestamp.isoformat(),
                'sensor_id': entity,
                'raw_value': vwc_value,
                'fused_value': fusion_result['fused_value'],
                'is_outlier': fusion_result['is_outlier'],
                'fusion_confidence': fusion_result['fusion_confidence']
            })
            
            # Trim history to max points
            self._trim_history('vwc_history')
            self._trim_history('dryback_history')
            
        except Exception as e:
            self.log(f"❌ Error processing VWC update: {e}", level='ERROR')

    async def _on_ec_update(self, entity, attribute, old, new, kwargs):
        """Handle EC sensor updates."""
        try:
            if new == 'unavailable' or new == 'unknown':
                return
            
            ec_value = float(new)
            timestamp = datetime.now()
            
            # Add to sensor fusion
            fusion_result = self.sensor_fusion.add_sensor_reading(
                entity, ec_value, timestamp, 'ec'
            )
            
            # Update dashboard EC history
            self.dashboard_data['ec_history'].append({
                'timestamp': timestamp.isoformat(),
                'sensor_id': entity,
                'raw_value': ec_value,
                'fused_value': fusion_result['fused_value'],
                'is_outlier': fusion_result['is_outlier'],
                'fusion_confidence': fusion_result['fusion_confidence']
            })
            
            # Trim history
            self._trim_history('ec_history')
            
        except Exception as e:
            self.log(f"❌ Error processing EC update: {e}", level='ERROR')

    async def _on_system_update(self, entity, attribute, old, new, kwargs):
        """Handle system state updates."""
        try:
            timestamp = datetime.now()
            
            # Track phase transitions
            if 'phase' in entity:
                self.dashboard_data['phase_history'].append({
                    'timestamp': timestamp.isoformat(),
                    'phase': new,
                    'previous_phase': old
                })
                self._trim_history('phase_history')
                
                self.log(f"📊 Phase transition: {old} → {new}")
            
        except Exception as e:
            self.log(f"❌ Error processing system update: {e}", level='ERROR')

    async def _on_irrigation_event(self, event_name, data, kwargs):
        """Handle irrigation shot events."""
        try:
            timestamp = datetime.now()
            
            # Record irrigation event
            irrigation_data = {
                'timestamp': timestamp.isoformat(),
                'zone': data.get('zone', 1),
                'duration': data.get('duration_seconds', 0),
                'shot_type': data.get('shot_type', 'manual'),
                'efficiency': 0.0  # Will be calculated later
            }
            
            self.dashboard_data['irrigation_events'].append(irrigation_data)
            self._trim_history('irrigation_events')
            
            # Prepare ML training data
            await self._prepare_ml_training_data(irrigation_data)
            
            self.log(f"💧 Irrigation event: Zone {irrigation_data['zone']}, {irrigation_data['duration']}s")
            
        except Exception as e:
            self.log(f"❌ Error processing irrigation event: {e}", level='ERROR')

    async def _on_phase_transition(self, event_name, data, kwargs):
        """Handle phase transition events."""
        try:
            self.log(f"🔄 Phase transition event: {data}")
            
        except Exception as e:
            self.log(f"❌ Error processing phase transition: {e}", level='ERROR')

    async def _update_dashboard(self, kwargs):
        """Main dashboard update routine."""
        try:
            # Generate real-time graphs
            graphs = await self._generate_dashboard_graphs()
            
            # Update dashboard entities
            await self._update_dashboard_entities(graphs)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations()
            
            # Update recommendation entities
            await self._update_recommendation_entities(recommendations)
            
        except Exception as e:
            self.log(f"❌ Error updating dashboard: {e}", level='ERROR')

    async def _generate_dashboard_graphs(self) -> Dict:
        """Generate Athena-style dashboard graphs."""
        graphs = {}
        
        try:
            # 1. VWC Trending Graph (Main Athena Style)
            graphs['vwc_trending'] = await self._create_vwc_trending_graph()
            
            # 2. EC Trending Graph
            graphs['ec_trending'] = await self._create_ec_trending_graph()
            
            # 3. Dryback Analysis Graph
            graphs['dryback_analysis'] = await self._create_dryback_analysis_graph()
            
            # 4. ML Predictions Graph
            graphs['ml_predictions'] = await self._create_ml_predictions_graph()
            
            # 5. Sensor Health Heatmap
            graphs['sensor_health'] = await self._create_sensor_health_graph()
            
            # 6. Phase Timeline
            graphs['phase_timeline'] = await self._create_phase_timeline_graph()
            
            # 7. Performance Analytics
            graphs['performance_analytics'] = await self._create_performance_graph()
            
        except Exception as e:
            self.log(f"❌ Error generating graphs: {e}", level='ERROR')
        
        return graphs

    async def _create_vwc_trending_graph(self) -> str:
        """Create Athena-style VWC trending graph."""
        try:
            if not self.dashboard_data['vwc_history']:
                return ""
            
            # Prepare data
            df = pd.DataFrame(self.dashboard_data['vwc_history'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Create subplot with secondary y-axis
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=('VWC Trending - Athena Style', 'Sensor Confidence & Outliers'),
                row_heights=[0.7, 0.3]
            )
            
            # Main VWC trend (fused values)
            fused_data = df[df['fused_value'].notna()]
            if not fused_data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=fused_data['timestamp'],
                        y=fused_data['fused_value'],
                        mode='lines',
                        name='Fused VWC',
                        line=dict(color=self.dashboard_config['colors']['primary'], width=3),
                        hovertemplate='VWC: %{y:.1f}%<br>Time: %{x}<extra></extra>'
                    ),
                    row=1, col=1
                )
            
            # Individual sensors (lighter traces)
            sensor_colors = px.colors.qualitative.Set3
            for i, sensor in enumerate(self.sensor_entities['vwc_sensors']):
                sensor_data = df[df['sensor_id'] == sensor]
                if not sensor_data.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=sensor_data['timestamp'],
                            y=sensor_data['raw_value'],
                            mode='lines',
                            name=sensor.split('.')[-1],
                            line=dict(color=sensor_colors[i % len(sensor_colors)], width=1, dash='dot'),
                            opacity=0.6,
                            hovertemplate=f'{sensor}: %{{y:.1f}}%<extra></extra>'
                        ),
                        row=1, col=1
                    )
            
            # Outliers
            outliers = df[df['is_outlier'] == True]
            if not outliers.empty:
                fig.add_trace(
                    go.Scatter(
                        x=outliers['timestamp'],
                        y=outliers['raw_value'],
                        mode='markers',
                        name='Outliers',
                        marker=dict(color='red', size=8, symbol='x'),
                        hovertemplate='Outlier: %{y:.1f}%<extra></extra>'
                    ),
                    row=1, col=1
                )
            
            # Dryback markers
            if self.dashboard_data['dryback_history']:
                dryback_df = pd.DataFrame(self.dashboard_data['dryback_history'])
                dryback_df['timestamp'] = pd.to_datetime(dryback_df['timestamp'])
                active_dryback = dryback_df[dryback_df['dryback_in_progress'] == True]
                
                if not active_dryback.empty:
                    # Add dryback regions
                    for _, row in active_dryback.iterrows():
                        fig.add_vline(
                            x=row['timestamp'],
                            line=dict(color='orange', width=1, dash='dash'),
                            annotation_text=f"Dryback: {row['dryback_percentage']:.1f}%",
                            row=1, col=1
                        )
            
            # Confidence score subplot
            if not fused_data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=fused_data['timestamp'],
                        y=fused_data['fusion_confidence'],
                        mode='lines+markers',
                        name='Fusion Confidence',
                        line=dict(color=self.dashboard_config['colors']['accent'], width=2),
                        marker=dict(size=4),
                        hovertemplate='Confidence: %{y:.2f}<extra></extra>'
                    ),
                    row=2, col=1
                )
            
            # Crop profile targets (if available)
            current_params = self.crop_profiles.get_current_parameters()
            if current_params:
                # Add target bands
                vwc_min = current_params.get('vwc_target_min', 50)
                vwc_max = current_params.get('vwc_target_max', 70)
                
                fig.add_hrect(
                    y0=vwc_min, y1=vwc_max,
                    fillcolor=self.dashboard_config['colors']['secondary'],
                    opacity=0.2,
                    annotation_text="Target Zone",
                    row=1, col=1
                )
            
            # Layout styling
            fig.update_layout(
                title={
                    'text': 'Advanced VWC Monitoring - Athena Style',
                    'x': 0.5,
                    'font': {'size': 20, 'color': 'white'}
                },
                template=self.dashboard_config['theme'],
                height=600,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
            fig.update_xaxes(title_text="Time", row=2, col=1)
            fig.update_yaxes(title_text="VWC (%)", row=1, col=1)
            fig.update_yaxes(title_text="Confidence", range=[0, 1], row=2, col=1)
            
            return fig.to_html(include_plotlyjs='cdn', div_id='vwc_trending_graph')
            
        except Exception as e:
            self.log(f"❌ Error creating VWC graph: {e}", level='ERROR')
            return ""

    async def _create_ec_trending_graph(self) -> str:
        """Create EC trending graph with target zones."""
        try:
            if not self.dashboard_data['ec_history']:
                return ""
            
            df = pd.DataFrame(self.dashboard_data['ec_history'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig = go.Figure()
            
            # Fused EC values
            fused_data = df[df['fused_value'].notna()]
            if not fused_data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=fused_data['timestamp'],
                        y=fused_data['fused_value'],
                        mode='lines',
                        name='Fused EC',
                        line=dict(color=self.dashboard_config['colors']['secondary'], width=3),
                        hovertemplate='EC: %{y:.2f} mS/cm<extra></extra>'
                    )
                )
            
            # Individual sensors
            sensor_colors = px.colors.qualitative.Pastel
            for i, sensor in enumerate(self.sensor_entities['ec_sensors']):
                sensor_data = df[df['sensor_id'] == sensor]
                if not sensor_data.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=sensor_data['timestamp'],
                            y=sensor_data['raw_value'],
                            mode='lines',
                            name=sensor.split('.')[-1],
                            line=dict(color=sensor_colors[i % len(sensor_colors)], width=1, dash='dot'),
                            opacity=0.6
                        )
                    )
            
            # EC targets from crop profile
            current_params = self.crop_profiles.get_current_parameters()
            if current_params:
                ec_baseline = current_params.get('ec_baseline', 3.0)
                ec_max = current_params.get('ec_max', 6.0)
                
                fig.add_hline(
                    y=ec_baseline,
                    line=dict(color='green', width=2, dash='dash'),
                    annotation_text=f"Baseline: {ec_baseline} mS/cm"
                )
                
                fig.add_hline(
                    y=ec_max,
                    line=dict(color='red', width=2, dash='dash'),
                    annotation_text=f"Maximum: {ec_max} mS/cm"
                )
            
            fig.update_layout(
                title='EC Trending with Target Zones',
                template=self.dashboard_config['theme'],
                height=400,
                xaxis_title="Time",
                yaxis_title="EC (mS/cm)"
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id='ec_trending_graph')
            
        except Exception as e:
            self.log(f"❌ Error creating EC graph: {e}", level='ERROR')
            return ""

    async def _create_dryback_analysis_graph(self) -> str:
        """Create advanced dryback analysis visualization."""
        try:
            if not self.dashboard_data['dryback_history']:
                return ""
            
            df = pd.DataFrame(self.dashboard_data['dryback_history'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                subplot_titles=('Dryback Percentage Over Time', 'Dryback Detection Confidence'),
                vertical_spacing=0.15
            )
            
            # Dryback percentage
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['dryback_percentage'],
                    mode='lines+markers',
                    name='Dryback %',
                    line=dict(color=self.dashboard_config['colors']['accent'], width=2),
                    marker=dict(size=4),
                    fill='tonexty',
                    hovertemplate='Dryback: %{y:.1f}%<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Confidence score
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['confidence'],
                    mode='lines',
                    name='Detection Confidence',
                    line=dict(color='lightblue', width=2),
                    hovertemplate='Confidence: %{y:.2f}<extra></extra>'
                ),
                row=2, col=1
            )
            
            # Target dryback zones
            current_params = self.crop_profiles.get_current_parameters()
            if current_params:
                target_dryback = current_params.get('dryback_target', 15)
                
                fig.add_hline(
                    y=target_dryback,
                    line=dict(color='green', width=2, dash='dash'),
                    annotation_text=f"Target: {target_dryback}%",
                    row=1, col=1
                )
            
            fig.update_layout(
                title='Advanced Dryback Detection Analysis',
                template=self.dashboard_config['theme'],
                height=500
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id='dryback_analysis_graph')
            
        except Exception as e:
            self.log(f"❌ Error creating dryback graph: {e}", level='ERROR')
            return ""

    async def _create_ml_predictions_graph(self) -> str:
        """Create ML irrigation predictions visualization."""
        try:
            # Get current ML predictions
            current_features = await self._get_current_ml_features()
            if not current_features:
                return ""
            
            predictions = self.ml_predictor.predict_irrigation_need(current_features)
            
            if not predictions.get('prediction_available', False):
                return ""
            
            pred_data = predictions['predictions']
            df = pd.DataFrame(pred_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig = go.Figure()
            
            # Irrigation probability prediction
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['irrigation_probability'],
                    mode='lines+markers',
                    name='Irrigation Need Probability',
                    line=dict(color=self.dashboard_config['colors']['primary'], width=3),
                    marker=dict(size=6),
                    hovertemplate='Probability: %{y:.1%}<extra></extra>'
                )
            )
            
            # Confidence bands
            model_confidence = predictions.get('model_confidence', 0.5)
            upper_bound = df['irrigation_probability'] + (1 - model_confidence) * 0.2
            lower_bound = df['irrigation_probability'] - (1 - model_confidence) * 0.2
            
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=upper_bound,
                    mode='lines',
                    name='Confidence Upper',
                    line=dict(color='rgba(0,204,150,0.3)', width=0),
                    showlegend=False
                )
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=lower_bound,
                    mode='lines',
                    name='Confidence Lower',
                    line=dict(color='rgba(0,204,150,0.3)', width=0),
                    fill='tonexty',
                    fillcolor='rgba(0,204,150,0.2)',
                    showlegend=False
                )
            )
            
            # Thresholds
            fig.add_hline(
                y=0.7,
                line=dict(color='orange', width=2, dash='dash'),
                annotation_text="High Need Threshold"
            )
            
            fig.add_hline(
                y=0.9,
                line=dict(color='red', width=2, dash='dash'),
                annotation_text="Critical Need Threshold"
            )
            
            fig.update_layout(
                title='ML Irrigation Predictions',
                template=self.dashboard_config['theme'],
                height=400,
                xaxis_title="Time",
                yaxis_title="Irrigation Probability",
                yaxis=dict(range=[0, 1])
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id='ml_predictions_graph')
            
        except Exception as e:
            self.log(f"❌ Error creating ML predictions graph: {e}", level='ERROR')
            return ""

    async def _create_sensor_health_graph(self) -> str:
        """Create sensor health status heatmap."""
        try:
            health_report = self.sensor_fusion.get_sensor_health_report()
            
            if not health_report['sensors']:
                return ""
            
            # Prepare data for heatmap
            sensors = []
            reliability_scores = []
            outlier_rates = []
            health_statuses = []
            
            for sensor_id, data in health_report['sensors'].items():
                sensors.append(sensor_id.split('.')[-1])  # Short name
                reliability_scores.append(data['reliability_score'])
                outlier_rates.append(data['outlier_rate'])
                health_statuses.append(data['health_status'])
            
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Sensor Reliability', 'Outlier Rate'),
                specs=[[{"type": "bar"}, {"type": "bar"}]]
            )
            
            # Reliability scores
            fig.add_trace(
                go.Bar(
                    x=sensors,
                    y=reliability_scores,
                    name='Reliability',
                    marker_color=self.dashboard_config['colors']['primary'],
                    hovertemplate='Sensor: %{x}<br>Reliability: %{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Outlier rates
            fig.add_trace(
                go.Bar(
                    x=sensors,
                    y=outlier_rates,
                    name='Outlier Rate',
                    marker_color=self.dashboard_config['colors']['accent'],
                    hovertemplate='Sensor: %{x}<br>Outlier Rate: %{y:.2%}<extra></extra>'
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                title='Sensor Health Status',
                template=self.dashboard_config['theme'],
                height=400,
                showlegend=False
            )
            
            fig.update_yaxes(title_text="Reliability Score", range=[0, 1], row=1, col=1)
            fig.update_yaxes(title_text="Outlier Rate", range=[0, 0.5], row=1, col=2)
            
            return fig.to_html(include_plotlyjs='cdn', div_id='sensor_health_graph')
            
        except Exception as e:
            self.log(f"❌ Error creating sensor health graph: {e}", level='ERROR')
            return ""

    async def _create_phase_timeline_graph(self) -> str:
        """Create irrigation phase timeline visualization."""
        try:
            if not self.dashboard_data['phase_history']:
                return ""
            
            df = pd.DataFrame(self.dashboard_data['phase_history'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Create Gantt-style chart
            fig = go.Figure()
            
            phase_colors = {
                'P0': '#FF6B6B',  # Red - Morning dryback
                'P1': '#4ECDC4',  # Teal - Ramp-up
                'P2': '#45B7D1',  # Blue - Maintenance
                'P3': '#FFA07A'   # Orange - Pre-lights-off
            }
            
            # Create phase blocks
            for i in range(len(df) - 1):
                phase = df.iloc[i]['phase']
                start_time = df.iloc[i]['timestamp']
                end_time = df.iloc[i + 1]['timestamp']
                duration = (end_time - start_time).total_seconds() / 60  # minutes
                
                fig.add_trace(
                    go.Scatter(
                        x=[start_time, end_time, end_time, start_time, start_time],
                        y=[0, 0, 1, 1, 0],
                        fill='toself',
                        fillcolor=phase_colors.get(phase, '#cccccc'),
                        line=dict(color=phase_colors.get(phase, '#cccccc')),
                        name=f'Phase {phase}',
                        hovertemplate=f'Phase {phase}<br>Duration: {duration:.1f} min<extra></extra>',
                        showlegend=True if i == 0 or df.iloc[i-1]['phase'] != phase else False
                    )
                )
            
            fig.update_layout(
                title='Irrigation Phase Timeline (Last 24 Hours)',
                template=self.dashboard_config['theme'],
                height=200,
                xaxis_title="Time",
                yaxis=dict(showticklabels=False, range=[0, 1]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id='phase_timeline_graph')
            
        except Exception as e:
            self.log(f"❌ Error creating phase timeline graph: {e}", level='ERROR')
            return ""

    async def _create_performance_graph(self) -> str:
        """Create system performance analytics visualization."""
        try:
            if not self.dashboard_data['performance_metrics']:
                return ""
            
            # Get performance data
            metrics = self.dashboard_data['performance_metrics']
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Irrigation Efficiency', 'Water Usage Trends',
                    'Target Achievement Rate', 'System Health Score'
                ),
                specs=[
                    [{"type": "indicator"}, {"type": "scatter"}],
                    [{"type": "indicator"}, {"type": "indicator"}]
                ]
            )
            
            # Irrigation Efficiency Gauge
            efficiency = metrics.get('irrigation_efficiency', 0.5)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=efficiency * 100,
                    title={'text': "Efficiency %"},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': self.dashboard_config['colors']['primary']},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "yellow"},
                            {'range': [80, 100], 'color': "green"}
                        ]
                    }
                ),
                row=1, col=1
            )
            
            # Water usage trends (if available)
            if 'water_usage_history' in metrics:
                usage_data = metrics['water_usage_history']
                df_usage = pd.DataFrame(usage_data)
                df_usage['timestamp'] = pd.to_datetime(df_usage['timestamp'])
                
                fig.add_trace(
                    go.Scatter(
                        x=df_usage['timestamp'],
                        y=df_usage['daily_usage'],
                        mode='lines+markers',
                        name='Daily Water Usage',
                        line=dict(color=self.dashboard_config['colors']['secondary'])
                    ),
                    row=1, col=2
                )
            
            # Target Achievement Rate
            achievement_rate = metrics.get('target_achievement_rate', 0.7)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=achievement_rate * 100,
                    title={'text': "Target Hit %"},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': self.dashboard_config['colors']['accent']},
                        'steps': [
                            {'range': [0, 60], 'color': "lightgray"},
                            {'range': [60, 85], 'color': "yellow"},
                            {'range': [85, 100], 'color': "green"}
                        ]
                    }
                ),
                row=2, col=1
            )
            
            # System Health Score
            health_score = metrics.get('system_health_score', 0.8)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=health_score * 100,
                    title={'text': "System Health"},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': 'lightblue'},
                        'steps': [
                            {'range': [0, 70], 'color': "lightgray"},
                            {'range': [70, 90], 'color': "yellow"},
                            {'range': [90, 100], 'color': "green"}
                        ]
                    }
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                title='System Performance Analytics',
                template=self.dashboard_config['theme'],
                height=600
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id='performance_graph')
            
        except Exception as e:
            self.log(f"❌ Error creating performance graph: {e}", level='ERROR')
            return ""

    async def _get_current_ml_features(self) -> Optional[Dict]:
        """Extract current ML features from system state."""
        try:
            features = {}
            
            # Get latest VWC from fusion
            if self.dashboard_data['vwc_history']:
                latest_vwc = self.dashboard_data['vwc_history'][-1]
                features['current_vwc'] = latest_vwc.get('fused_value', latest_vwc.get('raw_value', 0))
                
                # Calculate VWC trends
                if len(self.dashboard_data['vwc_history']) >= 10:
                    vwc_values = [h.get('fused_value', h.get('raw_value', 0)) for h in self.dashboard_data['vwc_history'][-10:]]
                    features['vwc_trend_5min'] = vwc_values[-1] - vwc_values[-3] if len(vwc_values) >= 3 else 0
                    features['vwc_trend_15min'] = vwc_values[-1] - vwc_values[-6] if len(vwc_values) >= 6 else 0
                    features['vwc_trend_30min'] = vwc_values[-1] - vwc_values[0]
            
            # Get latest EC
            if self.dashboard_data['ec_history']:
                latest_ec = self.dashboard_data['ec_history'][-1]
                features['current_ec'] = latest_ec.get('fused_value', latest_ec.get('raw_value', 0))
                
                # EC trend and ratio
                if len(self.dashboard_data['ec_history']) >= 5:
                    ec_values = [h.get('fused_value', h.get('raw_value', 0)) for h in self.dashboard_data['ec_history'][-5:]]
                    features['ec_trend_5min'] = ec_values[-1] - ec_values[0]
                    features['ec_ratio'] = ec_values[-1] / max(ec_values[0], 0.1)
            
            # Irrigation history
            recent_irrigations = [e for e in self.dashboard_data['irrigation_events'] 
                                if (datetime.now() - datetime.fromisoformat(e['timestamp'])).total_seconds() < 86400]
            features['irrigation_count_24h'] = len(recent_irrigations)
            
            if recent_irrigations:
                last_irrigation = max(recent_irrigations, key=lambda x: x['timestamp'])
                time_since = (datetime.now() - datetime.fromisoformat(last_irrigation['timestamp'])).total_seconds() / 60
                features['time_since_last_irrigation'] = time_since
                features['avg_irrigation_duration'] = np.mean([i['duration'] for i in recent_irrigations])
            else:
                features['time_since_last_irrigation'] = 1440  # 24 hours
                features['avg_irrigation_duration'] = 0
            
            # System state
            features['current_phase'] = self.get_state(self.sensor_entities['system']['current_phase'], default='P2')
            features['steering_mode'] = self.get_state(self.sensor_entities['system']['steering_mode'], default='Vegetative')
            
            # Dryback info
            if self.dashboard_data['dryback_history']:
                latest_dryback = self.dashboard_data['dryback_history'][-1]
                features['dryback_percentage'] = latest_dryback['dryback_percentage']
                features['dryback_rate'] = latest_dryback.get('dryback_rate', 0)
            
            # Environmental data
            features['temperature'] = float(self.get_state(self.sensor_entities['environmental']['temperature'], default=25))
            features['humidity'] = float(self.get_state(self.sensor_entities['environmental']['humidity'], default=60))
            features['vpd'] = float(self.get_state(self.sensor_entities['environmental']['vpd'], default=1.0))
            features['lights_on'] = self.get_state('sun.sun', attribute='elevation', default=0) > 0
            
            return features
            
        except Exception as e:
            self.log(f"❌ Error extracting ML features: {e}", level='ERROR')
            return None

    async def _update_ml_predictions(self, kwargs):
        """Update ML predictions and recommendations."""
        try:
            # Get current features
            features = await self._get_current_ml_features()
            if not features:
                return
            
            # Generate predictions
            predictions = self.ml_predictor.predict_irrigation_need(features)
            
            if predictions.get('prediction_available', False):
                # Store predictions
                self.dashboard_data['ml_predictions'] = predictions
                
                # Update dashboard entities with predictions
                await self._update_ml_entities(predictions)
                
                self.log(f"🤖 ML predictions updated - Max need: {predictions['analysis']['max_irrigation_need']:.2f}")
            
        except Exception as e:
            self.log(f"❌ Error updating ML predictions: {e}", level='ERROR')

    async def _monitor_sensor_health(self, kwargs):
        """Monitor and report sensor health status."""
        try:
            health_report = self.sensor_fusion.get_sensor_health_report()
            
            # Update sensor health tracking
            self.dashboard_data['sensor_health'] = health_report
            
            # Alert on sensor issues
            faulty_sensors = health_report['faulty_sensors']
            offline_sensors = health_report['offline_sensors']
            
            if faulty_sensors > 0:
                self.log(f"⚠️ {faulty_sensors} sensors are faulty", level='WARNING')
            
            if offline_sensors > 0:
                self.log(f"🔴 {offline_sensors} sensors are offline", level='WARNING')
            
            # Update HA entities
            await self._update_sensor_health_entities(health_report)
            
        except Exception as e:
            self.log(f"❌ Error monitoring sensor health: {e}", level='ERROR')

    async def _update_performance_metrics(self, kwargs):
        """Update system performance metrics."""
        try:
            metrics = {}
            
            # Calculate irrigation efficiency
            recent_irrigations = [e for e in self.dashboard_data['irrigation_events']
                                if (datetime.now() - datetime.fromisoformat(e['timestamp'])).total_seconds() < 86400]
            
            if recent_irrigations:
                avg_efficiency = np.mean([i.get('efficiency', 0.5) for i in recent_irrigations])
                metrics['irrigation_efficiency'] = avg_efficiency
            
            # Calculate target achievement rate
            if self.dashboard_data['dryback_history']:
                recent_dryback = self.dashboard_data['dryback_history'][-20:]  # Last 20 samples
                current_params = self.crop_profiles.get_current_parameters()
                
                if current_params:
                    target_dryback = current_params.get('dryback_target', 15)
                    achieved_count = sum(1 for d in recent_dryback 
                                       if abs(d['dryback_percentage'] - target_dryback) < 5)
                    metrics['target_achievement_rate'] = achieved_count / len(recent_dryback)
            
            # System health score
            health_report = self.dashboard_data.get('sensor_health', {})
            total_sensors = health_report.get('total_sensors', 1)
            healthy_sensors = health_report.get('healthy_sensors', 0)
            metrics['system_health_score'] = healthy_sensors / total_sensors if total_sensors > 0 else 0
            
            # Store metrics
            self.dashboard_data['performance_metrics'] = metrics
            
            # Update HA entities
            await self._update_performance_entities(metrics)
            
        except Exception as e:
            self.log(f"❌ Error updating performance metrics: {e}", level='ERROR')

    async def _prepare_ml_training_data(self, irrigation_data: Dict):
        """Prepare and add ML training sample."""
        try:
            # Get features at time of irrigation
            features = await self._get_current_ml_features()
            if not features:
                return
            
            # Calculate irrigation outcome (simplified for now)
            outcome = {
                'irrigation_efficiency': 0.7,  # Would be calculated from actual VWC response
                'vwc_improvement': 5.0,  # VWC increase from irrigation
                'optimal_timing_score': 0.8  # How optimal the timing was
            }
            
            # Add training sample
            result = self.ml_predictor.add_training_sample(features, outcome)
            
            if result['status'] == 'retrained':
                self.log(f"🎓 ML models retrained - Performance: {result['performance']['ensemble']['r2']:.3f}")
            
        except Exception as e:
            self.log(f"❌ Error preparing ML training data: {e}", level='ERROR')

    async def _update_dashboard_entities(self, graphs: Dict):
        """Update Home Assistant dashboard entities."""
        try:
            # Create dashboard HTML
            dashboard_html = self._create_dashboard_html(graphs)
            
            # Store as HA attribute or file
            self.set_state('sensor.crop_steering_dashboard_html', 
                          state='active',
                          attributes={'html_content': dashboard_html})
            
        except Exception as e:
            self.log(f"❌ Error updating dashboard entities: {e}", level='ERROR')

    async def _update_ml_entities(self, predictions: Dict):
        """Update ML prediction entities."""
        try:
            analysis = predictions.get('analysis', {})
            
            self.set_state('sensor.crop_steering_ml_irrigation_need',
                          state=analysis.get('max_irrigation_need', 0),
                          attributes=predictions)
            
            self.set_state('sensor.crop_steering_ml_confidence',
                          state=predictions.get('model_confidence', 0),
                          attributes={'predictions': predictions})
            
        except Exception as e:
            self.log(f"❌ Error updating ML entities: {e}", level='ERROR')

    async def _update_sensor_health_entities(self, health_report: Dict):
        """Update sensor health entities."""
        try:
            self.set_state('sensor.crop_steering_sensor_health',
                          state=health_report['healthy_sensors'],
                          attributes=health_report)
            
        except Exception as e:
            self.log(f"❌ Error updating sensor health entities: {e}", level='ERROR')

    async def _update_performance_entities(self, metrics: Dict):
        """Update performance metric entities."""
        try:
            for metric_name, value in metrics.items():
                entity_id = f'sensor.crop_steering_{metric_name}'
                self.set_state(entity_id, state=value, attributes={'last_updated': datetime.now().isoformat()})
            
        except Exception as e:
            self.log(f"❌ Error updating performance entities: {e}", level='ERROR')

    async def _generate_recommendations(self) -> Dict:
        """Generate intelligent irrigation recommendations."""
        try:
            recommendations = {}
            
            # ML-based recommendations
            if self.dashboard_data.get('ml_predictions'):
                ml_predictions = self.dashboard_data['ml_predictions']
                ml_recs = ml_predictions.get('recommendations', {})
                recommendations.update(ml_recs)
            
            # Dryback-based recommendations
            if self.dashboard_data['dryback_history']:
                latest_dryback = self.dashboard_data['dryback_history'][-1]
                current_params = self.crop_profiles.get_current_parameters()
                
                if current_params and latest_dryback['dryback_in_progress']:
                    target_dryback = current_params.get('dryback_target', 15)
                    current_dryback = latest_dryback['dryback_percentage']
                    
                    if current_dryback >= target_dryback * 0.9:
                        recommendations['dryback_action'] = f"Target dryback achieved ({current_dryback:.1f}%), ready for irrigation"
                    elif current_dryback < target_dryback * 0.5:
                        recommendations['dryback_action'] = f"Early in dryback cycle ({current_dryback:.1f}%), continue monitoring"
            
            # Sensor health recommendations
            health_report = self.dashboard_data.get('sensor_health', {})
            if health_report.get('faulty_sensors', 0) > 0:
                recommendations['sensor_maintenance'] = "Attention required: faulty sensors detected"
            
            return recommendations
            
        except Exception as e:
            self.log(f"❌ Error generating recommendations: {e}", level='ERROR')
            return {}

    async def _update_recommendation_entities(self, recommendations: Dict):
        """Update recommendation entities."""
        try:
            self.set_state('sensor.crop_steering_recommendations',
                          state='active',
                          attributes=recommendations)
            
        except Exception as e:
            self.log(f"❌ Error updating recommendation entities: {e}", level='ERROR')

    def _create_dashboard_html(self, graphs: Dict) -> str:
        """Create complete dashboard HTML."""
        html_parts = [
            "<div style='background-color: #2f3136; color: white; padding: 20px;'>",
            "<h1 style='text-align: center; color: #00cc96;'>🌱 Advanced Crop Steering Dashboard</h1>",
            "<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px;'>"
        ]
        
        for graph_name, graph_html in graphs.items():
            if graph_html:
                html_parts.append(f"<div style='margin-bottom: 20px;'>{graph_html}</div>")
        
        html_parts.extend(["</div>", "</div>"])
        
        return "\n".join(html_parts)

    def _trim_history(self, history_key: str):
        """Trim history data to maximum points."""
        if history_key in self.dashboard_data:
            history = self.dashboard_data[history_key]
            if len(history) > self.max_data_points:
                # Remove oldest entries
                excess = len(history) - self.max_data_points
                self.dashboard_data[history_key] = history[excess:]

    def get_dashboard_status(self) -> Dict:
        """Get comprehensive dashboard status."""
        return {
            'modules_initialized': {
                'dryback_detector': bool(self.dryback_detector),
                'sensor_fusion': bool(self.sensor_fusion),
                'ml_predictor': bool(self.ml_predictor),
                'crop_profiles': bool(self.crop_profiles)
            },
            'data_points': {
                'vwc_history': len(self.dashboard_data['vwc_history']),
                'ec_history': len(self.dashboard_data['ec_history']),
                'dryback_history': len(self.dashboard_data['dryback_history']),
                'irrigation_events': len(self.dashboard_data['irrigation_events'])
            },
            'ml_status': self.ml_predictor.get_model_status() if self.ml_predictor else {},
            'sensor_health': self.dashboard_data.get('sensor_health', {}),
            'active_crop_profile': self.crop_profiles.current_profile if self.crop_profiles else None
        }
