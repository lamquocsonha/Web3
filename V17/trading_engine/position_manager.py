"""
Position Manager
Manages positions with AFL-style logic: entry, tracking, dynamic TP/SL, exit
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .dynamic_exit import DynamicExitManager, Position


class PositionManager:
    """
    Manages trading positions with AFL-compatible logic
    - Entry signal validation
    - Position tracking (one position at a time)
    - Dynamic TP/SL/Trailing management
    - Exit signal generation
    """
    
    def __init__(self, 
                 max_positions: int = 1,
                 buy_order_limit: int = 10,
                 short_order_limit: int = 10,
                 exit_manager: DynamicExitManager = None):
        """
        Initialize Position Manager
        
        Args:
            max_positions: Maximum concurrent positions (AFL default: 1)
            buy_order_limit: Max buy orders in a session
            short_order_limit: Max short orders in a session
            exit_manager: DynamicExitManager instance
        """
        self.max_positions = max_positions
        self.buy_order_limit = buy_order_limit
        self.short_order_limit = short_order_limit
        self.exit_manager = exit_manager or DynamicExitManager()
        
        # Position state
        self.current_position: Optional[Position] = None
        self.position_history: List[Dict] = []
        
        # Order counters (reset daily in AFL)
        self.buy_order_count = 0
        self.short_order_count = 0
        
        # Tracking variables
        self.hhv_since_buy = None  # Highest high since buy
        self.llv_since_short = None  # Lowest low since short
        
    def reset_daily_counters(self):
        """Reset daily order limits (call at start of new trading day)"""
        self.buy_order_count = 0
        self.short_order_count = 0
    
    def can_enter_long(self) -> bool:
        """Check if can enter long position"""
        return (self.current_position is None and 
                self.buy_order_count < self.buy_order_limit)
    
    def can_enter_short(self) -> bool:
        """Check if can enter short position"""
        return (self.current_position is None and 
                self.short_order_count < self.short_order_limit)
    
    def enter_long(self, 
                   bar_index: int,
                   entry_price: float,
                   size: float,
                   time: Optional[datetime] = None) -> bool:
        """
        Enter long position
        
        Args:
            bar_index: Current bar index
            entry_price: Entry price
            size: Position size
            time: Entry timestamp
        
        Returns:
            True if entered, False if cannot enter
        """
        if not self.can_enter_long():
            return False
        
        self.current_position = Position(
            entry_price=entry_price,
            direction='long',
            size=size,
            exit_manager=self.exit_manager
        )
        self.current_position.entry_time = time
        self.current_position.entry_bar = bar_index
        
        # Initialize tracking
        self.hhv_since_buy = entry_price
        
        self.buy_order_count += 1
        
        print(f"  📈 LONG @ {entry_price:.2f} | Size: {size:.2f} | Bar: {bar_index}")
        return True
    
    def enter_short(self,
                    bar_index: int,
                    entry_price: float,
                    size: float,
                    time: Optional[datetime] = None) -> bool:
        """
        Enter short position
        
        Args:
            bar_index: Current bar index
            entry_price: Entry price
            size: Position size
            time: Entry timestamp
        
        Returns:
            True if entered, False if cannot enter
        """
        if not self.can_enter_short():
            return False
        
        self.current_position = Position(
            entry_price=entry_price,
            direction='short',
            size=size,
            exit_manager=self.exit_manager
        )
        self.current_position.entry_time = time
        self.current_position.entry_bar = bar_index
        
        # Initialize tracking
        self.llv_since_short = entry_price
        
        self.short_order_count += 1
        
        print(f"  📉 SHORT @ {entry_price:.2f} | Size: {size:.2f} | Bar: {bar_index}")
        return True
    
    def update_position(self,
                       bar_index: int,
                       high: float,
                       low: float,
                       close: float,
                       time: Optional[datetime] = None) -> Tuple[bool, Optional[str]]:
        """
        Update position and check for exit
        
        Args:
            bar_index: Current bar index
            high: Current bar high
            low: Current bar low
            close: Current bar close
            time: Current timestamp
        
        Returns:
            (should_exit, exit_reason)
        """
        if not self.current_position:
            return False, None
        
        # Update HHV/LLV tracking
        if self.current_position.direction == 'long':
            self.hhv_since_buy = max(self.hhv_since_buy, high)
        else:  # short
            self.llv_since_short = min(self.llv_since_short, low)
        
        # Update position profit tracking
        should_exit, exit_reason = self.current_position.update(high, low)
        
        return should_exit, exit_reason
    
    def exit_position(self,
                     bar_index: int,
                     exit_price: float,
                     exit_reason: str,
                     time: Optional[datetime] = None) -> Optional[Dict]:
        """
        Exit current position
        
        Args:
            bar_index: Current bar index
            exit_price: Exit price
            exit_reason: Reason for exit (stop_loss, take_profit, trailing_stop, etc)
            time: Exit timestamp
        
        Returns:
            Position statistics dict
        """
        if not self.current_position:
            return None
        
        self.current_position.close(exit_price, exit_reason)
        self.current_position.exit_time = time
        self.current_position.exit_bar = bar_index
        
        # Calculate profit
        profit = self.current_position.get_current_profit(exit_price)
        profit_pct = (profit / self.current_position.entry_price) * 100
        
        # Get position stats
        stats = self.current_position.get_stats()
        stats['exit_bar'] = bar_index
        stats['profit_pct'] = profit_pct
        stats['hhv_profit'] = self.current_position.highest_profit
        
        # Store in history
        self.position_history.append(stats)
        
        print(f"  📉 EXIT @ {exit_price:.2f} | P&L: {profit:.2f} pts ({profit_pct:.2f}%) | Reason: {exit_reason} | Max Profit: {self.current_position.highest_profit:.2f}")
        
        # Clear position
        self.current_position = None
        self.hhv_since_buy = None
        self.llv_since_short = None
        
        return stats
    
    def has_position(self) -> bool:
        """Check if currently in position"""
        return self.current_position is not None
    
    def get_current_position(self) -> Optional[Position]:
        """Get current position object"""
        return self.current_position
    
    def get_position_info(self, current_price: float) -> Optional[Dict]:
        """
        Get current position information
        
        Args:
            current_price: Current market price
        
        Returns:
            Dict with position details
        """
        if not self.current_position:
            return None
        
        profit = self.current_position.get_current_profit(current_price)
        exit_levels = self.current_position.get_exit_levels(current_price)
        
        return {
            'direction': self.current_position.direction,
            'entry_price': self.current_position.entry_price,
            'current_price': current_price,
            'size': self.current_position.size,
            'profit': profit,
            'profit_pct': (profit / self.current_position.entry_price) * 100,
            'highest_profit': self.current_position.highest_profit,
            'tp': exit_levels.get('tp'),
            'sl': exit_levels.get('sl'),
            'trailing': exit_levels.get('trailing'),
            'hhv_since_buy': self.hhv_since_buy if self.current_position.direction == 'long' else None,
            'llv_since_short': self.llv_since_short if self.current_position.direction == 'short' else None
        }
    
    def get_statistics(self) -> Dict:
        """
        Get overall trading statistics
        
        Returns:
            Dict with performance metrics
        """
        if not self.position_history:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_profit': 0,
                'avg_profit': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'largest_win': 0,
                'largest_loss': 0,
                'profit_factor': 0
            }
        
        profits = [pos['profit'] for pos in self.position_history]
        winning_trades = [p for p in profits if p > 0]
        losing_trades = [p for p in profits if p < 0]
        
        total_profit = sum(profits)
        total_win = sum(winning_trades) if winning_trades else 0
        total_loss = abs(sum(losing_trades)) if losing_trades else 0
        
        return {
            'total_trades': len(self.position_history),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(self.position_history) * 100) if self.position_history else 0,
            'total_profit': total_profit,
            'avg_profit': total_profit / len(self.position_history),
            'avg_win': sum(winning_trades) / len(winning_trades) if winning_trades else 0,
            'avg_loss': sum(losing_trades) / len(losing_trades) if losing_trades else 0,
            'largest_win': max(winning_trades) if winning_trades else 0,
            'largest_loss': min(losing_trades) if losing_trades else 0,
            'profit_factor': (total_win / total_loss) if total_loss > 0 else float('inf')
        }
    
    def get_position_history(self) -> List[Dict]:
        """Get all closed positions"""
        return self.position_history.copy()
    
    def reset(self):
        """Reset position manager state"""
        self.current_position = None
        self.position_history = []
        self.buy_order_count = 0
        self.short_order_count = 0
        self.hhv_since_buy = None
        self.llv_since_short = None


class TradingEngine:
    """
    Complete Trading Engine with AFL-compatible logic
    Integrates: Signals → Position Manager → Dynamic Exits
    """
    
    def __init__(self,
                 initial_capital: float = 10000,
                 position_size_pct: float = 10,
                 max_positions: int = 1,
                 commission: float = 0.5,
                 slippage: float = 0.1,
                 exit_manager: DynamicExitManager = None):
        """
        Initialize Trading Engine
        
        Args:
            initial_capital: Starting capital
            position_size_pct: Position size as % of capital
            max_positions: Max concurrent positions
            commission: Commission per trade (points)
            slippage: Slippage per trade (points)
            exit_manager: DynamicExitManager instance
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position_size_pct = position_size_pct
        self.commission = commission
        self.slippage = slippage
        
        self.position_manager = PositionManager(
            max_positions=max_positions,
            exit_manager=exit_manager or DynamicExitManager()
        )
        
        self.equity_curve = []
        self.daily_pnl = {}
    
    def calculate_position_size(self, price: float) -> float:
        """Calculate position size based on available capital"""
        position_value = self.capital * (self.position_size_pct / 100)
        size = position_value / price
        return size
    
    def process_bar(self,
                   bar_index: int,
                   open_price: float,
                   high: float,
                   low: float,
                   close: float,
                   buy_signal: bool,
                   short_signal: bool,
                   time: Optional[datetime] = None) -> Dict:
        """
        Process single bar (AFL-style)
        
        Args:
            bar_index: Current bar index
            open_price: Bar open
            high: Bar high
            low: Bar low
            close: Bar close
            buy_signal: Long entry signal
            short_signal: Short entry signal
            time: Bar timestamp
        
        Returns:
            Dict with bar results
        """
        result = {
            'bar': bar_index,
            'action': None,
            'price': None,
            'position': None
        }
        
        # Check existing position first
        if self.position_manager.has_position():
            # Update position
            should_exit, exit_reason = self.position_manager.update_position(
                bar_index, high, low, close, time
            )
            
            if should_exit:
                # Determine exit price based on reason
                if exit_reason == 'stop_loss':
                    pos_info = self.position_manager.get_position_info(close)
                    exit_price = pos_info['sl']
                elif exit_reason == 'take_profit':
                    pos_info = self.position_manager.get_position_info(close)
                    exit_price = pos_info['tp']
                elif exit_reason == 'trailing_stop':
                    pos_info = self.position_manager.get_position_info(close)
                    exit_price = pos_info['trailing']
                else:
                    exit_price = close
                
                # Apply slippage
                direction = self.position_manager.current_position.direction
                if direction == 'long':
                    exit_price -= self.slippage
                else:
                    exit_price += self.slippage
                
                # Exit position
                stats = self.position_manager.exit_position(
                    bar_index, exit_price, exit_reason, time
                )
                
                # Update capital
                profit = stats['profit'] * stats['size']
                profit -= (self.commission * 2)  # Entry + Exit
                self.capital += profit
                
                # Update daily P&L
                if time:
                    date_str = str(time)[:10]
                    self.daily_pnl[date_str] = self.daily_pnl.get(date_str, 0) + profit
                
                result['action'] = 'exit'
                result['price'] = exit_price
                result['profit'] = profit
        
        # Check for new entry (if no position)
        elif buy_signal and self.position_manager.can_enter_long():
            entry_price = open_price + self.slippage
            size = self.calculate_position_size(entry_price)
            
            entered = self.position_manager.enter_long(
                bar_index, entry_price, size, time
            )
            
            if entered:
                result['action'] = 'enter_long'
                result['price'] = entry_price
        
        elif short_signal and self.position_manager.can_enter_short():
            entry_price = open_price - self.slippage
            size = self.calculate_position_size(entry_price)
            
            entered = self.position_manager.enter_short(
                bar_index, entry_price, size, time
            )
            
            if entered:
                result['action'] = 'enter_short'
                result['price'] = entry_price
        
        # Update equity curve
        current_equity = self.capital
        if self.position_manager.has_position():
            pos_info = self.position_manager.get_position_info(close)
            unrealized_pnl = pos_info['profit'] * pos_info['size']
            current_equity += unrealized_pnl
        
        self.equity_curve.append({
            'bar': bar_index,
            'time': time,
            'equity': current_equity,
            'capital': self.capital
        })
        
        result['equity'] = current_equity
        result['position'] = self.position_manager.get_position_info(close)
        
        return result
    
    def get_results(self) -> Dict:
        """Get complete trading results"""
        stats = self.position_manager.get_statistics()
        
        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_return': ((self.capital - self.initial_capital) / self.initial_capital * 100),
            'equity_curve': self.equity_curve,
            'trades': self.position_manager.get_position_history(),
            'statistics': stats
        }
