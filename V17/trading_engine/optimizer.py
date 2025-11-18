"""
Genetic Algorithm Optimizer
Optimizes strategy parameters using genetic algorithms
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Callable
from copy import deepcopy
from .strategy import Strategy
from .backtest_engine import BacktestEngine


class GeneticOptimizer:
    """
    Genetic Algorithm for strategy parameter optimization
    """
    
    def __init__(self,
                 strategy_template: Strategy,
                 data: Dict[str, np.ndarray],
                 population_size: int = 50,
                 generations: int = 20,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.7,
                 elitism_pct: float = 0.1):
        """
        Initialize optimizer
        
        Args:
            strategy_template: Base strategy to optimize
            data: Historical data for backtesting
            population_size: Number of individuals per generation
            generations: Number of generations to evolve
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
            elitism_pct: Percentage of best individuals to keep
        """
        self.strategy_template = strategy_template
        self.data = data
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_count = int(population_size * elitism_pct)
        
        self.param_ranges = {}
        self.population = []
        self.best_individual = None
        self.best_fitness = -float('inf')
        self.history = []
    
    def add_parameter(self, 
                     param_path: str,
                     min_value: float,
                     max_value: float,
                     step: float = 1.0,
                     param_type: str = 'int'):
        """
        Add parameter to optimize
        
        Args:
            param_path: Path to parameter in strategy config (e.g., "indicators.0.params.period")
            min_value: Minimum value
            max_value: Maximum value
            step: Step size for discrete parameters
            param_type: 'int' or 'float'
        """
        self.param_ranges[param_path] = {
            'min': min_value,
            'max': max_value,
            'step': step,
            'type': param_type
        }
        print(f"  Added parameter: {param_path} [{min_value}, {max_value}]")
    
    def _create_individual(self) -> Dict:
        """Create random individual (parameter set)"""
        individual = {}
        for param_path, param_range in self.param_ranges.items():
            if param_range['type'] == 'int':
                value = random.randint(
                    int(param_range['min']),
                    int(param_range['max'])
                )
            else:
                value = random.uniform(param_range['min'], param_range['max'])
            
            individual[param_path] = value
        
        return individual
    
    def _apply_parameters(self, strategy: Strategy, individual: Dict) -> Strategy:
        """Apply parameter values to strategy"""
        config = deepcopy(strategy.config)
        
        for param_path, value in individual.items():
            # Parse path (e.g., "indicators.0.params.period")
            keys = param_path.split('.')
            
            # Navigate to nested dict
            current = config
            for key in keys[:-1]:
                if key.isdigit():
                    current = current[int(key)]
                else:
                    current = current[key]
            
            # Set value
            last_key = keys[-1]
            if last_key.isdigit():
                current[int(last_key)] = value
            else:
                current[last_key] = value
        
        return Strategy(strategy_json=config)
    
    def _fitness_function(self, individual: Dict) -> float:
        """
        Calculate fitness of individual
        
        Args:
            individual: Parameter set
        
        Returns:
            Fitness score (higher is better)
        """
        try:
            # Create strategy with these parameters
            strategy = self._apply_parameters(self.strategy_template, individual)
            
            # Run backtest
            engine = BacktestEngine(strategy)
            results = engine.run(self.data)
            
            # Fitness = combination of return and win rate
            # You can customize this formula
            total_return = results['total_return']
            win_rate = results['win_rate']
            profit_factor = results['profit_factor']
            max_drawdown = abs(results['max_drawdown'])
            
            # Weighted fitness score
            fitness = (
                total_return * 0.4 +
                win_rate * 0.3 +
                profit_factor * 10 * 0.2 -
                max_drawdown * 0.1
            )
            
            return fitness
            
        except Exception as e:
            print(f"  ✗ Error evaluating individual: {e}")
            return -float('inf')
    
    def _initialize_population(self):
        """Create initial population"""
        print(f"\n🧬 Initializing population ({self.population_size} individuals)...")
        self.population = []
        
        for i in range(self.population_size):
            individual = self._create_individual()
            fitness = self._fitness_function(individual)
            
            self.population.append({
                'params': individual,
                'fitness': fitness
            })
            
            print(f"  Individual {i+1}/{self.population_size} | Fitness: {fitness:.2f}")
        
        # Sort by fitness
        self.population.sort(key=lambda x: x['fitness'], reverse=True)
        
        # Update best
        if self.population[0]['fitness'] > self.best_fitness:
            self.best_fitness = self.population[0]['fitness']
            self.best_individual = self.population[0]['params']
    
    def _selection(self) -> Tuple[Dict, Dict]:
        """Select two parents using tournament selection"""
        tournament_size = 5
        
        # Tournament 1
        tournament1 = random.sample(self.population, tournament_size)
        parent1 = max(tournament1, key=lambda x: x['fitness'])
        
        # Tournament 2
        tournament2 = random.sample(self.population, tournament_size)
        parent2 = max(tournament2, key=lambda x: x['fitness'])
        
        return parent1['params'], parent2['params']
    
    def _crossover(self, parent1: Dict, parent2: Dict) -> Tuple[Dict, Dict]:
        """Crossover two parents to create offspring"""
        if random.random() > self.crossover_rate:
            return deepcopy(parent1), deepcopy(parent2)
        
        child1 = {}
        child2 = {}
        
        for param_path in parent1.keys():
            if random.random() < 0.5:
                child1[param_path] = parent1[param_path]
                child2[param_path] = parent2[param_path]
            else:
                child1[param_path] = parent2[param_path]
                child2[param_path] = parent1[param_path]
        
        return child1, child2
    
    def _mutate(self, individual: Dict) -> Dict:
        """Mutate individual"""
        mutated = deepcopy(individual)
        
        for param_path, value in mutated.items():
            if random.random() < self.mutation_rate:
                param_range = self.param_ranges[param_path]
                
                if param_range['type'] == 'int':
                    # Random mutation within range
                    mutated[param_path] = random.randint(
                        int(param_range['min']),
                        int(param_range['max'])
                    )
                else:
                    # Gaussian mutation
                    sigma = (param_range['max'] - param_range['min']) * 0.1
                    new_value = value + random.gauss(0, sigma)
                    new_value = np.clip(new_value, param_range['min'], param_range['max'])
                    mutated[param_path] = new_value
        
        return mutated
    
    def optimize(self) -> Dict:
        """
        Run genetic algorithm optimization
        
        Returns:
            Best parameters found
        """
        print(f"\n🚀 Starting genetic algorithm optimization")
        print(f"   Population: {self.population_size}")
        print(f"   Generations: {self.generations}")
        print(f"   Mutation Rate: {self.mutation_rate}")
        print(f"   Crossover Rate: {self.crossover_rate}")
        
        # Initialize population
        self._initialize_population()
        
        # Evolution loop
        for gen in range(self.generations):
            print(f"\n📊 Generation {gen + 1}/{self.generations}")
            
            # Create new population
            new_population = []
            
            # Elitism: Keep best individuals
            new_population.extend(self.population[:self.elitism_count])
            print(f"  Elite individuals: {self.elitism_count}")
            
            # Generate offspring
            while len(new_population) < self.population_size:
                # Selection
                parent1, parent2 = self._selection()
                
                # Crossover
                child1, child2 = self._crossover(parent1, parent2)
                
                # Mutation
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)
                
                # Evaluate fitness
                fitness1 = self._fitness_function(child1)
                fitness2 = self._fitness_function(child2)
                
                new_population.append({'params': child1, 'fitness': fitness1})
                if len(new_population) < self.population_size:
                    new_population.append({'params': child2, 'fitness': fitness2})
            
            # Replace population
            self.population = new_population
            self.population.sort(key=lambda x: x['fitness'], reverse=True)
            
            # Update best
            if self.population[0]['fitness'] > self.best_fitness:
                self.best_fitness = self.population[0]['fitness']
                self.best_individual = self.population[0]['params']
                print(f"  🎯 New best fitness: {self.best_fitness:.2f}")
            
            # Statistics
            avg_fitness = np.mean([ind['fitness'] for ind in self.population])
            print(f"  Best: {self.population[0]['fitness']:.2f} | Avg: {avg_fitness:.2f} | Worst: {self.population[-1]['fitness']:.2f}")
            
            # Store history
            self.history.append({
                'generation': gen + 1,
                'best_fitness': self.population[0]['fitness'],
                'avg_fitness': avg_fitness,
                'worst_fitness': self.population[-1]['fitness']
            })
        
        print(f"\n✅ Optimization complete!")
        print(f"   Best fitness: {self.best_fitness:.2f}")
        print(f"   Best parameters:")
        for param, value in self.best_individual.items():
            print(f"     {param}: {value}")
        
        return {
            'best_params': self.best_individual,
            'best_fitness': self.best_fitness,
            'history': self.history,
            'final_population': self.population
        }
    
    def get_optimized_strategy(self) -> Strategy:
        """Get strategy with optimized parameters"""
        if not self.best_individual:
            raise ValueError("No optimization run yet. Call optimize() first.")
        
        return self._apply_parameters(self.strategy_template, self.best_individual)
