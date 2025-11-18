"""
Backtest Engine
Tests trading strategies on historical data
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .strategy import Strategy
from .dynamic_exit import Position


class BacktestEngine:
    """
    Backtest trading strategies on historical data
    """
    
    def __init__(self, 
                 strategy: Strategy,
                 initial_capital: float = 10000,
                 commission: float = 0.5,
                 slippage: float = 0.1):
        """
        Initialize backtest engine
        
        Args:
            strategy: Strategy instance
            initial_capital: Starting capital
            commission: Commission per trade (points)
            slippage: Slippage per trade (points)
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        self.reset()
    
    def reset(self):
        """Reset backtest state"""
        self.capital = self.initial_capital
        self.equity_curve = []
        self.trades = []
        self.current_position = None
        self.daily_pnl = {}
        
    def run(self, data: Dict[str, np.ndarray]) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            data: Dict with OHLCV data as numpy arrays
                  Must include: 'open', 'high', 'low', 'close', 'volume'
                  Optional: 'time' (datetime or timestamp)
        
        Returns:
            Dict with backtest results
        """
        print(f"\n🚀 Running backtest: {self.strategy.config['name']}")
        print(f"   Initial Capital: ${self.initial_capital:,.2f}")
        print(f"   Data points: {len(data['close'])}")
        
        self.reset()
        
        # Generate signals
        signals = self.strategy.generate_signals(data)
        buy_signals = signals['buy']
        short_signals = signals['short']
        
        # Get risk management settings
        risk_mgmt = self.strategy.config['risk_management']
        max_positions = risk_mgmt.get('max_positions', 1)
        max_daily_loss = risk_mgmt.get('max_daily_loss', 50)

        # Get active/inactive settings for buy/short
        settings = self.strategy.config.get('settings', {})
        active = settings.get('active', True)
        buy_active = settings.get('buy_active', True)
        short_active = settings.get('short_active', True)

        print(f"   Strategy Active: {active}")
        print(f"   Buy Active: {buy_active}")
        print(f"   Short Active: {short_active}")

        n_bars = len(data['close'])
        
        # Iterate through bars
        for i in range(1, n_bars):
            current_open = data['open'][i]
            current_high = data['high'][i]
            current_low = data['low'][i]
            current_close = data['close'][i]
            
            # Check if we have open position
            if self.current_position:
                # Update position and check exit
                should_exit, exit_reason = self.current_position.update(current_high, current_low)
                
                if should_exit:
                    # Close position
                    if exit_reason == 'stop_loss':
                        exit_price = self.current_position.get_exit_levels(current_close)['sl']
                    elif exit_reason == 'take_profit':
                        exit_price = self.current_position.get_exit_levels(current_close)['tp']
                    elif exit_reason == 'trailing_stop':
                        exit_price = self.current_position.get_exit_levels(current_close)['trailing']
                    else:
                        exit_price = current_close
                    
                    # Apply slippage
                    if self.current_position.direction == 'long':
                        exit_price -= self.slippage
                    else:
                        exit_price += self.slippage
                    
                    self._close_position(i, exit_price, exit_reason, data)
            
            # Check for new entries (only if no position)
            if not self.current_position and max_positions > 0 and active:
                # Check daily loss limit
                current_date = data.get('time', [None])[i]
                if current_date:
                    date_str = str(current_date)[:10]  # YYYY-MM-DD
                    daily_loss = self.daily_pnl.get(date_str, 0)
                    if daily_loss <= -max_daily_loss:
                        continue  # Skip trading for today

                # Check buy signal (only if buy_active is True)
                if buy_signals[i] and buy_active:
                    entry_price = current_open + self.slippage
                    self._open_position(i, entry_price, 'long', data)

                # Check short signal (only if short_active is True)
                elif short_signals[i] and short_active:
                    entry_price = current_open - self.slippage
                    self._open_position(i, entry_price, 'short', data)
            
            # Update equity curve
            current_equity = self.capital
            if self.current_position:
                unrealized_pnl = self.current_position.get_current_profit(current_close)
                current_equity += unrealized_pnl
            
            self.equity_curve.append({
                'bar': i,
                'time': data.get('time', [None])[i],
                'equity': current_equity,
                'capital': self.capital
            })
        
        # Close any remaining position
        if self.current_position:
            self._close_position(n_bars - 1, data['close'][-1], 'end_of_data', data)
        
        # Calculate statistics
        results = self._calculate_statistics(data)
        
        print(f"\n✅ Backtest completed!")
        print(f"   Total Trades: {results['total_trades']}")
        print(f"   Win Rate: {results['win_rate']:.2f}%")
        print(f"   Final Capital: ${results['final_capital']:,.2f}")
        print(f"   Total Return: {results['total_return']:.2f}%")
        print(f"   Max Drawdown: {results['max_drawdown']:.2f}%")
        
        return results
    
    def _open_position(self, bar_index: int, entry_price: float, direction: str, data: Dict):
        """Open new position"""
        # Calculate position size
        risk_mgmt = self.strategy.config['risk_management']
        position_size_pct = risk_mgmt.get('position_size_pct', 10)
        position_value = self.capital * (position_size_pct / 100)
        size = position_value / entry_price
        
        # Create position
        self.current_position = Position(
            entry_price=entry_price,
            direction=direction,
            size=size,
            exit_manager=self.strategy.get_exit_manager()
        )
        self.current_position.entry_time = data.get('time', [None])[bar_index]
        
        print(f"  📈 {direction.upper()} @ {entry_price:.2f} (Bar {bar_index})")
    
    def _close_position(self, bar_index: int, exit_price: float, exit_reason: str, data: Dict):
        """Close current position"""
        self.current_position.close(exit_price, exit_reason)
        self.current_position.exit_time = data.get('time', [None])[bar_index]
        
        # Calculate P&L
        profit = self.current_position.get_current_profit(exit_price)
        profit_points = profit
        profit_value = profit * self.current_position.size
        
        # Subtract commission
        total_commission = self.commission * 2  # Entry + Exit
        profit_value -= total_commission
        
        # Update capital
        self.capital += profit_value
        
        # Update daily P&L
        exit_time = self.current_position.exit_time
        if exit_time:
            date_str = str(exit_time)[:10]
            self.daily_pnl[date_str] = self.daily_pnl.get(date_str, 0) + profit_value
        
        # Store trade
        trade = {
            'entry_time': self.current_position.entry_time,
            'entry_price': self.current_position.entry_price,
            'exit_time': self.current_position.exit_time,
            'exit_price': exit_price,
            'direction': self.current_position.direction,
            'size': self.current_position.size,
            'profit_points': profit_points,
            'profit_value': profit_value,
            'exit_reason': exit_reason,
            'highest_profit': self.current_position.highest_profit
        }
        self.trades.append(trade)
        
        print(f"  📉 EXIT @ {exit_price:.2f} | P&L: {profit_points:.2f} pts (${profit_value:.2f}) | Reason: {exit_reason}")
        
        # Clear position
        self.current_position = None
    
    def _calculate_statistics(self, data: Dict) -> Dict:
        """Calculate backtest statistics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'final_capital': self.initial_capital,
                'total_return': 0,
                'max_drawdown': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'largest_win': 0,
                'largest_loss': 0,
                'trades': [],
                'equity_curve': []
            }
        
        trades_df = pd.DataFrame(self.trades)
        
        # Basic stats
        total_trades = len(self.trades)
        winning_trades = len(trades_df[trades_df['profit_value'] > 0])
        losing_trades = len(trades_df[trades_df['profit_value'] < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # P&L stats
        total_profit = trades_df[trades_df['profit_value'] > 0]['profit_value'].sum()
        total_loss = abs(trades_df[trades_df['profit_value'] < 0]['profit_value'].sum())
        profit_factor = (total_profit / total_loss) if total_loss > 0 else float('inf')
        
        # Equity curve stats
        equity_df = pd.DataFrame(self.equity_curve)
        final_capital = equity_df['equity'].iloc[-1] if len(equity_df) > 0 else self.initial_capital
        total_return = ((final_capital - self.initial_capital) / self.initial_capital * 100)
        
        # Max drawdown
        equity_series = equity_df['equity']
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        
        # Sharpe ratio (simplified)
        returns = equity_series.pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std() * np.sqrt(252)) if len(returns) > 0 else 0
        
        # Average win/loss and largest win/loss
        wins = trades_df[trades_df['profit_value'] > 0]['profit_value']
        losses = trades_df[trades_df['profit_value'] <= 0]['profit_value']

        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = abs(losses.mean()) if len(losses) > 0 else 0  # Return positive value
        largest_win = wins.max() if len(wins) > 0 else 0
        largest_loss = abs(losses.min()) if len(losses) > 0 else 0  # Return positive value
        
        # Convert NaN to 0
        if pd.isna(avg_win):
            avg_win = 0
        if pd.isna(avg_loss):
            avg_loss = 0
        if pd.isna(largest_win):
            largest_win = 0
        if pd.isna(largest_loss):
            largest_loss = 0
        if pd.isna(sharpe_ratio):
            sharpe_ratio = 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'final_capital': final_capital,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'trades': self.trades,
            'equity_curve': self.equity_curve,
            'daily_pnl': self.daily_pnl
        }
    
    def get_trades_dataframe(self) -> pd.DataFrame:
        """Get trades as pandas DataFrame"""
        if not self.trades:
            return pd.DataFrame()
        return pd.DataFrame(self.trades)
    
    def get_equity_dataframe(self) -> pd.DataFrame:
        """Get equity curve as pandas DataFrame"""
        if not self.equity_curve:
            return pd.DataFrame()
        return pd.DataFrame(self.equity_curve)
    
    def export_results(self, filepath: str):
        """Export backtest results to JSON"""
        import json
        results = self._calculate_statistics({})
        
        # Remove non-serializable objects
        results_export = {
            k: v for k, v in results.items() 
            if k not in ['trades', 'equity_curve', 'daily_pnl']
        }
        
        with open(filepath, 'w') as f:
            json.dump(results_export, f, indent=2)
        
        print(f"💾 Results exported to {filepath}")
