import random
import math
import copy

def initialize_candidate(user_cats, extra_cats, min_max):
    candidate = {"user": {}, "extra": {}}
    # For each user category, allocate a random value between min and max.
    for cat in user_cats:
        mi, ma = min_max[cat]
        candidate["user"][cat] = random.uniform(mi, ma)
    # For extra categories, randomly decide to include (50% chance).
    for cat in extra_cats:
        if random.random() < 0.5:
            mi, ma = min_max[cat]
            candidate["extra"][cat] = random.uniform(mi, ma)
        else:
            candidate["extra"][cat] = 0.0  # not included
    return candidate

def total_cost(candidate):
    return sum(candidate["user"].values()) + sum(candidate["extra"].values())

def fitness(candidate, avg_prices, min_max, total_budget, penalty_factor=1e8, extra_reward=100):
    cost = total_cost(candidate)
    fit = 0.0
    # Heavy penalty if over budget:
    if cost > total_budget:
        fit += penalty_factor * (cost - total_budget)
    # For user categories: aim for allocation close to the average
    for cat, alloc in candidate["user"].items():
        avg = avg_prices.get(cat, alloc)
        fit += (alloc - avg) ** 2
    # For extra categories: if included, add deviation and reward inclusion.
    for cat, alloc in candidate["extra"].items():
        if alloc > 0:
            avg = avg_prices.get(cat, alloc)
            fit += (alloc - avg) ** 2 - extra_reward
    return fit

def mutate(candidate, user_cats, extra_cats, min_max, mutation_rate=0.2, mutation_scale=0.1):
    new_candidate = copy.deepcopy(candidate)
    for cat in user_cats:
        if random.random() < mutation_rate:
            mi, ma = min_max[cat]
            current = new_candidate["user"][cat]
            noise = random.gauss(0, mutation_scale * (ma - mi))
            new_val = current + noise
            new_candidate["user"][cat] = min(max(new_val, mi), ma)
    for cat in extra_cats:
        if random.random() < mutation_rate:
            mi, ma = min_max[cat]
            if new_candidate["extra"][cat] == 0:
                new_candidate["extra"][cat] = random.uniform(mi, ma)
            else:
                if random.random() < 0.5:
                    current = new_candidate["extra"][cat]
                    noise = random.gauss(0, mutation_scale * (ma - mi))
                    new_val = current + noise
                    new_candidate["extra"][cat] = min(max(new_val, mi), ma)
                else:
                    new_candidate["extra"][cat] = 0.0
    return new_candidate

def crossover(parent1, parent2, user_cats, extra_cats):
    child1 = {"user": {}, "extra": {}}
    child2 = {"user": {}, "extra": {}}
    for cat in user_cats:
        if random.random() < 0.5:
            child1["user"][cat] = parent1["user"][cat]
            child2["user"][cat] = parent2["user"][cat]
        else:
            child1["user"][cat] = parent2["user"][cat]
            child2["user"][cat] = parent1["user"][cat]
    for cat in extra_cats:
        if random.random() < 0.5:
            child1["extra"][cat] = parent1["extra"][cat]
            child2["extra"][cat] = parent2["extra"][cat]
        else:
            child1["extra"][cat] = parent2["extra"][cat]
            child2["extra"][cat] = parent1["extra"][cat]
    return child1, child2

def genetic_algorithm(user_cats, extra_cats, avg_prices, min_max, total_budget, population_size=50, generations=100):
    population = [initialize_candidate(user_cats, extra_cats, min_max) for _ in range(population_size)]
    best = None
    for gen in range(generations):
        fitnesses = [fitness(c, avg_prices, min_max, total_budget) for c in population]
        gen_best = min(population, key=lambda c: fitness(c, avg_prices, min_max, total_budget))
        if best is None or fitness(gen_best, avg_prices, min_max, total_budget) < fitness(best, avg_prices, min_max, total_budget):
            best = gen_best
        new_population = []
        while len(new_population) < population_size:
            tournament = random.sample(population, 3)
            parent1 = min(tournament, key=lambda c: fitness(c, avg_prices, min_max, total_budget))
            tournament = random.sample(population, 3)
            parent2 = min(tournament, key=lambda c: fitness(c, avg_prices, min_max, total_budget))
            child1, child2 = crossover(parent1, parent2, user_cats, extra_cats)
            child1 = mutate(child1, user_cats, extra_cats, min_max)
            child2 = mutate(child2, user_cats, extra_cats, min_max)
            new_population.extend([child1, child2])
        population = new_population[:population_size]
    population.sort(key=lambda c: fitness(c, avg_prices, min_max, total_budget))
    return population[:5]
