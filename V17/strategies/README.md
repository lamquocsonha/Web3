# Strategy JSON Structure

This document describes the structure of strategy JSON files used in the V12 trading system.

## Overview

Strategy files are JSON documents that define trading strategies including entry conditions, exit rules, indicators, and risk management parameters.

## File Structure

```json
{
  "name": "Strategy Name",
  "description": "Optional description",
  "entry_conditions": { ... },
  "exit_rules": { ... },
  "indicators": [ ... ],
  "risk_management": { ... }
}
```

## Entry Conditions

Entry conditions are separated by direction (long/short):

```json
"entry_conditions": {
  "long": [
    {
      "name": "Entry Rule Name",
      "conditions": [
        {
          "left": "close",           // Left operand (indicator or price)
          "leftOffset": 0,           // Bars ago (0 = current bar)
          "operator": "cross_above", // Comparison operator
          "right": "ema_20",         // Right operand
          "rightOffset": 0,          // Bars ago
          "logic": "AND"             // Logic operator (AND/OR)
        }
      ]
    }
  ],
  "short": [ ... ]  // Same structure as long
}
```

### Supported Operators
- `cross_above`: Cross above
- `cross_below`: Cross below
- `>`: Greater than
- `<`: Less than
- `>=`: Greater than or equal
- `<=`: Less than or equal
- `==`: Equal to

## Exit Rules

**NEW STRUCTURE (v2):** Exit rules are now separated by direction to allow different exit strategies for long and short positions.

```json
"exit_rules": {
  "long": {
    "dynamic_tp_sl": true,      // Enable dynamic TP/SL
    "time_exit": "14:30",       // Time-based exit (HH:MM)
    "tp_sl_table": [
      {
        "profit_range": [0, 2],  // When profit is between 0-2 points
        "tp": 5,                 // Take profit at 5 points
        "sl": 3,                 // Stop loss at 3 points
        "trailing": 2            // Trailing stop at 2 points
      }
    ]
  },
  "short": {
    "dynamic_tp_sl": true,
    "time_exit": "14:30",
    "tp_sl_table": [ ... ]      // Same structure as long
  }
}
```

### Old Structure (v1) - Deprecated

The old structure with unified exit rules is still supported for backward compatibility:

```json
"exit_rules": {
  "dynamic_tp_sl": true,
  "time_exit": "14:30",
  "tp_sl_table": [ ... ]
}
```

Files with the old structure will be automatically migrated to the new format when loaded.

## Indicators

Indicators define technical indicators used in the strategy:

```json
"indicators": [
  {
    "id": "ema_20",              // Unique identifier
    "type": "EMA",               // Indicator type
    "params": {
      "period": 20               // Indicator parameters
    },
    "display": {
      "show": true,              // Show on chart
      "color": "#2962FF",        // Line color
      "lineStyle": "solid",      // Line style (solid/dashed/dotted)
      "lineWidth": 2             // Line width
    }
  }
]
```

### Supported Indicator Types
- `EMA`: Exponential Moving Average
- `SMA`: Simple Moving Average
- `RSI`: Relative Strength Index
- `MACD`: Moving Average Convergence Divergence
- `BB`: Bollinger Bands
- And more...

## Risk Management

```json
"risk_management": {
  "max_positions": 1,           // Maximum concurrent positions
  "position_size_pct": 10,      // Position size as % of account
  "max_daily_loss": 50,         // Maximum daily loss
  "trading_hours": {
    "start": "09:00",           // Trading start time
    "end": "14:30"              // Trading end time
  }
}
```

## Migration Guide

### Converting Old Format to New Format

If you have strategy files in the old format (unified exit rules), you can manually convert them:

**Old:**
```json
"exit_rules": {
  "dynamic_tp_sl": true,
  "time_exit": "14:30",
  "tp_sl_table": [...]
}
```

**New:**
```json
"exit_rules": {
  "long": {
    "dynamic_tp_sl": true,
    "time_exit": "14:30",
    "tp_sl_table": [...]
  },
  "short": {
    "dynamic_tp_sl": true,
    "time_exit": "14:30",
    "tp_sl_table": [...]
  }
}
```

The system will automatically perform this conversion when loading old files, but it's recommended to save them in the new format for clarity.

## Example Files

- `strategy_template.json` - Template with the new structure
- `Chien_luoc_11.json` - Example strategy file

## Notes

- All time values use 24-hour format (HH:MM)
- Profit ranges in TP/SL tables should be sequential and non-overlapping
- Indicator IDs must be unique within a strategy
- The system automatically validates JSON syntax when loading files
