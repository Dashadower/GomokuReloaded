import numpy
import random
import shelve
import sys
import time
from GeneticAlphaBeta import AlphaBeta

from Agent.AnalyzerOptimized import WinChecker
from Agent.GameBoard import GameBoard

# Genetic Algorithm Approach to adjust weights in FilterStrings.py for Analyzer function
# Refer to FilterStrings.py for more info on weights.
template = [2, 250, 10000, 20]
#          [open2, open3, open4, closed4]

mutation_rate = 10
starting_population = 16
default_generation_deviation = 20

simulations = 5

game_searchrange = 1
game_playdepth = 2


def multiinput(msg):
    print(msg)
    sys.stdout.flush()

def open_traindata():

    pool = []
    data = shelve.open("traindata")
    if data.keys():
        for item in data:
            pool.append(data[item][0])
            generation = data[item][1]
        data.close()
        multiinput("Loaded training data")
    else:
        generation = 1
        for x in range(starting_population):
            generatedchromo = []
            for x in range(4):
                generatedchromo.append(generate_random_gene())
            pool.append(generatedchromo)
        multiinput("Created chromosomes from scratch")
    return pool, generation


def generate_random_gene():
    return round(numpy.random.normal(0.0, default_generation_deviation), 2)


def play_game(c1, c2):
    board = GameBoard(10,10)
    refree = WinChecker(board)

    ai1 = AlphaBeta(board,"black",game_playdepth, game_searchrange,c1)
    ai2 = AlphaBeta(board, "white", game_playdepth,game_searchrange,c2)
    board.addstone((5,5), "black")
    while True:
        if not len(ai2.getopenmoves()) == 0:
            ai2.addaistone(ai2.ChooseMove()[1])
            if refree.check("white"):
                return c2
            else:
                if not len(ai1.getopenmoves()) == 0:
                    ai1.addaistone(ai1.ChooseMove()[1])
                    if refree.check("black"):
                        return c1
                else:
                    return 0
        else:
            return 0


start_chromosomes, generation = open_traindata()
multiinput("START GENES:")
multiinput(start_chromosomes)

def select_opponent(subject, pool, exclusion_pool):
    pool = [item for item in pool if item not in exclusion_pool]
    if len(pool) == 2:
        return pool[0] if pool[0] != subject else pool[1]
    else:
        while True:
            chosen = random.choice(pool)
            if chosen == subject:
                pass
            else:
                return chosen

while True:
    multiinput("****************")
    multiinput("GENERATION "+str(generation))
    start = time.time()
    evaluated_chromosomes = []
    for chromosome in start_chromosomes:
        fitness = 0
        ex_pool = []
        for t in range(simulations):
            opponent = select_opponent(chromosome, start_chromosomes, ex_pool)
            ex_pool.append(opponent)
            result = play_game(chromosome, opponent)
            if result == chromosome: fitness += 1
            elif result == opponent: fitness -= 1
            elif not result: pass
        evaluated_chromosomes.append((chromosome, fitness))
        multiinput("%d of %d chromosomes done simulating"%(len(evaluated_chromosomes), len(start_chromosomes)))
    evaluated_chromosomes = sorted(evaluated_chromosomes, key= lambda x: x[1], reverse=True)
    evaluated_chromosomes = evaluated_chromosomes[:-round(starting_population/2)]
    fresh_chromosome = []
    tmp_list = []
    for x in range(round(starting_population/2)):
        first_chromosome = random.choice(evaluated_chromosomes)[0]
        second_chromosome = select_opponent(first_chromosome, evaluated_chromosomes, [])[0]
        crossover_policy = []
        for y in range(0,4):
            crossover_policy.append(numpy.random.choice([0,1]))
        new_chromosome = []
        gene_index = 0
        for item in crossover_policy:
            mrate = numpy.random.randint(1,mutation_rate+1)
            if mrate == 2:
                new_chromosome.append(generate_random_gene())
                gene_index += 1
            else:
                if item == 0:
                    new_chromosome.append(first_chromosome[gene_index])
                elif item == 1:
                    new_chromosome.append(second_chromosome[gene_index])
                gene_index += 1

        fresh_chromosome.append(new_chromosome)
        tmp_list.append(new_chromosome)

    for item in evaluated_chromosomes:
        tmp_list.append(item[0])
    ncr = 0
    for ch in fresh_chromosome:
        fitness = 0
        ex_pool = []
        for tc in range(simulations):
            opponent = select_opponent(ch, tmp_list, ex_pool)
            ex_pool.append(opponent)
            result = play_game(ch, opponent)
            if result == ch:
                fitness += 1
            elif result == opponent:
                fitness -= 1
            elif not result:
                pass
        evaluated_chromosomes.append((ch, fitness))
        ncr += 1
        multiinput("%d of %d new chromosomes evaluated"%(ncr, len(fresh_chromosome)))
    end = time.time()
    multiinput("*"*10)
    multiinput("Results of Generation" +str(generation))
    evaluated_chromosomes = sorted(evaluated_chromosomes, key=lambda x: x[1], reverse=True)
    for item in evaluated_chromosomes[:5]:
        multiinput(str(item)+"\n")
    multiinput("Duration of generation"+str(generation)+":"+str(end-start))
    start_chromosomes = []
    for hj in evaluated_chromosomes:
        start_chromosomes.append(hj[0])
    generation += 1
    shv = shelve.open("traindata")
    dx = 0
    for n in start_chromosomes:
        shv[str(dx)] = (n, generation)
        dx += 1
    shv.close()





