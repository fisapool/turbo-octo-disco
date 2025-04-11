import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import joblib
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedAnalytics:
    def __init__(self):
        self.scaler = StandardScaler()
        self.rf_classifier = RandomForestClassifier(n_estimators=200, random_state=42)
        self.gb_classifier = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.lstm_model = None
        self.model_dir = 'models'
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Initialize models
        self._initialize_models()
        
        # Enhanced risk factor weights with temporal considerations
        self.risk_weights = {
            'posture': {'immediate': 0.20, 'cumulative': 0.15, 'trend': 0.10},
            'activity': {'immediate': 0.15, 'cumulative': 0.15, 'trend': 0.10},
            'stress': {'immediate': 0.15, 'cumulative': 0.10, 'trend': 0.05},
            'focus': {'immediate': 0.10, 'cumulative': 0.05, 'trend': 0.05},
            'breaks': {'immediate': 0.10, 'cumulative': 0.05, 'trend': 0.05}
        }
        
        # Historical risk patterns with temporal thresholds
        self.risk_patterns = {
            'high_risk': {
                'immediate': {
                    'posture_score': 0.3,
                    'activity_level': 0.2,
                    'stress_level': 0.8,
                    'focus_score': 0.4,
                    'break_compliance': 0.3
                },
                'cumulative': {
                    'posture_score': 0.4,
                    'activity_level': 0.3,
                    'stress_level': 0.7,
                    'focus_score': 0.5,
                    'break_compliance': 0.4
                },
                'trend': {
                    'posture_score': 0.5,
                    'activity_level': 0.4,
                    'stress_level': 0.6,
                    'focus_score': 0.6,
                    'break_compliance': 0.5
                }
            },
            'medium_risk': {
                'immediate': {
                    'posture_score': 0.6,
                    'activity_level': 0.5,
                    'stress_level': 0.5,
                    'focus_score': 0.6,
                    'break_compliance': 0.6
                },
                'cumulative': {
                    'posture_score': 0.7,
                    'activity_level': 0.6,
                    'stress_level': 0.4,
                    'focus_score': 0.7,
                    'break_compliance': 0.7
                },
                'trend': {
                    'posture_score': 0.8,
                    'activity_level': 0.7,
                    'stress_level': 0.3,
                    'focus_score': 0.8,
                    'break_compliance': 0.8
                }
            }
        }
        
        # User-specific thresholds and patterns
        self.user_profiles = {}
        
        # Risk factor history for trend analysis
        self.risk_history = {
            'posture': [],
            'activity': [],
            'stress': [],
            'focus': [],
            'breaks': []
        }
    
    def _initialize_models(self):
        """Initialize the machine learning models with baseline data."""
        try:
            # Sample baseline data for initialization
            baseline_data = np.array([
                [0.8, 0.9, 0.7, 0.6, 0.5],  # Good metrics
                [0.7, 0.8, 0.6, 0.5, 0.4],
                [0.6, 0.7, 0.5, 0.4, 0.3],
            ])
            
            # Fit the scaler
            self.scaler.fit(baseline_data)
            
            # Initialize LSTM model
            self._build_lstm_model((24, 5))  # 24 time steps, 5 features
            
            logger.info("Models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            raise
    
    def _build_lstm_model(self, input_shape):
        """Build and compile LSTM model for time series prediction."""
        model = Sequential([
            LSTM(64, input_shape=input_shape, return_sequences=True),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        self.lstm_model = model
        return model
    
    def train_time_series_model(self, data: pd.DataFrame, target_col: str, sequence_length: int = 24):
        """
        Train LSTM model for time series forecasting.
        
        Args:
            data: DataFrame containing time series data
            target_col: Name of the target column to predict
            sequence_length: Number of time steps to use for prediction
        """
        try:
            # Prepare data
            X, y = self._prepare_time_series_data(data, target_col, sequence_length)
            
            # Build and train model
            self.lstm_model = self._build_lstm_model((sequence_length, X.shape[2]))
            
            callbacks = [
                EarlyStopping(monitor='val_loss', patience=5),
                ModelCheckpoint(
                    os.path.join(self.model_dir, 'lstm_model.h5'),
                    save_best_only=True
                )
            ]
            
            history = self.lstm_model.fit(
                X, y,
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                callbacks=callbacks
            )
            
            return history.history
        except Exception as e:
            logger.error(f"Error training time series model: {str(e)}")
            raise
    
    def _prepare_time_series_data(self, data: pd.DataFrame, target_col: str, sequence_length: int):
        """Prepare data for LSTM training."""
        # Scale features
        scaled_data = self.scaler.fit_transform(data)
        
        X, y = [], []
        for i in range(len(data) - sequence_length):
            X.append(scaled_data[i:(i + sequence_length)])
            y.append(scaled_data[i + sequence_length, data.columns.get_loc(target_col)])
        
        return np.array(X), np.array(y)
    
    def predict_health_risk(self, user_data: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """
        Predict personalized health risks using enhanced ensemble methods with temporal analysis.
        
        Args:
            user_data: Dictionary containing user's activity and health metrics
            user_id: Optional user identifier for personalized predictions
            
        Returns:
            Dictionary containing risk predictions, confidence scores, and detailed risk factors
        """
        try:
            # Update user profile if provided
            if user_id:
                self._update_user_profile(user_id, user_data)
            
            # Calculate immediate risk factors
            immediate_risk = self._calculate_immediate_risk(user_data)
            
            # Calculate cumulative risk factors
            cumulative_risk = self._calculate_cumulative_risk(user_data)
            
            # Calculate trend-based risk factors
            trend_risk = self._calculate_trend_risk(user_data)
            
            # Combine risk factors with temporal weights
            overall_risk = self._combine_temporal_risks(
                immediate_risk,
                cumulative_risk,
                trend_risk
            )
            
            # Generate personalized recommendations
            recommendations = self._generate_personalized_recommendations(
                immediate_risk,
                cumulative_risk,
                trend_risk,
                user_id
            )
            
            return {
                'risk_level': overall_risk,
                'confidence': self._calculate_confidence_score(
                    immediate_risk,
                    cumulative_risk,
                    trend_risk
                ),
                'risk_category': self._determine_risk_category(overall_risk),
                'risk_factors': {
                    'immediate': immediate_risk,
                    'cumulative': cumulative_risk,
                    'trend': trend_risk
                },
                'timestamp': datetime.now().isoformat(),
                'recommendations': recommendations,
                'user_specific': user_id is not None
            }
        except Exception as e:
            logger.error(f"Error predicting health risk: {str(e)}")
            raise
    
    def _calculate_immediate_risk(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate immediate risk factors based on current user data."""
        return {
            'posture_risk': 1 - user_data.get('posture_score', 0.5),
            'activity_risk': 1 - user_data.get('activity_level', 0.5),
            'stress_risk': user_data.get('stress_level', 0.5),
            'focus_risk': 1 - user_data.get('focus_score', 0.5),
            'break_risk': 1 - user_data.get('break_compliance', 0.5)
        }
    
    def _calculate_cumulative_risk(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate cumulative risk factors based on historical patterns."""
        # Update risk history
        for factor in self.risk_history:
            self.risk_history[factor].append(user_data.get(factor, 0.5))
            if len(self.risk_history[factor]) > 24:  # Keep last 24 hours
                self.risk_history[factor].pop(0)
        
        return {
            'posture_risk': 1 - np.mean(self.risk_history['posture']),
            'activity_risk': 1 - np.mean(self.risk_history['activity']),
            'stress_risk': np.mean(self.risk_history['stress']),
            'focus_risk': 1 - np.mean(self.risk_history['focus']),
            'break_risk': 1 - np.mean(self.risk_history['breaks'])
        }
    
    def _calculate_trend_risk(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate trend-based risk factors using moving averages."""
        trend_risk = {}
        for factor in self.risk_history:
            if len(self.risk_history[factor]) >= 3:
                # Calculate trend using simple moving average
                ma = np.mean(self.risk_history[factor][-3:])
                trend_risk[f'{factor}_risk'] = abs(ma - user_data.get(factor, 0.5))
            else:
                trend_risk[f'{factor}_risk'] = 0.0
        return trend_risk
    
    def _combine_temporal_risks(self, immediate: Dict[str, float],
                              cumulative: Dict[str, float],
                              trend: Dict[str, float]) -> float:
        """Combine risk factors with temporal weights."""
        combined_risk = 0.0
        
        for factor in immediate:
            factor_risk = (
                self.risk_weights[factor]['immediate'] * immediate[factor] +
                self.risk_weights[factor]['cumulative'] * cumulative[factor] +
                self.risk_weights[factor]['trend'] * trend[f'{factor}_risk']
            )
            combined_risk += factor_risk
        
        return min(1.0, combined_risk)
    
    def _calculate_confidence_score(self, immediate: Dict[str, float],
                                  cumulative: Dict[str, float],
                                  trend: Dict[str, float]) -> float:
        """Calculate confidence score based on data consistency."""
        # Calculate variance in risk factors
        variances = []
        for factor in immediate:
            values = [
                immediate[factor],
                cumulative[factor],
                trend[f'{factor}_risk']
            ]
            variances.append(np.var(values))
        
        # Lower variance indicates higher confidence
        avg_variance = np.mean(variances)
        confidence = 1.0 - min(1.0, avg_variance * 2)
        
        return confidence
    
    def _generate_personalized_recommendations(self, immediate: Dict[str, float],
                                            cumulative: Dict[str, float],
                                            trend: Dict[str, float],
                                            user_id: str = None) -> List[str]:
        """Generate personalized recommendations based on all risk factors."""
        recommendations = []
        
        # Immediate risk recommendations
        if immediate['posture_risk'] > 0.7:
            recommendations.append("Immediate posture adjustment needed")
        if immediate['stress_risk'] > 0.7:
            recommendations.append("High stress detected - take a break now")
        
        # Cumulative risk recommendations
        if cumulative['activity_risk'] > 0.6:
            recommendations.append("Consider increasing daily activity level")
        if cumulative['break_risk'] > 0.6:
            recommendations.append("Improve break schedule compliance")
        
        # Trend-based recommendations
        if trend['posture_risk'] > 0.5:
            recommendations.append("Posture quality declining - review ergonomics")
        if trend['focus_risk'] > 0.5:
            recommendations.append("Focus levels decreasing - consider task rotation")
        
        # User-specific recommendations if available
        if user_id and user_id in self.user_profiles:
            user_profile = self.user_profiles[user_id]
            if user_profile.get('preferred_break_type'):
                recommendations.append(
                    f"Try your preferred break activity: {user_profile['preferred_break_type']}"
                )
        
        return recommendations
    
    def _update_user_profile(self, user_id: str, user_data: Dict[str, Any]):
        """Update or create user profile with personalized thresholds."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'preferred_break_type': None,
                'custom_thresholds': {},
                'risk_history': []
            }
        
        # Update risk history
        self.user_profiles[user_id]['risk_history'].append({
            'timestamp': datetime.now().isoformat(),
            'risk_factors': self._calculate_immediate_risk(user_data)
        })
        
        # Keep last 7 days of history
        if len(self.user_profiles[user_id]['risk_history']) > 168:  # 24 * 7
            self.user_profiles[user_id]['risk_history'].pop(0)
    
    def _determine_risk_category(self, risk_score: float) -> str:
        """Determine risk category based on risk score."""
        if risk_score >= 0.7:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def identify_break_opportunities(self, activity_data: List[Dict[str, Any]], 
                                   min_duration: int = 300,
                                   user_id: str = None) -> List[Dict[str, Any]]:
        """
        Identify optimal break opportunities based on activity patterns, user state, and historical patterns.
        
        Args:
            activity_data: List of activity events
            min_duration: Minimum duration in seconds for a break opportunity
            user_id: Optional user identifier for personalized break scheduling
            
        Returns:
            List of break opportunities with timing, quality scores, and personalized recommendations
        """
        try:
            if not activity_data:
                return []
            
            # Convert activity data to DataFrame
            df = pd.DataFrame(activity_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Calculate advanced activity metrics
            df['activity_score'] = df['activity_level'] * df['attention_level']
            df['rolling_avg'] = df['activity_score'].rolling(window=5).mean()
            df['activity_trend'] = df['activity_score'].diff().rolling(window=3).mean()
            
            # Calculate stress and fatigue indicators
            df['stress_indicator'] = df['stress_level'].rolling(window=3).mean()
            df['fatigue_indicator'] = (1 - df['activity_level']) * df['inactivity_duration']
            df['cognitive_load'] = df['attention_level'] * (1 - df['stress_level'])
            
            # Calculate pattern-based metrics
            df['pattern_score'] = self._calculate_pattern_score(df)
            df['optimal_break_window'] = self._identify_optimal_windows(df)
            
            # Identify potential break points
            break_opportunities = []
            for i in range(1, len(df)):
                time_diff = (df.iloc[i]['timestamp'] - df.iloc[i-1]['timestamp']).total_seconds()
                
                if time_diff >= min_duration:
                    # Calculate comprehensive break quality score
                    quality_score = self._calculate_break_quality(
                        df.iloc[i-1],
                        df.iloc[i],
                        time_diff,
                        user_id
                    )
                    
                    # Generate personalized recommendations
                    recommendations = self._generate_break_recommendations(
                        df.iloc[i-1],
                        quality_score,
                        user_id
                    )
                    
                    # Calculate break type and duration
                    break_type, suggested_duration = self._determine_break_type(
                        df.iloc[i-1],
                        quality_score,
                        user_id
                    )
                    
                    break_opportunities.append({
                        'start_time': df.iloc[i-1]['timestamp'].isoformat(),
                        'end_time': df.iloc[i]['timestamp'].isoformat(),
                        'duration_minutes': int(time_diff / 60),
                        'quality_score': quality_score,
                        'confidence': min(1.0, quality_score * 1.2),
                        'recommendations': recommendations,
                        'break_type': break_type,
                        'suggested_duration': suggested_duration,
                        'activity_before': df.iloc[i-1]['activity_level'],
                        'stress_level': df.iloc[i-1]['stress_level'],
                        'fatigue_level': df.iloc[i-1].get('fatigue_indicator', 0),
                        'cognitive_load': df.iloc[i-1].get('cognitive_load', 0),
                        'pattern_score': df.iloc[i-1].get('pattern_score', 0),
                        'optimal_window': df.iloc[i-1].get('optimal_break_window', False)
                    })
            
            # Sort opportunities by quality score and pattern alignment
            break_opportunities.sort(
                key=lambda x: (
                    x['quality_score'] * 0.7 +
                    x['pattern_score'] * 0.3
                ),
                reverse=True
            )
            
            return break_opportunities
        except Exception as e:
            logger.error(f"Error identifying break opportunities: {str(e)}")
            raise
    
    def _calculate_pattern_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate pattern-based score for break opportunities."""
        # Calculate activity patterns
        activity_pattern = df['activity_score'].rolling(window=24).mean()
        
        # Calculate stress patterns
        stress_pattern = df['stress_level'].rolling(window=24).mean()
        
        # Calculate focus patterns
        focus_pattern = df['attention_level'].rolling(window=24).mean()
        
        # Combine patterns with weights
        pattern_score = (
            0.4 * (1 - activity_pattern) +
            0.3 * (1 - stress_pattern) +
            0.3 * (1 - focus_pattern)
        )
        
        return pattern_score
    
    def _identify_optimal_windows(self, df: pd.DataFrame) -> pd.Series:
        """Identify optimal windows for breaks based on multiple factors."""
        # Calculate time-based windows (e.g., every 90 minutes)
        time_windows = (df['timestamp'].dt.hour * 60 + df['timestamp'].dt.minute) % 90 < 5
        
        # Calculate activity-based windows
        activity_windows = df['activity_score'] < 0.3
        
        # Calculate stress-based windows
        stress_windows = df['stress_level'] > 0.7
        
        # Combine windows
        optimal_windows = time_windows | activity_windows | stress_windows
        
        return optimal_windows
    
    def _calculate_break_quality(self, before_state: pd.Series, 
                               after_state: pd.Series, 
                               duration: float,
                               user_id: str = None) -> float:
        """Calculate comprehensive quality score for a break opportunity."""
        # Base quality factors
        activity_factor = 1 - before_state['activity_level']
        stress_factor = 1 - before_state['stress_level']
        duration_factor = min(1.0, duration / 3600)  # Normalize to 1 hour
        
        # Additional quality factors
        fatigue_factor = 1 - min(1.0, before_state.get('fatigue_indicator', 0))
        focus_factor = 1 - before_state.get('attention_level', 0.5)
        cognitive_factor = 1 - before_state.get('cognitive_load', 0.5)
        pattern_factor = before_state.get('pattern_score', 0.5)
        window_factor = 1.0 if before_state.get('optimal_break_window', False) else 0.5
        
        # User-specific adjustments
        user_factor = 1.0
        if user_id and user_id in self.user_profiles:
            user_profile = self.user_profiles[user_id]
            # Adjust based on user's preferred break times
            if 'preferred_break_times' in user_profile:
                current_hour = before_state['timestamp'].hour
                if current_hour in user_profile['preferred_break_times']:
                    user_factor = 1.2
        
        # Weighted quality score
        quality_score = (
            0.2 * activity_factor +
            0.15 * stress_factor +
            0.15 * duration_factor +
            0.1 * fatigue_factor +
            0.1 * focus_factor +
            0.1 * cognitive_factor +
            0.1 * pattern_factor +
            0.1 * window_factor
        ) * user_factor
        
        return min(1.0, quality_score)
    
    def _determine_break_type(self, state: pd.Series,
                            quality_score: float,
                            user_id: str = None) -> Tuple[str, int]:
        """Determine the most appropriate break type and duration."""
        # Base break types and durations
        if state['stress_level'] > 0.7:
            break_type = "stress_relief"
            duration = 15
        elif state.get('fatigue_indicator', 0) > 0.7:
            break_type = "rest"
            duration = 20
        elif state['activity_level'] > 0.8:
            break_type = "physical"
            duration = 10
        else:
            break_type = "mental"
            duration = 5
        
        # Adjust based on quality score
        if quality_score > 0.8:
            duration = int(duration * 1.5)
        elif quality_score < 0.4:
            duration = int(duration * 0.8)
        
        # User-specific adjustments
        if user_id and user_id in self.user_profiles:
            user_profile = self.user_profiles[user_id]
            if 'preferred_break_duration' in user_profile:
                duration = user_profile['preferred_break_duration'].get(break_type, duration)
        
        return break_type, duration
    
    def _generate_break_recommendations(self, state: pd.Series, 
                                      quality_score: float,
                                      user_id: str = None) -> List[str]:
        """Generate personalized break recommendations based on user state and history."""
        recommendations = []
        
        # Activity-based recommendations
        if state['activity_level'] > 0.8:
            recommendations.append("Take a short walk to reduce physical strain")
            recommendations.append("Do some light stretching exercises")
        
        # Stress-based recommendations
        if state['stress_level'] > 0.7:
            recommendations.append("Practice deep breathing exercises")
            recommendations.append("Try a short meditation session")
        
        # Fatigue-based recommendations
        if state.get('fatigue_indicator', 0) > 0.7:
            recommendations.append("Consider a power nap if possible")
            recommendations.append("Take a short walk outside")
        
        # Focus-based recommendations
        if state.get('attention_level', 0.5) < 0.3:
            recommendations.append("Step away from the screen for a few minutes")
            recommendations.append("Do a quick mindfulness exercise")
        
        # Cognitive load recommendations
        if state.get('cognitive_load', 0.5) > 0.7:
            recommendations.append("Take a mental break - no screens")
            recommendations.append("Try a brief relaxation technique")
        
        # User-specific recommendations
        if user_id and user_id in self.user_profiles:
            user_profile = self.user_profiles[user_id]
            if 'preferred_break_activities' in user_profile:
                recommendations.extend(user_profile['preferred_break_activities'])
        
        # Duration-based recommendations
        if quality_score > 0.8:
            recommendations.append("This is an excellent time for a longer break")
            recommendations.append("Consider a complete change of environment")
        elif quality_score > 0.6:
            recommendations.append("Consider a short break now")
            recommendations.append("Try a quick refreshment activity")
        
        return recommendations
    
    def analyze_focus_time(self, activity_data: List[Dict[str, Any]], 
                          window_size: int = 15) -> Dict[str, Any]:
        """
        Analyze focus time patterns and provide insights.
        
        Args:
            activity_data: List of activity events
            window_size: Size of the analysis window in minutes
            
        Returns:
            Dictionary containing focus time analysis results
        """
        try:
            if not activity_data:
                return {}
            
            # Convert activity data to DataFrame
            df = pd.DataFrame(activity_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Calculate focus metrics
            df['focus_score'] = df['activity_level'] * df['attention_level']
            df['rolling_focus'] = df['focus_score'].rolling(
                window=window_size,
                min_periods=1
            ).mean()
            
            # Identify focus periods
            focus_periods = []
            current_period = None
            
            for idx, row in df.iterrows():
                if row['rolling_focus'] >= 0.7:  # High focus threshold
                    if current_period is None:
                        current_period = {
                            'start_time': row['timestamp'],
                            'end_time': row['timestamp'],
                            'avg_focus': row['rolling_focus']
                        }
                    else:
                        current_period['end_time'] = row['timestamp']
                        current_period['avg_focus'] = (
                            current_period['avg_focus'] + row['rolling_focus']
                        ) / 2
                elif current_period is not None:
                    duration = (
                        current_period['end_time'] - current_period['start_time']
                    ).total_seconds() / 60
                    
                    if duration >= 5:  # Minimum 5 minutes for a focus period
                        focus_periods.append({
                            'start_time': current_period['start_time'].isoformat(),
                            'end_time': current_period['end_time'].isoformat(),
                            'duration_minutes': duration,
                            'focus_score': current_period['avg_focus']
                        })
                    current_period = None
            
            # Calculate overall metrics
            total_time = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 60
            focus_time = sum(p['duration_minutes'] for p in focus_periods)
            
            return {
                'total_time_minutes': total_time,
                'focus_time_minutes': focus_time,
                'focus_percentage': (focus_time / total_time) * 100 if total_time > 0 else 0,
                'focus_periods': focus_periods,
                'avg_focus_score': df['focus_score'].mean(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error analyzing focus time: {str(e)}")
            raise
    
    def save_models(self):
        """Save trained models to disk."""
        try:
            if self.lstm_model:
                self.lstm_model.save(os.path.join(self.model_dir, 'lstm_model.h5'))
            logger.info("Models saved successfully")
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            raise 