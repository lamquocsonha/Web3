"""
Technical Indicators Library
Comprehensive collection of trading indicators
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple


class Indicators:
    """Technical Analysis Indicators"""
    
    # ==================== TREND INDICATORS ====================
    
    @staticmethod
    def ema(data: np.ndarray, period: int) -> np.ndarray:
        """Exponential Moving Average"""
        ema = np.zeros_like(data)
        ema[0] = data[0]
        multiplier = 2 / (period + 1)
        
        for i in range(1, len(data)):
            ema[i] = (data[i] - ema[i-1]) * multiplier + ema[i-1]
        
        return ema
    
    @staticmethod
    def sma(data: np.ndarray, period: int) -> np.ndarray:
        """Simple Moving Average"""
        sma = np.convolve(data, np.ones(period)/period, mode='same')
        sma[:period-1] = np.nan
        return sma
    
    @staticmethod
    def wma(data: np.ndarray, period: int) -> np.ndarray:
        """Weighted Moving Average"""
        weights = np.arange(1, period + 1)
        wma = np.convolve(data, weights/weights.sum(), mode='same')
        wma[:period-1] = np.nan
        return wma
    
    @staticmethod
    def dema(data: np.ndarray, period: int) -> np.ndarray:
        """Double Exponential Moving Average"""
        ema1 = Indicators.ema(data, period)
        ema2 = Indicators.ema(ema1, period)
        return 2 * ema1 - ema2
    
    @staticmethod
    def tema(data: np.ndarray, period: int) -> np.ndarray:
        """Triple Exponential Moving Average"""
        ema1 = Indicators.ema(data, period)
        ema2 = Indicators.ema(ema1, period)
        ema3 = Indicators.ema(ema2, period)
        return 3 * ema1 - 3 * ema2 + ema3
    
    # ==================== MOMENTUM INDICATORS ====================
    
    @staticmethod
    def rsi(data: np.ndarray, period: int = 14) -> np.ndarray:
        """Relative Strength Index"""
        delta = np.diff(data, prepend=data[0])
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        
        avg_gain = Indicators.ema(gain, period)
        avg_loss = Indicators.ema(loss, period)
        
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(data: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """MACD - Moving Average Convergence Divergence"""
        ema_fast = Indicators.ema(data, fast)
        ema_slow = Indicators.ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = Indicators.ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def stochastic(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                   k_period: int = 14, d_period: int = 3) -> Tuple[np.ndarray, np.ndarray]:
        """Stochastic Oscillator"""
        lowest_low = pd.Series(low).rolling(k_period).min().values
        highest_high = pd.Series(high).rolling(k_period).max().values
        
        k = 100 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)
        d = Indicators.sma(k, d_period)
        
        return k, d
    
    @staticmethod
    def cci(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 20) -> np.ndarray:
        """Commodity Channel Index"""
        tp = (high + low + close) / 3
        sma_tp = Indicators.sma(tp, period)
        mad = pd.Series(tp).rolling(period).apply(lambda x: np.abs(x - x.mean()).mean()).values
        
        cci = (tp - sma_tp) / (0.015 * mad + 1e-10)
        
        return cci
    
    @staticmethod
    def mfi(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
            volume: np.ndarray, period: int = 14) -> np.ndarray:
        """Money Flow Index"""
        tp = (high + low + close) / 3
        raw_mf = tp * volume
        
        delta = np.diff(tp, prepend=tp[0])
        positive_mf = np.where(delta > 0, raw_mf, 0)
        negative_mf = np.where(delta < 0, raw_mf, 0)
        
        positive_mf_sum = pd.Series(positive_mf).rolling(period).sum().values
        negative_mf_sum = pd.Series(negative_mf).rolling(period).sum().values
        
        mfr = positive_mf_sum / (negative_mf_sum + 1e-10)
        mfi = 100 - (100 / (1 + mfr))
        
        return mfi
    
    # ==================== VOLATILITY INDICATORS ====================
    
    @staticmethod
    def bollinger_bands(data: np.ndarray, period: int = 20, std_dev: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Bollinger Bands"""
        middle = Indicators.sma(data, period)
        std = pd.Series(data).rolling(period).std().values
        
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        return upper, middle, lower
    
    @staticmethod
    def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
        """Average True Range"""
        tr1 = high - low
        tr2 = np.abs(high - np.roll(close, 1))
        tr3 = np.abs(low - np.roll(close, 1))
        
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        tr[0] = tr1[0]
        
        atr = Indicators.ema(tr, period)
        
        return atr
    
    @staticmethod
    def keltner_channel(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                        period: int = 20, multiplier: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Keltner Channel"""
        middle = Indicators.ema(close, period)
        atr = Indicators.atr(high, low, close, period)
        
        upper = middle + (multiplier * atr)
        lower = middle - (multiplier * atr)
        
        return upper, middle, lower
    
    @staticmethod
    def donchian_channel(high: np.ndarray, low: np.ndarray, period: int = 20) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Donchian Channel"""
        upper = pd.Series(high).rolling(period).max().values
        lower = pd.Series(low).rolling(period).min().values
        middle = (upper + lower) / 2
        
        return upper, middle, lower
    
    # ==================== VOLUME INDICATORS ====================
    
    @staticmethod
    def obv(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """On Balance Volume"""
        direction = np.sign(np.diff(close, prepend=close[0]))
        obv = np.cumsum(direction * volume)
        
        return obv
    
    @staticmethod
    def vwap(high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Volume Weighted Average Price"""
        tp = (high + low + close) / 3
        cumulative_tp_volume = np.cumsum(tp * volume)
        cumulative_volume = np.cumsum(volume)
        
        vwap = cumulative_tp_volume / (cumulative_volume + 1e-10)
        
        return vwap
    
    # ==================== CUSTOM INDICATORS ====================
    
    @staticmethod
    def supertrend(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                   period: int = 10, multiplier: float = 3.0) -> Tuple[np.ndarray, np.ndarray]:
        """SuperTrend Indicator"""
        atr = Indicators.atr(high, low, close, period)
        hl_avg = (high + low) / 2
        
        basic_upper = hl_avg + (multiplier * atr)
        basic_lower = hl_avg - (multiplier * atr)
        
        final_upper = np.zeros_like(basic_upper)
        final_lower = np.zeros_like(basic_lower)
        supertrend = np.zeros_like(close)
        direction = np.ones_like(close)  # 1 = uptrend, -1 = downtrend
        
        final_upper[0] = basic_upper[0]
        final_lower[0] = basic_lower[0]
        supertrend[0] = final_upper[0]
        
        for i in range(1, len(close)):
            # Calculate final bands
            if basic_upper[i] < final_upper[i-1] or close[i-1] > final_upper[i-1]:
                final_upper[i] = basic_upper[i]
            else:
                final_upper[i] = final_upper[i-1]
            
            if basic_lower[i] > final_lower[i-1] or close[i-1] < final_lower[i-1]:
                final_lower[i] = basic_lower[i]
            else:
                final_lower[i] = final_lower[i-1]
            
            # Determine trend direction
            if close[i] <= final_upper[i]:
                direction[i] = -1
                supertrend[i] = final_upper[i]
            else:
                direction[i] = 1
                supertrend[i] = final_lower[i]
        
        return supertrend, direction
    
    @staticmethod
    def pivot_points(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> dict:
        """Classic Pivot Points (Daily)"""
        # Assume last complete bar is yesterday
        h = high[-2] if len(high) > 1 else high[-1]
        l = low[-2] if len(low) > 1 else low[-1]
        c = close[-2] if len(close) > 1 else close[-1]
        
        pp = (h + l + c) / 3
        r1 = (2 * pp) - l
        s1 = (2 * pp) - h
        r2 = pp + (r1 - s1)
        s2 = pp - (r1 - s1)
        r3 = pp + (r2 - s1)
        s3 = pp - (r2 - s1)
        
        return {
            'PP': pp,
            'R1': r1, 'R2': r2, 'R3': r3,
            'S1': s1, 'S2': s2, 'S3': s3
        }
    
    @staticmethod
    def peak_trough(high: np.ndarray, low: np.ndarray, lookback: int = 20) -> Tuple[np.ndarray, np.ndarray]:
        """Peak and Trough Detection"""
        peak = pd.Series(high).rolling(lookback, center=True).max().values
        trough = pd.Series(low).rolling(lookback, center=True).min().values
        
        return peak, trough


# ==================== HELPER FUNCTIONS ====================

def calculate_indicator(indicator_name: str, data: dict, params: dict) -> Union[np.ndarray, Tuple]:
    """
    Universal indicator calculator
    
    Args:
        indicator_name: Name of indicator (e.g., 'EMA', 'RSI', 'MACD')
        data: Dict with 'open', 'high', 'low', 'close', 'volume' as numpy arrays
        params: Dict with indicator parameters
    
    Returns:
        Indicator values as numpy array or tuple of arrays
    """
    ind = Indicators()
    
    # Map indicator names to methods
    indicator_map = {
        'EMA': lambda: ind.ema(data['close'], params.get('period', 14)),
        'SMA': lambda: ind.sma(data['close'], params.get('period', 14)),
        'WMA': lambda: ind.wma(data['close'], params.get('period', 14)),
        'DEMA': lambda: ind.dema(data['close'], params.get('period', 14)),
        'TEMA': lambda: ind.tema(data['close'], params.get('period', 14)),
        'RSI': lambda: ind.rsi(data['close'], params.get('period', 14)),
        'MACD': lambda: ind.macd(data['close'], params.get('fast', 12), params.get('slow', 26), params.get('signal', 9)),
        'Stochastic': lambda: ind.stochastic(data['high'], data['low'], data['close'], params.get('k_period', 14), params.get('d_period', 3)),
        'CCI': lambda: ind.cci(data['high'], data['low'], data['close'], params.get('period', 20)),
        'MFI': lambda: ind.mfi(data['high'], data['low'], data['close'], data['volume'], params.get('period', 14)),
        'BollingerBands': lambda: ind.bollinger_bands(data['close'], params.get('period', 20), params.get('std_dev', 2.0)),
        'ATR': lambda: ind.atr(data['high'], data['low'], data['close'], params.get('period', 14)),
        'KeltnerChannel': lambda: ind.keltner_channel(data['high'], data['low'], data['close'], params.get('period', 20), params.get('multiplier', 2.0)),
        'DonchianChannel': lambda: ind.donchian_channel(data['high'], data['low'], params.get('period', 20)),
        'OBV': lambda: ind.obv(data['close'], data['volume']),
        'VWAP': lambda: ind.vwap(data['high'], data['low'], data['close'], data['volume']),
        'SuperTrend': lambda: ind.supertrend(data['high'], data['low'], data['close'], params.get('period', 10), params.get('multiplier', 3.0)),
        'PivotPoints': lambda: ind.pivot_points(data['high'], data['low'], data['close']),
        'PeakTrough': lambda: ind.peak_trough(data['high'], data['low'], params.get('lookback', 20))
    }
    
    if indicator_name in indicator_map:
        return indicator_map[indicator_name]()
    else:
        raise ValueError(f"Unknown indicator: {indicator_name}")
