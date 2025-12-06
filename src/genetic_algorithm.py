import os
import sys
import time
import random
import numpy as np
from joblib import Parallel, delayed

from config import Config as c
from simulator import Simulator
from crossover import Crossover
from mutation import Mutation

class GA:
    """Genetic Algorithm for traffic signal optimization"""

    def __init__(self):
        pass

    def create_initial_population(self, base_gene):
        """Create initial population with some diversity"""
        population = [base_gene]
        
        generated = set()
        generated.add(tuple(base_gene)) 
        
        attempts = 0
        while len(population) < c.POPULATION and attempts < c.MAX_INIT_ATTEMPTS:
            gene = []
            for base_duration in base_gene:
                variation = random.uniform(c.INIT_VARIATION_MIN, c.INIT_VARIATION_MAX)
                new_duration = int(base_duration * variation)
                new_duration = max(c.MIN_GREEN, min(c.MAX_GREEN, new_duration))
                gene.append(new_duration)
            
            gene_tuple = tuple(gene)
            if gene_tuple not in generated:
                generated.add(gene_tuple)
                population.append(gene)
            
            attempts += 1
        
        # Fill remaining slots with random genes
        while len(population) < c.POPULATION:
            gene = [random.randint(c.MIN_GREEN, c.MAX_GREEN) for _ in range(c.NUM_SIGNALS)]
            population.append(gene)
        
        return population
    
    def tournament_selection(self, fitnesses):
        """Tournament selection for parent selection"""
        selected_indices = []
        
        for _ in range(c.SELECT_COUNT):
            tournament_indices = random.sample(range(len(fitnesses)), c.TOURNAMENT_SIZE)
            tournament_fitness = [fitnesses[i] for i in tournament_indices]
            winner_idx = tournament_indices[tournament_fitness.index(min(tournament_fitness))]
            selected_indices.append(winner_idx)
        
        return selected_indices

    def run_ga(self, base_gene):
        """Main GA execution with full logging"""
        simulator = Simulator()
        history = {
            'baseline': {
                'gene': base_gene,
                'waiting_time': None,
                'queue_length': None,
                'delay': None
            },
            'generations': []
        }
        
        # Evaluate baseline
        baseline_stats = simulator.simulate(base_gene)
        history['baseline'].update({
            'waiting_time': baseline_stats['average_waiting_time'],
            'queue_length': baseline_stats['average_queue_length'],
            'delay': baseline_stats['average_time_loss']
        })
        
        baseline_fitness = baseline_stats['average_time_loss']
        population = self.create_initial_population(base_gene)
        
        best_genes = None
        best_fitness = float('inf')
        
        for generation in range(c.GENERATIONS):
            start_time = time.time()

            print(f"Generation ({generation})")

            # Generation tracking
            gen_history = {
                'generation': generation,
                'genes': [],
                'best_idx': None,
                'best_gene': None,
                'best_fitness': None,
                'avg_fitness': None,
                'delays': [],
                'waiting_times': [],
                'queue_lengths': []
            }
            
            # EVALUATION
            fitnesses = []
            for idx, individual in enumerate(population):
                stats = simulator.simulate(individual)
                fitness = stats['average_time_loss']
                fitnesses.append(fitness)
                
                # Store data
                gen_history['genes'].append(individual.copy())
                gen_history['delays'].append(stats['average_time_loss'])
                gen_history['waiting_times'].append(stats['average_waiting_time'])
                gen_history['queue_lengths'].append(stats['average_queue_length'])

                # Log individual
                print(f"individual ({idx}); gene: {individual}; delay: {stats['average_time_loss']:.2f}s")
            
            # Update generation history
            gen_history['best_idx'] = fitnesses.index(min(fitnesses))
            gen_history['best_gene'] = population[gen_history['best_idx']].copy()
            gen_history['best_fitness'] = fitnesses[gen_history['best_idx']]
            gen_history['avg_fitness'] = sum(fitnesses) / len(fitnesses)
            history['generations'].append(gen_history)

            # Track overall best
            gen_best_idx = gen_history['best_idx']
            gen_best_genes = population[gen_best_idx]
            gen_best_fitness = fitnesses[gen_best_idx]
            
            if gen_best_fitness < best_fitness:
                best_genes = gen_best_genes.copy()
                best_fitness = gen_best_fitness

            # SELECTION
            selected_indices = self.tournament_selection(fitnesses)

            # CROSSOVER & MUTATION
            children = []
            for i in range(0, c.POPULATION - 1, 2):
                parent1 = population[selected_indices[i]]
                parent2 = population[selected_indices[i + 1]]
                
                child1, child2 = Crossover.single_point(parent1, parent2)
                
                child1 = Mutation.gaussian_mutate(child1, mutation_rate=c.MUTATION_RATE)
                child2 = Mutation.gaussian_mutate(child2, mutation_rate=c.MUTATION_RATE)
                
                children.extend([child1, child2])

            # Handle odd population
            if c.POPULATION % 2 == 1:
                children.append(population[selected_indices[-1]])

            # ELITISM
            children[0] = gen_best_genes.copy()
            random.shuffle(children)
            
            # NEXT GENERATION
            population = children

            # LOGGING
            avg_fitness = sum(fitnesses) / len(fitnesses)
            improvement = ((baseline_fitness - best_fitness) / baseline_fitness * 100)
            print(f"Generation ({generation}); Best: {gen_best_genes}, "
                  f"Delay: {gen_best_fitness:.2f}s ({improvement:+.1f}%), "
                  f"Avg: {avg_fitness:.2f}s\n")
            
            # TIMING
            elapsed = time.time() - start_time
            print(f"elapsed time: {elapsed:.2f}s")

        return best_genes, best_fitness, baseline_fitness, history
    
    def run_ga_parallel(self, base_gene, n_jobs=-1):
        """Parallel GA implementation using Joblib"""
        # Initialize for consistency with other methods
        baseline_fitness = Simulator().simulate(base_gene)['average_time_loss']
        print(f"Baseline fitness: {baseline_fitness:.2f}s")

        population = self.create_initial_population(base_gene)
        best_genes = None
        best_fitness = float('inf')
        
        for generation in range(c.GENERATIONS):
            start_time = time.time()

            print(f"Generation ({generation}): ", end="")

            # PARALLEL FITNESS EVALUATION
            fitnesses = Parallel(n_jobs=n_jobs)(
                delayed(self._evaluate_fitness)(ind) for ind in population
            )
            
            # Track best
            gen_best_idx = fitnesses.index(min(fitnesses))
            gen_best_genes = population[gen_best_idx]
            gen_best_fitness = fitnesses[gen_best_idx]
            
            if gen_best_fitness < best_fitness:
                best_genes = gen_best_genes.copy()
                best_fitness = gen_best_fitness

            # SELECTION
            selected_indices = self.tournament_selection(fitnesses)

            # CROSSOVER & MUTATION
            children = []
            for i in range(0, c.POPULATION - 1, 2):
                parent1 = population[selected_indices[i]]
                parent2 = population[selected_indices[i + 1]]
                
                child1, child2 = Crossover.single_point(parent1, parent2)
                
                child1 = Mutation.gaussian_mutate(child1, mutation_rate=c.MUTATION_RATE)
                child2 = Mutation.gaussian_mutate(child2, mutation_rate=c.MUTATION_RATE)
                
                children.extend([child1, child2])

            # Handle odd population
            if c.POPULATION % 2 == 1:
                children.append(population[selected_indices[-1]])

            # ELITISM
            children[0] = gen_best_genes.copy()
            random.shuffle(children)
            
            # NEXT GENERATION
            population = children

            # LOGGING
            avg_fitness = sum(fitnesses) / len(fitnesses)
            improvement = ((baseline_fitness - best_fitness) / baseline_fitness * 100)
            print(f"Best: {best_fitness:.2f}s ({improvement:+.1f}%), "
                  f"Avg: {avg_fitness:.2f}s ", end="")

            # TIMING
            elapsed = time.time() - start_time
            print(f"elapsed time: {elapsed:.2f}s")

        return best_genes, best_fitness, baseline_fitness

    def _evaluate_fitness(self, individual):
        """Helper for parallel fitness evaluation"""
        return Simulator().simulate(individual)['average_time_loss']
    
    def run_ga_parallel_with_stats(self, base_gene, n_jobs=-1):
        """Parallel GA with comprehensive statistics"""
        
        # Evaluate baseline
        baseline_fitness = Simulator().simulate(base_gene)['average_time_loss']
        print(f"Baseline fitness: {baseline_fitness:.2f}s")
        
        # Initialize population and tracking
        population = self.create_initial_population(base_gene)
        best_genes = None
        best_fitness = float('inf')
        
        # Initialize history
        history = {
            'baseline_fitness': baseline_fitness,
            'generations': []
        }
        
        for generation in range(c.GENERATIONS):
            start_time = time.time()

            print(f"Generation ({generation}): ", end="")

            # PARALLEL FITNESS EVALUATION
            fitnesses = Parallel(n_jobs=n_jobs)(
                delayed(self._evaluate_fitness)(ind) for ind in population
            )
            
            # Calculate statistics
            gen_best_idx = fitnesses.index(min(fitnesses))
            gen_best_genes = population[gen_best_idx]
            gen_best_fitness = fitnesses[gen_best_idx]
            
            # Update overall best
            if gen_best_fitness < best_fitness:
                best_genes = gen_best_genes.copy()
                best_fitness = gen_best_fitness
            
            # Population diversity metrics
            unique_genes = len(set(tuple(g) for g in population))
            diversity = unique_genes / len(population)
            
            # Gene-wise statistics
            gene_stats = []
            if population:
                for i in range(len(population[0])):
                    gene_values = [ind[i] for ind in population]
                    gene_stats.append({
                        'index': i,
                        'mean': sum(gene_values) / len(gene_values),
                        'min': min(gene_values),
                        'max': max(gene_values),
                        'std': np.std(gene_values) if len(gene_values) > 1 else 0
                    })
            
            # Store generation stats
            history['generations'].append({
                'generation': generation,
                'best_gene': gen_best_genes.copy(),
                'best_fitness': gen_best_fitness,
                'avg_fitness': sum(fitnesses) / len(fitnesses),
                'fitness_std': np.std(fitnesses) if len(fitnesses) > 1 else 0,
                'diversity': diversity,
                'gene_stats': gene_stats
            })
            
            # SELECTION
            selected_indices = self.tournament_selection(fitnesses)

            # CROSSOVER & MUTATION
            children = []
            for i in range(0, c.POPULATION - 1, 2):
                parent1 = population[selected_indices[i]]
                parent2 = population[selected_indices[i + 1]]
                
                child1, child2 = Crossover.single_point(parent1, parent2)
                
                # Decaying Mutation
                curr_mutation_rate = c.MUTATION_RATE * (c.MUTATION_DECAY ** generation)
                curr_mutation_rate = max(c.MIN_MUTATION_RATE, curr_mutation_rate)

                child1 = Mutation.gaussian_mutate(child1, mutation_rate=curr_mutation_rate, sigma=c.MUTATION_SIGMA)
                child2 = Mutation.gaussian_mutate(child2, mutation_rate=curr_mutation_rate, sigma=c.MUTATION_SIGMA)
                
                children.extend([child1, child2])

            # Handle odd population
            if c.POPULATION % 2 == 1:
                children.append(population[selected_indices[-1]])

            # ELITISM
            children[0] = gen_best_genes.copy()
            random.shuffle(children)
            
            # NEXT GENERATION
            population = children

            # LOGGING
            avg_fitness = sum(fitnesses) / len(fitnesses)
            improvement = ((baseline_fitness - best_fitness) / baseline_fitness * 100)
            print(f"Best: {best_fitness:.2f}s ({improvement:+.1f}%), "
                  f"Avg: {avg_fitness:.2f}s, Diversity: {diversity:.2f} ", end="")

            # TIMING
            elapsed = time.time() - start_time
            print(f"elapsed time: {elapsed:.2f}s")
            
        return best_genes, best_fitness, baseline_fitness, history