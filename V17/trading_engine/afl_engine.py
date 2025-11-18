"""
AFL Trading Engine
Complete implementation based on MT5_trading_engine.afl
- No repaint: Entry on NEXT candle after signal  
- Exit within current candle: SL/TP checked on current bar
- Dynamic TP/SL based on profit levels
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
from datetime import datetime, time


class AFLTradingEngine:
    """
    Trading engine that follows AFL logic exactly:
    1. Entry: Signal generated on bar[i], entry on bar[i+1] at Open
    2. Exit: Checked within bar[i] using High/Low
    3. Dynamic TP/SL: Adjusted based on HHV profit
    """
    
    def __init__(self, config: Dict):
        """
        Args:
            config: Strategy configuration with settings
        """
        self.config = config
        self.settings = config.get('settings', {})
        self.risk_mgmt = config.get('risk_management', {})
        
        # Trading parameters
        self.active = self.settings.get('active', True)
        self.buy_active = self.settings.get('buy_active', True)
        self.short_active = self.settings.get('short_active', True)
        
        # Time settings
        trading_hours = self.settings.get('trading_hours', {})
        self.start_time = self._parse_time(trading_hours.get('start', '09:00'))
        self.end_time = self._parse_time(trading_hours.get('end', '14:30'))
        self.base_time = self._parse_time(self.settings.get('base_time', '09:00'))
        
        # Order limits
        self.buy_order_limit = self.settings.get('buy_order_limit', 10)
        self.short_order_limit = self.settings.get('short_order_limit', 10)
        
        # Fees
        self.fee_tax = self.risk_mgmt.get('commission', 1.0)
        
        # Position tracking
        self.reset_position()
        
    def reset_position(self):
        """Reset position tracking"""
        self.position = 0  # 0=no position, 1=long, -1=short
        self.entry_price = 0.0
        self.entry_bar = -1
        self.buy_count = 0
        self.short_count = 0
        
        # TP/SL tracking for long
        self.tp_buy = None
        self.sl_buy = None
        self.trailing_buy = None
        self.hhv_since_buy = None
        self.hhv_buy_profit = 0.0
        
        # TP/SL tracking for short
        self.tp_short = None
        self.sl_short = None
        self.trailing_short = None
        self.llv_since_short = None
        self.hhv_short_profit = 0.0
        
    def _parse_time(self, time_str: str) -> time:
        """Parse time string HH:MM to time object"""
        try:
            h, m = map(int, time_str.split(':'))
            return time(h, m)
        except:
            return time(9, 0)
    
    def _time_to_int(self, dt: datetime) -> int:
        """Convert datetime to HHMMSS integer"""
        return dt.hour * 10000 + dt.minute * 100 + dt.second
    
    def _in_time_range(self, dt: datetime) -> bool:
        """Check if time is within trading hours"""
        t = dt.time()
        return self.start_time <= t <= self.end_time
    
    def _get_dynamic_tp_sl_buy(self, profit: float) -> Tuple[Optional[float], float, float]:
        """
        Get dynamic TP/SL for long position based on profit
        Returns: (tp_points, sl_points, trailing_points)
        Based on AFL lines 1088-1184
        """
        if profit >= 28:
            return None, 10, profit / 100 * 55
        elif profit >= 26:
            return None, 10, profit / 100 * 61
        elif profit >= 24:
            return None, 10, profit / 100 * 65
        elif profit >= 22:
            return None, 10, profit / 100 * 68
        elif profit >= 20:
            return None, 10, profit / 100 * 68
        elif profit >= 18:
            return None, 10, profit / 100 * 68
        elif profit >= 16:
            return None, 10, profit / 100 * 68
        elif profit >= 14:
            return None, 10, 8.2
        elif profit >= 12:
            return None, 10, 10.1
        elif profit >= 10:
            return None, 1, 12
        elif profit >= 8:
            return None, 1.2, 9.5
        elif profit >= 6:
            return None, 4, 10.1
        elif profit >= 4:
            return None, 5.5, 9.8
        elif profit >= 2:
            return None, 10.8, 13.9
        else:
            return None, 10.3, 11.9
    
    def _get_dynamic_tp_sl_short(self, profit: float) -> Tuple[Optional[float], float, float]:
        """
        Get dynamic TP/SL for short position based on profit
        Returns: (tp_points, sl_points, trailing_points)
        Based on AFL lines 1219-1312
        """
        if profit >= 28:
            return None, 10, profit / 100 * 55
        elif profit >= 26:
            return None, 10, profit / 100 * 61
        elif profit >= 24:
            return None, 10, profit / 100 * 65
        elif profit >= 22:
            return None, 10, profit / 100 * 68
        elif profit >= 20:
            return None, 10, profit / 100 * 68
        elif profit >= 18:
            return None, 10, profit / 100 * 68
        elif profit >= 16:
            return None, 10, profit / 100 * 68
        elif profit >= 14:
            return None, 10, 8.2
        elif profit >= 12:
            return None, 10, 10.1
        elif profit >= 10:
            return None, 1, 12
        elif profit >= 8:
            return None, 1.2, 9.5
        elif profit >= 6:
            return None, 4, 10.1
        elif profit >= 4:
            return None, 5.5, 9.8
        elif profit >= 2:
            return None, 10.8, 13.9
        else:
            return None, 10.3, 11.9
    
    def run_backtest(self, data: Dict[str, np.ndarray], signals: Dict[str, np.ndarray]) -> Dict:
        """
        Run backtest with AFL logic
        
        Args:
            data: OHLCV data with 'open', 'high', 'low', 'close', 'time'
            signals: Entry signals with 'buy_signal', 'short_signal'
        
        Returns:
            Dict with trades and statistics
        """
        n_bars = len(data['close'])
        
        # Initialize arrays
        buy = np.zeros(n_bars, dtype=bool)
        sell = np.zeros(n_bars, dtype=bool)
        short = np.zeros(n_bars, dtype=bool)
        cover = np.zeros(n_bars, dtype=bool)
        
        buy_price = np.zeros(n_bars)
        sell_price = np.zeros(n_bars)
        short_price = np.zeros(n_bars)
        cover_price = np.zeros(n_bars)
        
        # TP/SL lines
        sl_buy_line = np.full(n_bars, np.nan)
        tp_buy_line = np.full(n_bars, np.nan)
        trailing_buy_line = np.full(n_bars, np.nan)
        sl_short_line = np.full(n_bars, np.nan)
        tp_short_line = np.full(n_bars, np.nan)
        trailing_short_line = np.full(n_bars, np.nan)
        
        entry_price_line = np.full(n_bars, np.nan)
        hhv_since_buy_line = np.full(n_bars, np.nan)
        llv_since_short_line = np.full(n_bars, np.nan)
        
        trades = []
        
        # Reset
        self.reset_position()
        
        # Main loop
        for i in range(1, n_bars):
            O = data['open'][i]
            H = data['high'][i]
            L = data['low'][i]
            C = data['close'][i]
            
            # Time check
            if 'time' in data:
                dt = data['time'][i]
                if isinstance(dt, (int, float)):
                    dt = datetime.fromtimestamp(dt)
                in_time_range = self._in_time_range(dt)
                itime = self._time_to_int(dt)
            else:
                in_time_range = True
                itime = 100000
            
            # === MANAGE EXISTING LONG POSITION ===
            if self.position == 1:
                # Update HHV
                if self.hhv_since_buy is None or H > self.hhv_since_buy:
                    self.hhv_since_buy = H
                
                # Update profit
                current_profit = self.hhv_since_buy - self.entry_price - self.fee_tax
                if current_profit > self.hhv_buy_profit:
                    self.hhv_buy_profit = current_profit
                
                # Dynamic TP/SL
                tp_points, sl_points, trailing_points = self._get_dynamic_tp_sl_buy(self.hhv_buy_profit)
                
                if tp_points is not None:
                    self.tp_buy = self.entry_price + tp_points
                else:
                    self.tp_buy = None
                    
                self.sl_buy = self.entry_price - sl_points
                self.trailing_buy = self.hhv_since_buy - trailing_points
                
                # Update lines
                sl_buy_line[i] = self.sl_buy
                if self.tp_buy:
                    tp_buy_line[i] = self.tp_buy
                trailing_buy_line[i] = self.trailing_buy
                entry_price_line[i] = self.entry_price
                hhv_since_buy_line[i] = self.hhv_since_buy
                
                # Check exits
                exit_triggered = False
                exit_price = None
                exit_reason = None
                
                if in_time_range:
                    if L < self.sl_buy:
                        exit_triggered = True
                        exit_price = L
                        exit_reason = 'SL'
                    elif itime != 142900 and L < self.trailing_buy:
                        exit_triggered = True
                        exit_price = L
                        exit_reason = 'Trailing'
                    elif self.tp_buy and H > self.tp_buy and L > data['low'][i-1]:
                        exit_triggered = True
                        exit_price = H
                        exit_reason = 'TP'
                
                if exit_triggered:
                    sell[i] = True
                    sell_price[i] = exit_price
                    
                    profit = exit_price - self.entry_price - self.fee_tax
                    trades.append({
                        'entry_bar': self.entry_bar,
                        'exit_bar': i,
                        'type': 'long',
                        'entry_price': self.entry_price,
                        'exit_price': exit_price,
                        'profit': profit,
                        'max_profit': self.hhv_buy_profit,
                        'exit_reason': exit_reason,
                        'bars_held': i - self.entry_bar
                    })
                    
                    # Reset
                    self.position = 0
                    self.entry_price = 0.0
                    self.entry_bar = -1
                    self.tp_buy = None
                    self.sl_buy = None
                    self.trailing_buy = None
                    self.hhv_since_buy = None
                    self.hhv_buy_profit = 0.0
            
            # === MANAGE EXISTING SHORT POSITION ===
            elif self.position == -1:
                # Update LLV
                if self.llv_since_short is None or L < self.llv_since_short:
                    self.llv_since_short = L
                
                # Update profit
                current_profit = self.entry_price - self.llv_since_short - self.fee_tax
                if current_profit > self.hhv_short_profit:
                    self.hhv_short_profit = current_profit
                
                # Dynamic TP/SL
                tp_points, sl_points, trailing_points = self._get_dynamic_tp_sl_short(self.hhv_short_profit)
                
                if tp_points is not None:
                    self.tp_short = self.entry_price - tp_points
                else:
                    self.tp_short = None
                    
                self.sl_short = self.entry_price + sl_points
                self.trailing_short = self.llv_since_short + trailing_points
                
                # Update lines
                sl_short_line[i] = self.sl_short
                if self.tp_short:
                    tp_short_line[i] = self.tp_short
                trailing_short_line[i] = self.trailing_short
                entry_price_line[i] = self.entry_price
                llv_since_short_line[i] = self.llv_since_short
                
                # Check exits
                exit_triggered = False
                exit_price = None
                exit_reason = None
                
                if in_time_range:
                    if H > self.sl_short:
                        exit_triggered = True
                        exit_price = H
                        exit_reason = 'SL'
                    elif itime != 142900 and H > self.trailing_short:
                        exit_triggered = True
                        exit_price = H
                        exit_reason = 'Trailing'
                    elif self.tp_short and L < self.tp_short and H < data['high'][i-1]:
                        exit_triggered = True
                        exit_price = L
                        exit_reason = 'TP'
                
                if exit_triggered:
                    cover[i] = True
                    cover_price[i] = exit_price
                    
                    profit = self.entry_price - exit_price - self.fee_tax
                    trades.append({
                        'entry_bar': self.entry_bar,
                        'exit_bar': i,
                        'type': 'short',
                        'entry_price': self.entry_price,
                        'exit_price': exit_price,
                        'profit': profit,
                        'max_profit': self.hhv_short_profit,
                        'exit_reason': exit_reason,
                        'bars_held': i - self.entry_bar
                    })
                    
                    # Reset
                    self.position = 0
                    self.entry_price = 0.0
                    self.entry_bar = -1
                    self.tp_short = None
                    self.sl_short = None
                    self.trailing_short = None
                    self.llv_since_short = None
                    self.hhv_short_profit = 0.0
            
            # === NEW ENTRY (No repaint) ===
            if self.position == 0 and in_time_range:
                # Buy: Signal at [i-1], enter at [i] Open
                if i > 0 and signals['buy_signal'][i-1] and self.active and self.buy_active:
                    if self.buy_count < self.buy_order_limit:
                        buy[i] = True
                        buy_price[i] = O
                        
                        self.position = 1
                        self.entry_price = O
                        self.entry_bar = i
                        self.hhv_since_buy = O
                        self.hhv_buy_profit = 0.0
                        self.buy_count += 1
                
                # Short: Signal at [i-1], enter at [i] Open
                elif i > 0 and signals['short_signal'][i-1] and self.active and self.short_active:
                    if self.short_count < self.short_order_limit:
                        short[i] = True
                        short_price[i] = O
                        
                        self.position = -1
                        self.entry_price = O
                        self.entry_bar = i
                        self.llv_since_short = O
                        self.hhv_short_profit = 0.0
                        self.short_count += 1
        
        # Stats
        stats = self._calculate_stats(trades, data)
        
        return {
            'trades': trades,
            'stats': stats,
            'signals': {
                'buy': buy,
                'sell': sell,
                'short': short,
                'cover': cover,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'short_price': short_price,
                'cover_price': cover_price
            },
            'lines': {
                'sl_buy': sl_buy_line,
                'tp_buy': tp_buy_line,
                'trailing_buy': trailing_buy_line,
                'sl_short': sl_short_line,
                'tp_short': tp_short_line,
                'trailing_short': trailing_short_line,
                'entry_price': entry_price_line,
                'hhv_since_buy': hhv_since_buy_line,
                'llv_since_short': llv_since_short_line
            }
        }
    
    def _calculate_stats(self, trades: List[Dict], data: Dict) -> Dict:
        """Calculate trading statistics"""
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'total_profit': 0.0,
                'avg_profit': 0.0,
                'max_profit': 0.0,
                'max_loss': 0.0,
                'profit_factor': 0.0
            }
        
        profits = [t['profit'] for t in trades]
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p < 0]
        
        total_profit = sum(profits)
        win_rate = len(wins) / len(trades) * 100 if trades else 0
        
        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        return {
            'total_trades': len(trades),
            'win_trades': len(wins),
            'loss_trades': len(losses),
            'win_rate': round(win_rate, 2),
            'total_profit': round(total_profit, 2),
            'avg_profit': round(total_profit / len(trades), 2),
            'avg_win': round(sum(wins) / len(wins), 2) if wins else 0,
            'avg_loss': round(sum(losses) / len(losses), 2) if losses else 0,
            'max_profit': round(max(profits), 2),
            'max_loss': round(min(profits), 2),
            'profit_factor': round(profit_factor, 2),
            'gross_profit': round(gross_profit, 2),
            'gross_loss': round(gross_loss, 2)
        }
