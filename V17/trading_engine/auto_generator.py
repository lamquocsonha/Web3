"""
Auto Strategy Generator
Template-based strategy generation with randomization
"""

import random
import json
from typing import Dict, List
from pathlib import Path


class StrategyAutoGenerator:
    """
    Auto-generate strategies from templates
    """

    def __init__(self, templates_path: str = None):
        """
        Initialize generator

        Args:
            templates_path: Path to indicator templates JSON
        """
        if templates_path is None:
            # Default path
            base_path = Path(__file__).parent.parent
            templates_path = base_path / 'templates' / 'indicator_templates.json'

        # Load templates
        with open(templates_path, 'r') as f:
            self.templates = json.load(f)

        # Define operators for entry conditions
        self.operators = ['cross_above', 'cross_below', '>', '<', '>=', '<=']
        self.logic_operators = ['AND', 'OR']

    def generate(self, template_name: str = 'random') -> Dict:
        """
        Generate a random strategy

        Args:
            template_name: Name of template or 'random'

        Returns:
            Strategy configuration dict
        """
        # Select template
        if template_name == 'random':
            template_name = random.choice(list(self.templates.keys()))

        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        # Base strategy structure
        strategy = {
            'name': f'Auto_{template_name}_{random.randint(1000, 9999)}',
            'description': f'Auto-generated from {template["name"]} template',
            'indicators': template['indicators'],
            'entry_conditions': {
                'long': self._generate_entry_conditions(template['indicators'], 'long'),
                'short': self._generate_entry_conditions(template['indicators'], 'short')
            },
            'exit_rules': {
                'long': self._generate_exit_rules(),
                'short': self._generate_exit_rules()
            },
            'risk_management': {
                'max_positions': 1,
                'position_size_pct': 10,
                'max_daily_loss': 50,
                'trading_hours': {
                    'start': '09:00',
                    'end': '14:30'
                }
            }
        }

        return strategy

    def _generate_entry_conditions(self, indicators: List[Dict], direction: str) -> List[Dict]:
        """
        Generate random entry conditions

        Args:
            indicators: List of indicators from template
            direction: 'long' or 'short'

        Returns:
            List of entry condition groups
        """
        # Number of condition groups (1-2)
        num_groups = random.randint(1, 2)

        groups = []
        for i in range(num_groups):
            # Number of conditions per group (1-3)
            num_conditions = random.randint(1, 3)

            conditions = []
            used_indicators = []

            for j in range(num_conditions):
                # Select random indicator (avoid duplicates in same group)
                available_indicators = [ind for ind in indicators if ind['id'] not in used_indicators]
                if not available_indicators:
                    break

                indicator = random.choice(available_indicators)
                used_indicators.append(indicator['id'])

                # Select operator
                operator = random.choice(self.operators)

                # Select right operand (another indicator or price)
                right_operands = ['close', 'open', 'high', 'low']
                other_indicators = [ind['id'] for ind in indicators if ind['id'] != indicator['id']]
                right_operands.extend(other_indicators[:5])  # Limit to avoid too many choices

                right = random.choice(right_operands)

                # Logic operator
                logic = random.choice(self.logic_operators) if j < num_conditions - 1 else 'AND'

                condition = {
                    'left': indicator['id'],
                    'leftOffset': 0,
                    'operator': operator,
                    'right': right,
                    'rightOffset': 0,
                    'logic': logic
                }

                conditions.append(condition)

            if conditions:
                groups.append({
                    'name': f'{direction.capitalize()}_{i+1}',
                    'conditions': conditions
                })

        return groups

    def _generate_exit_rules(self) -> Dict:
        """
        Generate random exit rules

        Returns:
            Exit rules dict
        """
        # Random TP/SL values
        num_rules = random.randint(2, 4)

        tp_sl_table = []
        current_profit = 0

        for i in range(num_rules):
            # Profit range
            range_size = random.randint(2, 5)
            profit_range = [current_profit, current_profit + range_size]

            # TP/SL values
            tp = round(random.uniform(3, 15), 1)
            sl = round(random.uniform(2, 10), 1)
            trailing = round(random.uniform(1, 8), 1)

            tp_sl_table.append({
                'profit_range': profit_range,
                'tp': tp,
                'sl': sl,
                'trailing': trailing
            })

            current_profit += range_size

        return {
            'dynamic_tp_sl': True,
            'time_exit': '14:30',
            'tp_sl_table': tp_sl_table
        }

    def generate_batch(self, count: int, template_name: str = 'random') -> List[Dict]:
        """
        Generate multiple strategies

        Args:
            count: Number of strategies to generate
            template_name: Template to use or 'random'

        Returns:
            List of strategy configurations
        """
        strategies = []

        for i in range(count):
            try:
                # Use random template if specified
                current_template = template_name
                if template_name == 'random':
                    current_template = random.choice(list(self.templates.keys()))

                strategy = self.generate(current_template)
                strategies.append(strategy)

            except Exception as e:
                print(f"Error generating strategy {i+1}: {e}")
                continue

        return strategies

    def modify_strategy(self,
                       current_strategy: Dict,
                       long_signals: int = 2,
                       short_signals: int = 2,
                       indicators_per_signal: int = 2,
                       profit_levels: int = 4,
                       profit_step: int = 3,
                       keep_indicators: bool = True,
                       randomize_tpsl: bool = True) -> Dict:
        """
        Modify existing strategy with new random entry conditions and TP/SL

        Args:
            current_strategy: Current strategy configuration
            long_signals: Number of long entry condition groups
            short_signals: Number of short entry condition groups
            indicators_per_signal: Number of indicators per signal (connected with AND)
            profit_levels: Number of profit levels in TP/SL table
            profit_step: Step size between profit ranges
            keep_indicators: Keep existing indicators or generate new ones
            randomize_tpsl: Randomize TP/SL values

        Returns:
            Modified strategy configuration
        """
        # Use existing indicators or current strategy indicators
        indicators = current_strategy.get('indicators', []) if keep_indicators else []

        # Calculate how many indicators we need
        total_signals = long_signals + short_signals
        min_indicators_needed = min(indicators_per_signal, 10)  # Cap at 10 to avoid too many

        if len(indicators) < min_indicators_needed:
            # Need to add more indicators
            print(f"📊 Current indicators: {len(indicators)}, need at least: {min_indicators_needed}")

            # Generate various indicators to choose from
            indicator_templates = [
                {'id': 'ema_5', 'type': 'EMA', 'params': {'period': 5}},
                {'id': 'ema_10', 'type': 'EMA', 'params': {'period': 10}},
                {'id': 'ema_20', 'type': 'EMA', 'params': {'period': 20}},
                {'id': 'ema_50', 'type': 'EMA', 'params': {'period': 50}},
                {'id': 'ema_100', 'type': 'EMA', 'params': {'period': 100}},
                {'id': 'ema_200', 'type': 'EMA', 'params': {'period': 200}},
                {'id': 'sma_20', 'type': 'SMA', 'params': {'period': 20}},
                {'id': 'sma_50', 'type': 'SMA', 'params': {'period': 50}},
                {'id': 'rsi_14', 'type': 'RSI', 'params': {'period': 14}},
                {'id': 'rsi_21', 'type': 'RSI', 'params': {'period': 21}},
            ]

            # Get existing indicator IDs
            existing_ids = {ind['id'] for ind in indicators}

            # Add indicators until we have enough
            for template in indicator_templates:
                if len(indicators) >= min_indicators_needed:
                    break
                if template['id'] not in existing_ids:
                    indicators.append(template)
                    print(f"   Added indicator: {template['id']}")

        print(f"✅ Total indicators available: {len(indicators)}")

        # Generate new entry conditions
        long_entries = []
        for i in range(long_signals):
            conditions = self._generate_single_condition_group(indicators, 'long', i+1, indicators_per_signal)
            if conditions:
                long_entries.append(conditions)

        short_entries = []
        for i in range(short_signals):
            conditions = self._generate_single_condition_group(indicators, 'short', i+1, indicators_per_signal)
            if conditions:
                short_entries.append(conditions)

        # Generate new TP/SL tables
        long_tpsl = self._generate_tpsl_table(profit_levels, profit_step, randomize_tpsl)
        short_tpsl = self._generate_tpsl_table(profit_levels, profit_step, randomize_tpsl)

        # Build modified strategy
        modified_strategy = {
            'name': current_strategy.get('name', 'Modified Strategy'),
            'description': current_strategy.get('description', 'Auto-modified strategy'),
            'indicators': indicators,
            'entry_conditions': {
                'long': long_entries,
                'short': short_entries
            },
            'exit_rules': {
                'long': {
                    'dynamic_tp_sl': True,
                    'time_exit': '14:30',
                    'tp_sl_table': long_tpsl
                },
                'short': {
                    'dynamic_tp_sl': True,
                    'time_exit': '14:30',
                    'tp_sl_table': short_tpsl
                }
            },
            'risk_management': current_strategy.get('risk_management', {
                'max_positions': 1,
                'position_size_pct': 10,
                'max_daily_loss': 50,
                'trading_hours': {
                    'start': '09:00',
                    'end': '14:30'
                }
            })
        }

        return modified_strategy

    def _generate_single_condition_group(self, indicators: List[Dict], direction: str, group_num: int, num_indicators: int = 2) -> Dict:
        """
        Generate a single condition group with specified number of indicators

        Args:
            indicators: List of available indicators
            direction: 'long' or 'short'
            group_num: Group number for naming
            num_indicators: Number of indicators to use (connected with AND)
        """
        num_conditions = min(num_indicators, len(indicators))  # Can't use more indicators than available
        conditions = []
        used_indicators = []

        for j in range(num_conditions):
            available_indicators = [ind for ind in indicators if ind['id'] not in used_indicators]
            if not available_indicators:
                break

            indicator = random.choice(available_indicators)
            used_indicators.append(indicator['id'])

            operator = random.choice(self.operators)

            right_operands = ['close', 'open', 'high', 'low']
            other_indicators = [ind['id'] for ind in indicators if ind['id'] != indicator['id']]
            right_operands.extend(other_indicators[:5])
            right = random.choice(right_operands)

            # All conditions connected with AND logic
            logic = 'AND'

            condition = {
                'left': indicator['id'],
                'leftOffset': 0,
                'operator': operator,
                'right': right,
                'rightOffset': 0,
                'logic': logic
            }

            conditions.append(condition)

        if conditions:
            # Use proper naming convention: Buy1, Buy2 for long; Short1, Short2 for short
            signal_name = f'Buy{group_num}' if direction == 'long' else f'Short{group_num}'
            return {
                'name': signal_name,
                'conditions': conditions
            }
        return None

    def _generate_tpsl_table(self, levels: int, step: int, randomize: bool) -> List[Dict]:
        """Generate TP/SL table with specified levels and step size"""
        tp_sl_table = []
        current_profit = 0

        for i in range(levels):
            profit_range = [current_profit, current_profit + step]

            if randomize:
                tp = round(random.uniform(3, 15), 1)
                sl = round(random.uniform(2, 10), 1)
                trailing = round(random.uniform(1, 8), 1)
            else:
                # Use fixed values that scale with profit level
                tp = round(5 + i * 2, 1)
                sl = round(3 + i * 0.5, 1)
                trailing = round(2 + i * 0.5, 1)

            tp_sl_table.append({
                'profit_range': profit_range,
                'tp': tp,
                'sl': sl,
                'trailing': trailing
            })

            current_profit += step

        return tp_sl_table
