"""
Timeframe Resampler - Convert OHLCV data to different timeframes
Similar to Amibroker's timeframe functionality
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List


class TimeframeResampler:
    """Resample OHLCV data to different timeframes"""

    # Mapping of timeframe strings to pandas resample rules
    TIMEFRAME_MAP = {
        '1m': '1min',
        '5m': '5min',
        '15m': '15min',
        '30m': '30min',
        '1H': '1H',
        '2H': '2H',
        '4H': '4H',
        '1D': '1D',
        '1W': '1W',
        '1M': '1M'
    }

    def __init__(self, data: Dict):
        """
        Initialize resampler with OHLCV data

        Args:
            data: Dictionary with keys: 'times', 'opens', 'highs', 'lows', 'closes', 'volumes'
        """
        self.data = data

    def resample(self, timeframe: str) -> Dict:
        """
        Resample data to specified timeframe

        Args:
            timeframe: Target timeframe (e.g., '1H', '1D', '5m')

        Returns:
            Resampled data dictionary with same structure as input
        """
        # If timeframe not in map or is same as source, return original data
        if timeframe not in self.TIMEFRAME_MAP:
            return self.data

        resample_rule = self.TIMEFRAME_MAP[timeframe]

        try:
            # Convert to pandas DataFrame
            df = pd.DataFrame({
                'time': pd.to_datetime(self.data['times'], unit='s'),
                'open': self.data['opens'],
                'high': self.data['highs'],
                'low': self.data['lows'],
                'close': self.data['closes'],
                'volume': self.data['volumes']
            })

            # Set time as index
            df.set_index('time', inplace=True)

            # Resample using OHLC aggregation rules
            resampled = df.resample(resample_rule).agg({
                'open': 'first',    # First value in period
                'high': 'max',      # Maximum value
                'low': 'min',       # Minimum value
                'close': 'last',    # Last value in period
                'volume': 'sum'     # Sum of volumes
            })

            # Drop rows with NaN (incomplete periods)
            resampled.dropna(inplace=True)

            # Convert back to dictionary format
            result = {
                'times': [int(ts.timestamp()) for ts in resampled.index],
                'opens': resampled['open'].tolist(),
                'highs': resampled['high'].tolist(),
                'lows': resampled['low'].tolist(),
                'closes': resampled['close'].tolist(),
                'volumes': resampled['volume'].tolist()
            }

            return result

        except Exception as e:
            print(f"Error resampling data: {str(e)}")
            # Return original data if resampling fails
            return self.data

    @staticmethod
    def get_available_timeframes() -> List[str]:
        """Get list of available timeframes"""
        return list(TimeframeResampler.TIMEFRAME_MAP.keys())

    @staticmethod
    def is_valid_timeframe(timeframe: str) -> bool:
        """Check if timeframe is valid"""
        return timeframe in TimeframeResampler.TIMEFRAME_MAP


def resample_data(data: Dict, timeframe: str) -> Dict:
    """
    Convenience function to resample data

    Args:
        data: OHLCV data dictionary
        timeframe: Target timeframe

    Returns:
        Resampled data dictionary
    """
    resampler = TimeframeResampler(data)
    return resampler.resample(timeframe)
