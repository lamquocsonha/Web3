"""
Strategy Class
Parses JSON strategy files and generates trading signals
"""

import json
import numpy as np
from typing import Dict, List, Optional, Any
from .indicators import calculate_indicator
from .dynamic_exit import DynamicExitManager


class Strategy:
    """
    Trading Strategy Manager
    Loads, validates, and executes strategies from JSON
    """
    
    def __init__(self, strategy_json: Dict = None, strategy_file: str = None):
        """
        Initialize strategy from JSON dict or file
        
        Args:
            strategy_json: Strategy as dictionary
            strategy_file: Path to JSON strategy file
        """
        if strategy_file:
            with open(strategy_file, 'r') as f:
                self.config = json.load(f)
        elif strategy_json:
            self.config = strategy_json
        else:
            self.config = self._default_strategy()
        
        self._validate_strategy()
        self._init_components()
    
    def _default_strategy(self) -> Dict:
        """Default strategy template with multi-timeframe support"""
        return {
            "name": "Default Strategy",
            "version": "1.0",
            "description": "Basic EMA crossover strategy with multi-timeframe support",

            "indicators": [
                {
                    "id": "ema_fast",
                    "type": "EMA",
                    "params": {"period": 5}
                    # Optional: "timeframe": "5m" to calculate on different timeframe
                },
                {
                    "id": "ema_slow",
                    "type": "EMA",
                    "params": {"period": 19}
                }
                # Example multi-timeframe indicator:
                # {
                #     "id": "ema_20_1H",
                #     "type": "EMA",
                #     "params": {"period": 20},
                #     "timeframe": "1H"  # Calculate EMA on 1H data, expand to current timeframe
                # }
            ],
            
            "entry_conditions": {
                "long": [
                    {
                        "condition": "ema_fast > ema_slow",
                        "logic": "AND"
                    },
                    {
                        "condition": "close > ema_slow"
                    }
                ],
                "short": [
                    {
                        "condition": "ema_fast < ema_slow",
                        "logic": "AND"
                    },
                    {
                        "condition": "close < ema_slow"
                    }
                ]
            },
            
            "exit_rules": {
                "dynamic_tp_sl": True,
                "tp_sl_table": [],  # Use default from DynamicExitManager
                "time_exit": None
            },
            
            "settings": {
                "trading_hours": {
                    "start": "09:00",
                    "end": "14:30"
                },
                "base_time": "09:00",  # Time to capture base price
                "expiry_days": [],  # List of expiry dates (e.g., [20])
                "exit_on_expiry": False,
                "expiry_exit_time": "14:25",
                "exclude_entry_times": [],  # List of times in HHMMSS format
                "exclude_exit_times": [],   # List of times in HHMMSS format
                "candle_length_limit": 20.0  # Max candle range for HHV/LLV updates
            },
            
            "risk_management": {
                "position_size_pct": 10,
                "max_positions": 1,
                "max_daily_loss": 50
            }
        }
    
    def _validate_strategy(self):
        """Validate strategy configuration"""
        required_keys = ["name", "indicators", "entry_conditions", "exit_rules", "risk_management"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required key: {key}")
        
        # Validate indicators
        for ind in self.config["indicators"]:
            if "id" not in ind or "type" not in ind:
                raise ValueError("Indicator must have 'id' and 'type'")
        
        print(f"✅ Strategy '{self.config['name']}' validated")
    
    def _init_components(self):
        """Initialize strategy components"""
        # Initialize exit manager
        tp_sl_rules = self.config["exit_rules"].get("tp_sl_table", [])
        self.exit_manager = DynamicExitManager(tp_sl_rules if tp_sl_rules else None)
        
        # Cache for calculated indicators
        self.indicator_cache = {}
    
    def calculate_indicators(self, data: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Calculate all indicators defined in strategy with multi-timeframe support

        Args:
            data: Dict with OHLCV data as numpy arrays
                  Must include 'times' key if using multi-timeframe indicators

        Returns:
            Dict with indicator_id -> values

        Example indicator config with timeframe:
            {
                "id": "ema_5_1H",
                "type": "EMA",
                "params": {"period": 5},
                "timeframe": "1H"  # Optional: calculate on different timeframe
            }
        """
        self.indicator_cache = {}

        for indicator in self.config["indicators"]:
            ind_id = indicator["id"]
            ind_type = indicator["type"]
            params = indicator.get("params", {})
            timeframe = indicator.get("timeframe", None)  # Optional timeframe parameter

            try:
                # Pass timeframe to calculate_indicator for multi-timeframe support
                result = calculate_indicator(ind_type, data, params, timeframe)
                self.indicator_cache[ind_id] = result

                if timeframe:
                    print(f"  ✓ {ind_id} ({ind_type} on {timeframe}) calculated")
                else:
                    print(f"  ✓ {ind_id} ({ind_type}) calculated")
            except Exception as e:
                print(f"  ✗ Error calculating {ind_id}: {e}")
                self.indicator_cache[ind_id] = None

        return self.indicator_cache
    
    def evaluate_condition(self, condition: str, bar_index: int, data: Dict, left_offset: int = 0, right_offset: int = 0) -> bool:
        """
        Evaluate a single condition string
        
        Args:
            condition: Condition string like "ema_fast > ema_slow" or "close cross_above ema_5"
            bar_index: Current bar index
            data: OHLCV data dict
            left_offset: Offset for left operand (lookback bars)
            right_offset: Offset for right operand (lookback bars)
        
        Returns:
            Boolean result
        """
        try:
            # Handle cross_above and cross_below operators
            if 'cross_above' in condition or 'cross_below' in condition:
                parts = condition.split()
                if len(parts) != 3:
                    return False
                
                left_key = parts[0]
                operator = parts[1]
                right_key = parts[2]
                
                # Get current and previous values
                left_curr = self._get_value(left_key, bar_index - left_offset, data)
                left_prev = self._get_value(left_key, bar_index - left_offset - 1, data)
                right_curr = self._get_value(right_key, bar_index - right_offset, data)
                right_prev = self._get_value(right_key, bar_index - right_offset - 1, data)
                
                if operator == 'cross_above':
                    return left_prev <= right_prev and left_curr > right_curr
                elif operator == 'cross_below':
                    return left_prev >= right_prev and left_curr < right_curr
                
                return False
            
            # Replace indicator IDs with actual values
            eval_str = condition
            
            # Replace OHLC references
            for key in ['open', 'high', 'low', 'close', 'volume']:
                if key in eval_str:
                    eval_str = eval_str.replace(key, f"data['{key}'][{bar_index}]")
            
            # Replace indicator references
            for ind_id, ind_values in self.indicator_cache.items():
                if ind_id in eval_str:
                    if isinstance(ind_values, tuple):
                        # Handle multiple outputs (e.g., MACD returns 3 arrays)
                        # For simplicity, use first output
                        value = ind_values[0][bar_index]
                    elif isinstance(ind_values, dict):
                        # Handle dict outputs (e.g., Pivot Points)
                        # Can't directly evaluate, skip for now
                        continue
                    else:
                        value = ind_values[bar_index]
                    
                    eval_str = eval_str.replace(ind_id, str(value))
            
            # Handle time conditions (e.g., "time >= 09:00")
            if 'time' in eval_str:
                # Simplified: assume time is available in data
                if 'time' in data:
                    current_time = data['time'][bar_index]
                    eval_str = eval_str.replace('time', str(current_time))
            
            # Evaluate the expression
            result = eval(eval_str)
            return bool(result)
            
        except Exception as e:
            print(f"  ✗ Error evaluating condition '{condition}': {e}")
            return False
    
    def _get_value(self, key: str, bar_index: int, data: Dict) -> float:
        """Get value for a key at given bar index"""
        if bar_index < 0:
            return 0.0
        
        # Check if it's OHLCV data
        if key in ['open', 'high', 'low', 'close', 'volume']:
            return data[key][bar_index]
        
        # Check if it's an indicator
        if key in self.indicator_cache:
            ind_values = self.indicator_cache[key]
            if isinstance(ind_values, tuple):
                return ind_values[0][bar_index]
            elif isinstance(ind_values, dict):
                return 0.0
            else:
                return ind_values[bar_index]
        
        return 0.0
    
    def generate_signals(self, data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Generate buy/short signals based on strategy conditions
        
        Args:
            data: Dict with OHLCV data
        
        Returns:
            Dict with 'buy' and 'short' signal arrays (boolean)
        """
        print(f"\n📊 Generating signals for '{self.config['name']}'...")
        
        # Calculate indicators
        self.calculate_indicators(data)
        
        n_bars = len(data['close'])
        buy_signals = np.zeros(n_bars, dtype=bool)
        short_signals = np.zeros(n_bars, dtype=bool)
        
        # Get trading hours
        trading_hours = self.config["risk_management"].get("trading_hours", {})
        start_time = trading_hours.get("start")
        end_time = trading_hours.get("end")
        
        # Evaluate conditions for each bar
        for i in range(1, n_bars):  # Start from 1 to avoid lookback issues
            # Check trading hours
            in_trading_hours = True
            if 'time' in data and start_time and end_time:
                current_time = data['time'][i]
                # Simplified time check (assumes time is in format like "09:30")
                in_trading_hours = start_time <= str(current_time) <= end_time
            
            if not in_trading_hours:
                continue
            
            # Evaluate long conditions
            long_conditions_met = False
            for cond_group in self.config["entry_conditions"]["long"]:
                # Handle nested conditions format from UI
                if "conditions" in cond_group:
                    group_met = True
                    for cond in cond_group["conditions"]:
                        # Build condition string from object
                        left = cond["left"]
                        operator = cond["operator"]
                        right = cond["right"]
                        left_offset = cond.get("leftOffset", 0)
                        right_offset = cond.get("rightOffset", 0)
                        
                        # Build condition string
                        condition_str = f"{left} {operator} {right}"
                        result = self.evaluate_condition(condition_str, i, data, left_offset, right_offset)
                        
                        logic = cond.get("logic", "AND")
                        if logic == "AND":
                            group_met = group_met and result
                        else:  # OR
                            group_met = group_met or result
                    
                    # OR logic between different signal groups
                    long_conditions_met = long_conditions_met or group_met
                # Handle simple condition format (backward compatibility)
                elif "condition" in cond_group:
                    condition_str = cond_group["condition"]
                    result = self.evaluate_condition(condition_str, i, data, 0, 0)
                    
                    logic = cond_group.get("logic", "AND")
                    if logic == "AND":
                        long_conditions_met = long_conditions_met and result
                    else:  # OR
                        long_conditions_met = long_conditions_met or result
            
            buy_signals[i] = long_conditions_met
            
            # Evaluate short conditions
            short_conditions_met = False
            for cond_group in self.config["entry_conditions"]["short"]:
                # Handle nested conditions format from UI
                if "conditions" in cond_group:
                    group_met = True
                    for cond in cond_group["conditions"]:
                        # Build condition string from object
                        left = cond["left"]
                        operator = cond["operator"]
                        right = cond["right"]
                        left_offset = cond.get("leftOffset", 0)
                        right_offset = cond.get("rightOffset", 0)
                        
                        # Build condition string
                        condition_str = f"{left} {operator} {right}"
                        result = self.evaluate_condition(condition_str, i, data, left_offset, right_offset)
                        
                        logic = cond.get("logic", "AND")
                        if logic == "AND":
                            group_met = group_met and result
                        else:  # OR
                            group_met = group_met or result
                    
                    # OR logic between different signal groups
                    short_conditions_met = short_conditions_met or group_met
                # Handle simple condition format (backward compatibility)
                elif "condition" in cond_group:
                    condition_str = cond_group["condition"]
                    result = self.evaluate_condition(condition_str, i, data, 0, 0)
                    
                    logic = cond_group.get("logic", "AND")
                    if logic == "AND":
                        short_conditions_met = short_conditions_met and result
                    else:  # OR
                        short_conditions_met = short_conditions_met or result
            
            short_signals[i] = short_conditions_met
        
        print(f"  ✅ Generated {np.sum(buy_signals)} buy signals, {np.sum(short_signals)} short signals")
        
        return {
            'buy': buy_signals,
            'short': short_signals
        }
    
    def get_exit_manager(self) -> DynamicExitManager:
        """Get exit manager instance"""
        return self.exit_manager
    
    def save(self, filepath: str):
        """Save strategy to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"💾 Strategy saved to {filepath}")
    
    def export_config(self) -> Dict:
        """Export strategy configuration"""
        return self.config
    
    @staticmethod
    def load(filepath: str) -> 'Strategy':
        """Load strategy from JSON file"""
        return Strategy(strategy_file=filepath)
    
    @staticmethod
    def create_from_dict(config: Dict) -> 'Strategy':
        """Create strategy from dictionary"""
        return Strategy(strategy_json=config)
    
    # ==================== NEW RULE CHECKING METHODS ====================
    
    def is_within_trading_hours(self, current_time: str) -> bool:
        """
        Check if current time is within trading hours
        
        Args:
            current_time: Time string in HH:MM format
        
        Returns:
            bool: True if within trading hours
        """
        settings = self.config.get("settings", {})
        trading_hours = settings.get("trading_hours", {})
        start_time = trading_hours.get("start", "09:00")
        end_time = trading_hours.get("end", "14:30")
        
        return start_time <= current_time <= end_time
    
    def is_expiry_day(self, current_date: int) -> bool:
        """
        Check if current day is expiry day
        
        Args:
            current_date: Day of month (1-31)
        
        Returns:
            bool: True if expiry day
        """
        settings = self.config.get("settings", {})
        expiry_days = settings.get("expiry_days", [])
        return current_date in expiry_days
    
    def should_exit_on_expiry(self, current_time: str, current_date: int) -> bool:
        """
        Check if should exit due to expiry day
        
        Args:
            current_time: Time string in HH:MM format
            current_date: Day of month (1-31)
        
        Returns:
            bool: True if should exit
        """
        settings = self.config.get("settings", {})
        
        if not settings.get("exit_on_expiry", False):
            return False
        
        if not self.is_expiry_day(current_date):
            return False
        
        expiry_exit_time = settings.get("expiry_exit_time", "14:25")
        return current_time >= expiry_exit_time
    
    def is_excluded_entry_time(self, current_time: str) -> bool:
        """
        Check if entry is excluded at current time
        
        Args:
            current_time: Time string in HHMMSS format
        
        Returns:
            bool: True if entry excluded
        """
        settings = self.config.get("settings", {})
        exclude_times = settings.get("exclude_entry_times", [])
        
        # Convert HH:MM:SS to HHMMSS for comparison
        time_hhmmss = current_time.replace(":", "")
        return time_hhmmss in exclude_times
    
    def is_excluded_exit_time(self, current_time: str) -> bool:
        """
        Check if exit is excluded at current time
        
        Args:
            current_time: Time string in HHMMSS format
        
        Returns:
            bool: True if exit excluded
        """
        settings = self.config.get("settings", {})
        exclude_times = settings.get("exclude_exit_times", [])
        
        # Convert HH:MM:SS to HHMMSS for comparison
        time_hhmmss = current_time.replace(":", "")
        return time_hhmmss in exclude_times
    
    def should_update_trailing(self, candle_high: float, candle_low: float) -> bool:
        """
        Check if should update HHV/LLV for trailing stop
        
        Args:
            candle_high: Current candle high
            candle_low: Current candle low
        
        Returns:
            bool: True if should update (candle not too long)
        """
        settings = self.config.get("settings", {})
        candle_length_limit = settings.get("candle_length_limit", 20.0)
        
        candle_range = candle_high - candle_low
        return candle_range <= candle_length_limit


# ==================== STRATEGY BUILDER HELPERS ====================

class StrategyBuilder:
    """Helper class to build strategies programmatically"""
    
    def __init__(self, name: str, description: str = ""):
        self.config = {
            "name": name,
            "version": "1.0",
            "description": description,
            "indicators": [],
            "entry_conditions": {
                "long": [],
                "short": []
            },
            "exit_rules": {
                "dynamic_tp_sl": True,
                "tp_sl_table": [],
                "time_exit": None
            },
            "risk_management": {
                "position_size_pct": 10,
                "max_positions": 1,
                "max_daily_loss": 50,
                "trading_hours": {
                    "start": "09:00",
                    "end": "14:30"
                }
            }
        }
    
    def add_indicator(self, ind_id: str, ind_type: str, params: Dict) -> 'StrategyBuilder':
        """Add indicator to strategy"""
        self.config["indicators"].append({
            "id": ind_id,
            "type": ind_type,
            "params": params
        })
        return self
    
    def add_long_condition(self, condition: str, logic: str = "AND") -> 'StrategyBuilder':
        """Add long entry condition"""
        self.config["entry_conditions"]["long"].append({
            "condition": condition,
            "logic": logic
        })
        return self
    
    def add_short_condition(self, condition: str, logic: str = "AND") -> 'StrategyBuilder':
        """Add short entry condition"""
        self.config["entry_conditions"]["short"].append({
            "condition": condition,
            "logic": logic
        })
        return self
    
    def set_exit_rules(self, tp_sl_table: List[Dict], time_exit: str = None) -> 'StrategyBuilder':
        """Set exit rules"""
        self.config["exit_rules"]["tp_sl_table"] = tp_sl_table
        self.config["exit_rules"]["time_exit"] = time_exit
        return self
    
    def set_risk_management(self, position_size_pct: float = 10, 
                           max_positions: int = 1,
                           max_daily_loss: float = 50) -> 'StrategyBuilder':
        """Set risk management parameters"""
        self.config["risk_management"]["position_size_pct"] = position_size_pct
        self.config["risk_management"]["max_positions"] = max_positions
        self.config["risk_management"]["max_daily_loss"] = max_daily_loss
        return self
    
    def build(self) -> Strategy:
        """Build and return Strategy instance"""
        return Strategy(strategy_json=self.config)
    
    def export_json(self) -> Dict:
        """Export configuration as dict"""
        return self.config
