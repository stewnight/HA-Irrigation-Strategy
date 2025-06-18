"""
Advanced Dryback Detection for Crop Steering
Implements multi-scale peak detection and real-time dryback analysis
Based on research: MSPD (Multi-Scale Peak Detection) algorithms
"""

import numpy as np
import pandas as pd
from collections import deque
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from scipy import signal
from scipy.stats import zscore
import math

_LOGGER = logging.getLogger(__name__)


class AdvancedDrybackDetector:
    """
    Advanced dryback detection using multi-scale peak detection algorithms.
    
    Features:
    - Real-time peak/valley detection with noise reduction
    - Dryback percentage calculation with confidence scoring
    - Pattern recognition for irrigation timing optimization
    - Adaptive thresholds based on historical data
    """
    
    def __init__(self, window_size: int = 100, min_peak_distance: int = 10, 
                 noise_threshold: float = 0.5, confidence_threshold: float = 0.7):
        """
        Initialize the advanced dryback detector.
        
        Args:
            window_size: Size of rolling window for analysis
            min_peak_distance: Minimum distance between peaks (data points)
            noise_threshold: Threshold for noise filtering (% VWC)
            confidence_threshold: Minimum confidence for peak detection
        """
        self.window_size = window_size
        self.min_peak_distance = min_peak_distance
        self.noise_threshold = noise_threshold
        self.confidence_threshold = confidence_threshold
        
        # Data storage
        self.vwc_history = deque(maxlen=window_size * 2)  # Extended for better analysis
        self.timestamp_history = deque(maxlen=window_size * 2)
        self.peaks = deque(maxlen=50)  # Store detected peaks
        self.valleys = deque(maxlen=50)  # Store detected valleys
        
        # Current state
        self.current_dryback = 0.0
        self.dryback_in_progress = False
        self.last_peak_vwc = None
        self.last_peak_time = None
        self.last_valley_vwc = None
        self.last_valley_time = None
        self.dryback_start_time = None
        self.confidence_score = 0.0
        
        # Adaptive parameters
        self.adaptive_threshold_multiplier = 3.0  # Start with 3 std deviations
        self.moving_average_window = 20
        
        _LOGGER.info(f"Advanced Dryback Detector initialized: window={window_size}, "
                    f"min_distance={min_peak_distance}, noise={noise_threshold}")

    def add_vwc_reading(self, vwc: float, timestamp: datetime = None) -> Dict:
        """
        Add new VWC reading and analyze for dryback patterns.
        
        Args:
            vwc: Volumetric Water Content percentage
            timestamp: Timestamp of reading (default: now)
            
        Returns:
            Dict with dryback analysis results
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        # Add to history
        self.vwc_history.append(vwc)
        self.timestamp_history.append(timestamp)
        
        # Need minimum data points for analysis
        if len(self.vwc_history) < self.min_peak_distance * 2:
            return self._get_status_dict()
        
        # Perform multi-scale peak detection
        peaks, valleys = self._detect_peaks_valleys()
        
        # Update peak/valley history
        if peaks:
            self.peaks.extend(peaks)
        if valleys:
            self.valleys.extend(valleys)
        
        # Analyze current dryback status
        self._analyze_dryback_status()
        
        # Calculate confidence score
        self._calculate_confidence_score()
        
        return self._get_status_dict()

    def _detect_peaks_valleys(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Multi-scale peak detection with noise reduction.
        
        Returns:
            Tuple of (peaks, valleys) as lists of dictionaries
        """
        if len(self.vwc_history) < self.min_peak_distance * 2:
            return [], []
        
        # Convert to numpy array for analysis
        vwc_data = np.array(list(self.vwc_history))
        timestamps = list(self.timestamp_history)
        
        # Apply smoothing to reduce noise
        smoothed_data = self._apply_smoothing(vwc_data)
        
        # Calculate adaptive threshold
        std_dev = np.std(smoothed_data[-self.window_size:]) if len(smoothed_data) >= self.window_size else np.std(smoothed_data)
        threshold = std_dev * self.adaptive_threshold_multiplier
        
        # Detect peaks (irrigation events)
        peak_indices, peak_properties = signal.find_peaks(
            smoothed_data,
            height=np.mean(smoothed_data) + threshold,
            distance=self.min_peak_distance,
            prominence=self.noise_threshold
        )
        
        # Detect valleys (dryback bottoms)
        inverted_data = -smoothed_data
        valley_indices, valley_properties = signal.find_peaks(
            inverted_data,
            height=-np.mean(smoothed_data) + threshold,
            distance=self.min_peak_distance,
            prominence=self.noise_threshold
        )
        
        # Convert to dictionaries with metadata
        new_peaks = []
        for idx in peak_indices:
            if idx < len(timestamps) and idx >= len(self.vwc_history) - 20:  # Recent peaks only
                peak_data = {
                    'vwc': vwc_data[idx],
                    'timestamp': timestamps[idx],
                    'index': idx,
                    'confidence': self._calculate_peak_confidence(idx, vwc_data, peak_properties)
                }
                if peak_data['confidence'] >= self.confidence_threshold:
                    new_peaks.append(peak_data)
        
        new_valleys = []
        for idx in valley_indices:
            if idx < len(timestamps) and idx >= len(self.vwc_history) - 20:  # Recent valleys only
                valley_data = {
                    'vwc': vwc_data[idx],
                    'timestamp': timestamps[idx],
                    'index': idx,
                    'confidence': self._calculate_peak_confidence(idx, vwc_data, valley_properties)
                }
                if valley_data['confidence'] >= self.confidence_threshold:
                    new_valleys.append(valley_data)
        
        return new_peaks, new_valleys

    def _apply_smoothing(self, data: np.ndarray, method: str = 'savgol') -> np.ndarray:
        """
        Apply smoothing to reduce noise while preserving peaks.
        
        Args:
            data: Input VWC data
            method: Smoothing method ('savgol', 'gaussian', 'moving_avg')
            
        Returns:
            Smoothed data array
        """
        if len(data) < 5:
            return data
        
        if method == 'savgol':
            # Savitzky-Golay filter - good for preserving peaks
            window_length = min(len(data) // 4, 15)
            if window_length % 2 == 0:
                window_length += 1
            if window_length >= 3:
                return signal.savgol_filter(data, window_length, 2)
                
        elif method == 'gaussian':
            # Gaussian filter
            sigma = max(1, len(data) // 20)
            return signal.gaussian_filter1d(data, sigma)
            
        elif method == 'moving_avg':
            # Simple moving average
            window = min(len(data) // 5, self.moving_average_window)
            return np.convolve(data, np.ones(window)/window, mode='same')
        
        return data

    def _calculate_peak_confidence(self, peak_idx: int, data: np.ndarray, 
                                   properties: Dict) -> float:
        """
        Calculate confidence score for detected peak/valley.
        
        Args:
            peak_idx: Index of detected peak
            data: VWC data array
            properties: Peak detection properties
            
        Returns:
            Confidence score (0-1)
        """
        if peak_idx < 5 or peak_idx >= len(data) - 5:
            return 0.0
        
        # Factors for confidence calculation
        factors = []
        
        # 1. Prominence factor (how distinct the peak is)
        if 'prominences' in properties:
            prominence = properties['prominences'][0] if len(properties['prominences']) > 0 else 0
            prominence_factor = min(prominence / self.noise_threshold, 1.0)
            factors.append(prominence_factor * 0.3)
        
        # 2. Local variance factor (stability around peak)
        local_data = data[max(0, peak_idx-5):min(len(data), peak_idx+6)]
        local_std = np.std(local_data)
        variance_factor = max(0, 1 - (local_std / self.noise_threshold))
        factors.append(variance_factor * 0.2)
        
        # 3. Slope consistency factor
        left_slope = data[peak_idx] - data[max(0, peak_idx-3)]
        right_slope = data[min(len(data)-1, peak_idx+3)] - data[peak_idx]
        slope_consistency = 1.0 if (left_slope > 0 and right_slope < 0) else 0.5
        factors.append(slope_consistency * 0.2)
        
        # 4. Amplitude factor (relative to recent data)
        recent_data = data[-min(len(data), 30):]
        amplitude_factor = (data[peak_idx] - np.min(recent_data)) / (np.max(recent_data) - np.min(recent_data) + 0.001)
        factors.append(min(amplitude_factor, 1.0) * 0.3)
        
        return min(sum(factors), 1.0)

    def _analyze_dryback_status(self):
        """Analyze current dryback status based on detected peaks and valleys."""
        if not self.peaks or len(self.vwc_history) < 10:
            return
        
        # Get most recent peak
        recent_peak = max(self.peaks, key=lambda x: x['timestamp']) if self.peaks else None
        current_vwc = self.vwc_history[-1]
        current_time = self.timestamp_history[-1]
        
        if recent_peak:
            # Check if we're in a dryback phase
            time_since_peak = (current_time - recent_peak['timestamp']).total_seconds() / 60  # minutes
            
            # Consider dryback in progress if:
            # 1. Current VWC is lower than peak
            # 2. Time since peak is reasonable (not too old)
            # 3. VWC is declining trend
            if (current_vwc < recent_peak['vwc'] and 
                time_since_peak > 5 and  # At least 5 minutes since peak
                time_since_peak < 480):  # Less than 8 hours since peak
                
                # Calculate dryback percentage
                self.current_dryback = ((recent_peak['vwc'] - current_vwc) / recent_peak['vwc']) * 100
                self.dryback_in_progress = True
                self.last_peak_vwc = recent_peak['vwc']
                self.last_peak_time = recent_peak['timestamp']
                
                if not self.dryback_start_time:
                    self.dryback_start_time = recent_peak['timestamp']
                    
            else:
                self.dryback_in_progress = False
                if self.current_dryback > 0:  # Was in dryback, now ended
                    self.dryback_start_time = None

    def _calculate_confidence_score(self):
        """Calculate overall confidence in current dryback analysis."""
        factors = []
        
        # Data quantity factor
        data_factor = min(len(self.vwc_history) / self.window_size, 1.0)
        factors.append(data_factor * 0.3)
        
        # Peak detection quality
        if self.peaks:
            recent_peaks = [p for p in self.peaks if 
                           (self.timestamp_history[-1] - p['timestamp']).total_seconds() < 3600]
            if recent_peaks:
                avg_peak_confidence = np.mean([p['confidence'] for p in recent_peaks])
                factors.append(avg_peak_confidence * 0.4)
        
        # Data consistency (low noise)
        if len(self.vwc_history) >= 10:
            recent_data = list(self.vwc_history)[-10:]
            noise_level = np.std(recent_data) / np.mean(recent_data) if np.mean(recent_data) > 0 else 1.0
            consistency_factor = max(0, 1 - noise_level)
            factors.append(consistency_factor * 0.3)
        
        self.confidence_score = min(sum(factors), 1.0)

    def _get_status_dict(self) -> Dict:
        """Get current dryback status as dictionary."""
        return {
            'dryback_percentage': round(self.current_dryback, 2),
            'dryback_in_progress': self.dryback_in_progress,
            'last_peak_vwc': self.last_peak_vwc,
            'last_peak_time': self.last_peak_time.isoformat() if self.last_peak_time else None,
            'dryback_start_time': self.dryback_start_time.isoformat() if self.dryback_start_time else None,
            'confidence_score': round(self.confidence_score, 3),
            'peaks_detected': len(self.peaks),
            'valleys_detected': len(self.valleys),
            'data_points': len(self.vwc_history),
            'analysis_window': self.window_size
        }

    def get_dryback_prediction(self, target_percentage: float = None) -> Dict:
        """
        Predict when dryback will reach target percentage.
        
        Args:
            target_percentage: Target dryback percentage to predict
            
        Returns:
            Dictionary with prediction data
        """
        if not self.dryback_in_progress or len(self.vwc_history) < 10:
            return {'prediction_available': False, 'reason': 'No active dryback or insufficient data'}
        
        # Use recent data to calculate dryback rate
        recent_time_window = 30  # Last 30 minutes
        current_time = self.timestamp_history[-1]
        recent_data = []
        
        for i, timestamp in enumerate(self.timestamp_history):
            if (current_time - timestamp).total_seconds() <= recent_time_window * 60:
                recent_data.append({
                    'vwc': self.vwc_history[i],
                    'time': timestamp,
                    'minutes_ago': (current_time - timestamp).total_seconds() / 60
                })
        
        if len(recent_data) < 5:
            return {'prediction_available': False, 'reason': 'Insufficient recent data for trend analysis'}
        
        # Calculate dryback rate (% per minute)
        time_points = [d['minutes_ago'] for d in recent_data]
        vwc_points = [d['vwc'] for d in recent_data]
        
        # Linear regression for trend
        if len(time_points) >= 2:
            slope = np.polyfit(time_points, vwc_points, 1)[0]  # VWC change per minute
            dryback_rate = abs(slope) / self.last_peak_vwc * 100 if self.last_peak_vwc else 0  # % per minute
            
            if target_percentage and dryback_rate > 0:
                remaining_dryback = target_percentage - self.current_dryback
                if remaining_dryback > 0:
                    predicted_minutes = remaining_dryback / dryback_rate
                    predicted_time = current_time + timedelta(minutes=predicted_minutes)
                    
                    return {
                        'prediction_available': True,
                        'predicted_time': predicted_time.isoformat(),
                        'predicted_minutes_remaining': round(predicted_minutes, 1),
                        'current_dryback_rate': round(dryback_rate, 4),
                        'confidence': min(self.confidence_score + 0.2, 1.0)  # Boost confidence for predictions
                    }
        
        return {'prediction_available': False, 'reason': 'Unable to calculate reliable trend'}

    def reset_analysis(self):
        """Reset all analysis data."""
        self.vwc_history.clear()
        self.timestamp_history.clear()
        self.peaks.clear()
        self.valleys.clear()
        self.current_dryback = 0.0
        self.dryback_in_progress = False
        self.last_peak_vwc = None
        self.last_peak_time = None
        self.dryback_start_time = None
        self.confidence_score = 0.0
        
        _LOGGER.info("Advanced Dryback Detector reset")

    def export_analysis_data(self) -> Dict:
        """Export all analysis data for external use/storage."""
        return {
            'vwc_history': list(self.vwc_history),
            'timestamp_history': [t.isoformat() for t in self.timestamp_history],
            'peaks': [
                {
                    'vwc': p['vwc'],
                    'timestamp': p['timestamp'].isoformat(),
                    'confidence': p['confidence']
                } for p in self.peaks
            ],
            'valleys': [
                {
                    'vwc': v['vwc'], 
                    'timestamp': v['timestamp'].isoformat(),
                    'confidence': v['confidence']
                } for v in self.valleys
            ],
            'current_status': self._get_status_dict()
        }