"""
Auto Optimize Trading System - Trading Engine
Python implementation of AFL trading logic with visual strategy builder support
"""

__version__ = '1.0.0'
__author__ = 'Auto Optimize Trading System'

from .indicators import *
from .strategy import Strategy
from .backtest_engine import BacktestEngine
from .optimizer import GeneticOptimizer
from .dynamic_exit import DynamicExitManager, Position
from .position_manager import PositionManager, TradingEngine

__all__ = [
    'Strategy',
    'BacktestEngine', 
    'GeneticOptimizer',
    'DynamicExitManager',
    'Position',
    'PositionManager',
    'TradingEngine'
]
