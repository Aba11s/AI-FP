# crossover clas

import random

class Crossover:

    def single_point(parent1, parent2):
        point = random.randint(1, len(parent1) - 1)
    
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        
        return child1, child2
    
    def two_point(parent1, parent2):
        point1 = random.randint(1, len(parent1) - 2)
        point2 = random.randint(point1 + 1, len(parent1) - 1)
        
        child1 = (parent1[:point1] + 
                parent2[point1:point2] + 
                parent1[point2:])
        
        child2 = (parent2[:point1] + 
                parent1[point1:point2] + 
                parent2[point2:])
        
        return child1, child2
    
    def uniform(parent1, parent2):
        child1 = []
        child2 = []
        
        for p1, p2 in zip(parent1, parent2):    
            if random.random() < 0.5:
                child1.append(p1)
                child2.append(p2)
            else:
                child1.append(p2)
                child2.append(p1)
        
        return child1, child2
