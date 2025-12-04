import os
import sys
import time
import random
from joblib import Parallel, delayed

from config import Config as c
from simulator import Simulator
from crossover import Crossover
from mutation import Mutation

class GA:

    def __init__(self):
        ...

    def create_initial_population(self, base_gene):
        popsize = c.POPULATION - 1

        population = [base_gene]

        for _ in range(popsize):
            gene = []
            for base_duration in base_gene:
                variation = random.uniform(0.7, 1.3)
                new_duration = int(base_duration * variation)
                new_duration = max(10, min(30, new_duration))
                gene.append(new_duration)
            
            population.append(gene)

        return population
    
    def create_initial_population_diverse(self, base_gene):
        popsize = c.POPULATION - 1
        population = [base_gene]
        
        generated = set()
        generated.add(tuple(base_gene))  # Convert to tuple for hashing
        
        attempts = 0
        while len(population) < c.POPULATION and attempts < 1000:
            gene = []
            for base_green in base_gene:
                variation = random.uniform(0.7, 1.3)
                new_green = int(base_green * variation)
                new_green = max(10, min(30, new_green))
                gene.append(new_green)
            
            gene_tuple = tuple(gene)
            if gene_tuple not in generated:
                generated.add(gene_tuple)
                population.append(gene)
            
            attempts += 1
        
        # If couldn't generate enough unique, fill with random
        while len(population) < c.POPULATION:
            gene = [random.randint(10, 30) for _ in range(4)]
            population.append(gene)
        
        return population
    
    def tournament_selection(self, fitnesses, tournament_size=2, select_count=None):
        if select_count is None:
            select_count = len(fitnesses)
        
        selected_indices = []
        
        for _ in range(select_count):
            # Pick random tournament participants
            tournament_indices = random.sample(range(len(fitnesses)), tournament_size)
            
            # Find the best (lowest fitness for minimization)
            tournament_fitness = [fitnesses[i] for i in tournament_indices]
            winner_idx = tournament_indices[tournament_fitness.index(min(tournament_fitness))]
            
            selected_indices.append(winner_idx)
        
        return selected_indices

    def run_ga(self, gene):

        simulator = Simulator()
        history = {
        'baseline': {
            'gene': gene,
            'waiting_time': None,
            'queue_length': None,
            'delay': None
        },
        'generations': []
        }
        
        # Evaluate baseline
        baseline_stats = simulator.simulate(gene)
        history['baseline'].update({
            'waiting_time': baseline_stats['average_waiting_time'],
            'queue_length': baseline_stats['average_queue_length'],
            'delay': baseline_stats['average_time_loss']
        })
        
        baseline_fitness = baseline_stats['average_time_loss']
        population = self.create_initial_population_diverse(gene)
        
        best_genes = None
        best_fitness = float('inf')
        
        for generation in range(c.GENERATIONS):

            start = time.time()

            print(f"Generation ({generation})")

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
            idx = 0
            for individual in population:
                # LOG #
                print(f"individual ({idx});", end="")

                stats = simulator.simulate(individual)
                fitness = stats['average_time_loss']
                fitnesses.append(fitness)
                
                # Store data
                gen_history['genes'].append(individual.copy())
                gen_history['delays'].append(stats['average_time_loss'])
                gen_history['waiting_times'].append(stats['average_waiting_time'])
                gen_history['queue_lengths'].append(stats['average_queue_length'])

                # LOG #
                print(f"gene: {individual}; delay: {stats['average_time_loss']:.2f}s")

                idx += 1
            
            gen_history['best_idx'] = fitnesses.index(min(fitnesses))
            gen_history['best_gene'] = population[gen_history['best_idx']].copy()
            gen_history['best_fitness'] = fitnesses[gen_history['best_idx']]
            gen_history['avg_fitness'] = sum(fitnesses) / len(fitnesses)
            
            # Store generation
            history['generations'].append(gen_history)

            # TRACK BEST
            gen_best_idx = gen_history['best_idx']
            gen_best_genes = population[gen_best_idx]
            gen_best_fitness = fitnesses[gen_best_idx]
            
            if gen_best_fitness < best_fitness:
                best_genes = gen_best_genes.copy()
                best_fitness = gen_best_fitness

            # TOURNAMENT SELECTION
            selected_indices = self.tournament_selection(fitnesses, select_count=c.POPULATION)

            # CROSSOVER & MUTATION
            children = []
            for i in range(0, c.POPULATION-1, 2):
                parent1 = population[selected_indices[i]]
                parent2 = population[selected_indices[i+1]]
                
                child1, child2 = Crossover.single_point(parent1, parent2)
                
                child1 = Mutation.gaussian_mutate(child1, mutation_rate=0.25)
                child2 = Mutation.gaussian_mutate(child2, mutation_rate=0.25)
                
                children.extend([child1, child2])

            if c.POPULATION % 2 == 1:  # If odd population
                children.append(population[selected_indices[-1]])

            # ADD ELITISM
            children[0] = gen_best_genes.copy()
            
            # SET NEXT GENERATION
            population = children

            # LOGGING
            avg_fitness = sum(fitnesses) / len(fitnesses)
            improvement = ((baseline_fitness - best_fitness) / baseline_fitness * 100)
            print(f"Generation ({generation}); Best: {gen_best_genes}, Delay: {gen_best_fitness:.2f}s ({improvement:+.1f}%), Avg: {avg_fitness:.2f}s\n")
            
            # ELAPSED TIME
            end = time.time()
            print(f"elapsed time: {end-start:.2f}s")

            # END OF LOOP #

        return best_genes, best_fitness, baseline_fitness, history
    

    ## PARALLEL COMPUTING WITH JOBLIB ##
    def run_ga_joblib_simple(self, gene, n_jobs=-1):
        """Super simple Joblib implementation"""

        # Get baseline
        baseline_fitness = Simulator().simulate(gene)['average_time_loss']
        print(f"Baseline fitness: {baseline_fitness:.2f}s")

        population = self.create_initial_population(gene)
        best_genes = None
        best_fitness = float('inf')
        
        for generation in range(c.GENERATIONS):

            start = time.time()

            print(f"Generation ({generation}): ", end="")

            # parrallel fitness evaluation
            fitnesses = Parallel(n_jobs=n_jobs)(
                delayed(self.evaluate_fitness_only)(ind) for ind in population
            )
            
             # TRACK BEST
            gen_best_idx = fitnesses.index(min(fitnesses))
            gen_best_genes = population[gen_best_idx]
            gen_best_fitness = fitnesses[gen_best_idx]
            
            if gen_best_fitness < best_fitness:
                best_genes = gen_best_genes.copy()
                best_fitness = gen_best_fitness

            # TOURNAMENT SELECTION
            selected_indices = self.tournament_selection(fitnesses, select_count=c.POPULATION)

            # CROSSOVER & MUTATION
            children = []
            for i in range(0, c.POPULATION-1, 2):
                parent1 = population[selected_indices[i]]
                parent2 = population[selected_indices[i+1]]
                
                child1, child2 = Crossover.single_point(parent1, parent2)
                
                child1 = Mutation.gaussian_mutate(child1, mutation_rate=0.1)
                child2 = Mutation.gaussian_mutate(child2, mutation_rate=0.1)
                
                children.extend([child1, child2])

            if c.POPULATION % 2 == 1:  # If odd population
                children.append(population[selected_indices[-1]])

            # ADD ELITISM
            children[0] = best_genes.copy()
            
            # SET NEXT GENERATION
            population = children

             # LOGGING
            avg_fitness = sum(fitnesses) / len(fitnesses)
            improvement = ((baseline_fitness - best_fitness) / baseline_fitness * 100)
            print(f"Best: {best_fitness:.2f}s ({improvement:+.1f}%), Avg: {avg_fitness:.2f}s ", end="")

            # ELAPSED TIME
            end = time.time()
            print(f"elapsed time: {end-start:.2f}s")

            # END OF LOOP #
        
        return best_genes, best_fitness, baseline_fitness

    def evaluate_fitness_only(self, individual):
        """Return only fitness for maximum speed"""
        from simulator import Simulator
        return Simulator().simulate(individual)['average_time_loss']


