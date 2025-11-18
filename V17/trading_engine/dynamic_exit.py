"""
Dynamic Exit Manager
Manages Take Profit, Stop Loss, and Trailing Stop based on profit progression
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


class DynamicExitManager:
    """
    Dynamic TP/SL/Trailing Stop Manager
    Adjusts exit levels based on current profit
    """
    
    def __init__(self, tp_sl_rules: List[Dict] = None):
        """
        Initialize with TP/SL rules table
        
        Args:
            tp_sl_rules: List of dicts with profit_range, tp, sl, trailing
                Example: [
                    {"profit_range": [0, 2], "tp": 5, "sl": 3, "trailing": 2},
                    {"profit_range": [2, 4], "tp": 8, "sl": 2, "trailing": 3},
                    ...
                ]
        """
        self.tp_sl_rules = tp_sl_rules or self._default_rules()
        
    def _default_rules(self) -> List[Dict]:
        """Default TP/SL/Trailing rules based on AFL logic"""
        return [
            {"profit_range": [0, 2], "tp": 5, "sl": 10.3, "trailing": 11.9},
            {"profit_range": [2, 4], "tp": 8, "sl": 10.8, "trailing": 13.9},
            {"profit_range": [4, 6], "tp": 10, "sl": 5.5, "trailing": 9.8},
            {"profit_range": [6, 8], "tp": 12, "sl": 4, "trailing": 10.1},
            {"profit_range": [8, 10], "tp": 15, "sl": 1.2, "trailing": 9.5},
            {"profit_range": [10, 12], "tp": 18, "sl": 1, "trailing": 12},
            {"profit_range": [12, 14], "tp": 20, "sl": 10, "trailing": 10.1},
            {"profit_range": [14, 16], "tp": 25, "sl": 10, "trailing": 8.2},
            {"profit_range": [16, 20], "tp": 30, "sl": 10, "trailing": None},  # Use percentage
            {"profit_range": [20, 30], "tp": None, "sl": 10, "trailing": None},
            {"profit_range": [30, 50], "tp": None, "sl": 5, "trailing": None},
            {"profit_range": [50, float('inf')], "tp": None, "sl": 3, "trailing": None}
        ]
    
    def get_exit_levels(self, 
                       entry_price: float,
                       current_price: float,
                       direction: str,
                       highest_profit: float = 0) -> Dict[str, Optional[float]]:
        """
        Calculate TP/SL/Trailing levels based on current profit
        
        Args:
            entry_price: Entry price of position
            current_price: Current market price
            direction: 'long' or 'short'
            highest_profit: Highest profit achieved (for trailing)
        
        Returns:
            Dict with 'tp', 'sl', 'trailing' prices
        """
        # Calculate current profit
        if direction == 'long':
            profit = current_price - entry_price
        else:  # short
            profit = entry_price - current_price
        
        # Use highest profit for determining rules
        max_profit = max(profit, highest_profit)
        
        # Find matching rule
        rule = self._find_rule(max_profit)
        
        if not rule:
            return {'tp': None, 'sl': None, 'trailing': None}
        
        # Calculate levels
        if direction == 'long':
            tp = entry_price + rule['tp'] if rule['tp'] else None
            sl = entry_price - rule['sl'] if rule['sl'] else None
            
            # Trailing stop based on highest profit
            if rule['trailing']:
                if rule['trailing'] == 'percentage':
                    # Use percentage of profit
                    trailing = current_price - (max_profit * 0.68)
                else:
                    trailing = current_price - rule['trailing']
            else:
                trailing = None
                
        else:  # short
            tp = entry_price - rule['tp'] if rule['tp'] else None
            sl = entry_price + rule['sl'] if rule['sl'] else None
            
            # Trailing stop
            if rule['trailing']:
                if rule['trailing'] == 'percentage':
                    trailing = current_price + (max_profit * 0.68)
                else:
                    trailing = current_price + rule['trailing']
            else:
                trailing = None
        
        return {
            'tp': tp,
            'sl': sl,
            'trailing': trailing,
            'rule_applied': rule
        }
    
    def _find_rule(self, profit: float) -> Optional[Dict]:
        """Find matching rule for profit level"""
        for rule in self.tp_sl_rules:
            min_profit, max_profit = rule['profit_range']
            if min_profit <= profit < max_profit:
                return rule
        return None
    
    def should_exit(self,
                   entry_price: float,
                   current_high: float,
                   current_low: float,
                   direction: str,
                   highest_profit: float) -> Tuple[bool, str]:
        """
        Check if position should exit
        
        Args:
            entry_price: Entry price
            current_high: Current bar high
            current_low: Current bar low
            direction: 'long' or 'short'
            highest_profit: Highest profit achieved
        
        Returns:
            (should_exit, reason)
        """
        current_price = (current_high + current_low) / 2
        levels = self.get_exit_levels(entry_price, current_price, direction, highest_profit)
        
        if direction == 'long':
            # Check stop loss
            if levels['sl'] and current_low <= levels['sl']:
                return True, 'stop_loss'
            
            # Check trailing stop
            if levels['trailing'] and current_low <= levels['trailing']:
                return True, 'trailing_stop'
            
            # Check take profit
            if levels['tp'] and current_high >= levels['tp']:
                return True, 'take_profit'
                
        else:  # short
            # Check stop loss
            if levels['sl'] and current_high >= levels['sl']:
                return True, 'stop_loss'
            
            # Check trailing stop
            if levels['trailing'] and current_high >= levels['trailing']:
                return True, 'trailing_stop'
            
            # Check take profit
            if levels['tp'] and current_low <= levels['tp']:
                return True, 'take_profit'
        
        return False, None
    
    def update_rules(self, new_rules: List[Dict]):
        """Update TP/SL rules"""
        self.tp_sl_rules = new_rules
    
    def export_rules(self) -> List[Dict]:
        """Export current rules"""
        return self.tp_sl_rules
    
    @staticmethod
    def create_from_json(rules_json: List[Dict]) -> 'DynamicExitManager':
        """Create manager from JSON rules"""
        return DynamicExitManager(rules_json)


class Position:
    """Position tracking with dynamic exit management"""
    
    def __init__(self, 
                 entry_price: float,
                 direction: str,
                 size: float,
                 exit_manager: DynamicExitManager):
        """
        Initialize position
        
        Args:
            entry_price: Entry price
            direction: 'long' or 'short'
            size: Position size
            exit_manager: DynamicExitManager instance
        """
        self.entry_price = entry_price
        self.direction = direction
        self.size = size
        self.exit_manager = exit_manager
        
        self.highest_profit = 0
        self.lowest_drawdown = 0
        
        self.entry_time = None
        self.exit_time = None
        self.exit_price = None
        self.exit_reason = None
        
    def update(self, current_high: float, current_low: float) -> Tuple[bool, str]:
        """
        Update position and check for exit
        
        Args:
            current_high: Current bar high
            current_low: Current bar low
        
        Returns:
            (should_exit, exit_reason)
        """
        current_price = (current_high + current_low) / 2
        
        # Calculate current profit
        if self.direction == 'long':
            profit = current_price - self.entry_price
        else:
            profit = self.entry_price - current_price
        
        # Update highest profit
        self.highest_profit = max(self.highest_profit, profit)
        self.lowest_drawdown = min(self.lowest_drawdown, profit)
        
        # Check exit conditions
        should_exit, reason = self.exit_manager.should_exit(
            self.entry_price,
            current_high,
            current_low,
            self.direction,
            self.highest_profit
        )
        
        return should_exit, reason
    
    def get_current_profit(self, current_price: float) -> float:
        """Calculate current profit"""
        if self.direction == 'long':
            return current_price - self.entry_price
        else:
            return self.entry_price - current_price
    
    def get_exit_levels(self, current_price: float) -> Dict:
        """Get current TP/SL/Trailing levels"""
        return self.exit_manager.get_exit_levels(
            self.entry_price,
            current_price,
            self.direction,
            self.highest_profit
        )
    
    def close(self, exit_price: float, exit_reason: str):
        """Close position"""
        self.exit_price = exit_price
        self.exit_reason = exit_reason
        
    def get_stats(self) -> Dict:
        """Get position statistics"""
        if not self.exit_price:
            return None
        
        profit = self.get_current_profit(self.exit_price)
        
        return {
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'direction': self.direction,
            'profit': profit,
            'highest_profit': self.highest_profit,
            'exit_reason': self.exit_reason,
            'size': self.size
        }
