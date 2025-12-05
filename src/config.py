# GA configs

class Config:

    # GA
    POPULATION = 10
    GENERATIONS = 20
    CROSSOVER_METHOD = "uniform"
    SELECTION_METHOD = "tournament"

    # Simulation
    MAX_EVAL_STEPS = 900
    PATH_TO_NETWORK = "data/6lane4way.net.xml"
    PATH_TO_ROUTE = "data/6lane4way.rou.xml"
    PATH_TO_SUMOCONFIG = "data/6lane4way.sumocfg"
    JUNCTION_ID = "J4"