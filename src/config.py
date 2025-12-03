# GA configs

class Config:

    # GA
    POPULATION = 5
    GENERATIONS = 5
    CROSSOVER_METHOD = "uniform"
    SELECTION_METHOD = "tournament"

    # Simulation
    MAX_EVAL_STEPS = 900
    PATH_TO_NETWORK = "data/6l_4w_4p.net.xml"
    PATH_TO_ROUTE = "data/6l_4w_4p.rou.xml"
    PATH_TO_SUMOCONFIG = "data/6l_4w_4p.sumocfg"
    JUNCTION_ID = "j1"