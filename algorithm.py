import random
import math
import copy

def total_cost(candidate):
    return sum(candidate["user"].values()) + sum(candidate["extra"].values())

def repair_candidate(candidate, user_cats, extra_cats, min_max, total_budget):
    """
    Adjust candidate allocations so that total_cost(candidate) == total_budget,
    while trying to respect the bounds and leaving user-selected categories fixed.
    Extra categories are adjusted proportionally.
    """
    # Compute current total for user and extra categories.
    user_total = sum(candidate["user"][cat] for cat in user_cats)
    extra_total = sum(candidate["extra"][cat] for cat in extra_cats)
    current_total = user_total + extra_total

    # If the sum of user minima exceeds the budget, candidate is infeasible.
    min_user_total = sum(min_max[cat][0] for cat in user_cats)
    if min_user_total > total_budget:
        # Set each user category to its minimum and extra to 0.
        for cat in user_cats:
            candidate["user"][cat] = min_max[cat][0]
        for cat in extra_cats:
            candidate["extra"][cat] = 0.0
        return candidate

    # Calculate remaining budget for extra categories.
    remaining = total_budget - user_total

    # If no extra categories are included, then candidate remains as is.
    if extra_total == 0:
        # We could also try to allocate remaining equally among extra categories,
        # but here we leave them as 0 (i.e. not included).
        return candidate

    # Scale each extra allocation proportionally so that their sum equals remaining.
    for cat in extra_cats:
        current = candidate["extra"][cat]
        mi, ma = min_max[cat]
        # Only adjust if currently included (allocation > 0)
        if current > 0:
            ratio = current / extra_total
            new_val = ratio * remaining
            # Clamp to bounds.
            candidate["extra"][cat] = min(max(new_val, mi), ma)
        else:
            candidate["extra"][cat] = 0.0

    # Recalculate extra_total after scaling.
    new_extra_total = sum(candidate["extra"][cat] for cat in extra_cats)
    new_total = user_total + new_extra_total

    # If there is a small difference (due to clamping) try to distribute the remainder among extra categories not at max.
    diff = total_budget - new_total
    if abs(diff) > 1e-3 and diff > 0:
        not_at_max = [cat for cat in extra_cats if candidate["extra"][cat] < min_max[cat][1]]
        if not_at_max:
            total_gap = sum(min_max[cat][1] - candidate["extra"][cat] for cat in not_at_max)
            for cat in not_at_max:
                gap = min_max[cat][1] - candidate["extra"][cat]
                add = diff * (gap / total_gap)
                candidate["extra"][cat] = min(candidate["extra"][cat] + add, min_max[cat][1])
    return candidate

def initialize_candidate(user_cats, extra_cats, min_max, total_budget):
    candidate = {"user": {}, "extra": {}}
    # For each user category, choose a random allocation between min and max.
    for cat in user_cats:
        mi, ma = min_max[cat]
        candidate["user"][cat] = random.uniform(mi, ma)
    # For extra categories, randomly decide to include (50% chance) and if so allocate randomly.
    for cat in extra_cats:
        if random.random() < 0.5:
            mi, ma = min_max[cat]
            candidate["extra"][cat] = random.uniform(mi, ma)
        else:
            candidate["extra"][cat] = 0.0
    candidate = repair_candidate(candidate, user_cats, extra_cats, min_max, total_budget)
    return candidate

def fitness(candidate, avg_prices, min_max, total_budget, penalty_factor=1e8, extra_reward=100):
    cost = total_cost(candidate)
    fit = 0.0
    # Penalize if candidate is over budget.
    if cost > total_budget:
        fit += penalty_factor * (cost - total_budget)
    # For user categories, sum squared deviation from average.
    for cat, alloc in candidate["user"].items():
        avg = avg_prices.get(cat, alloc)
        fit += (alloc - avg) ** 2
    # For extra categories, if included, add deviation and reward.
    for cat, alloc in candidate["extra"].items():
        if alloc > 0:
            avg = avg_prices.get(cat, alloc)
            fit += (alloc - avg) ** 2 - extra_reward
    return fit

def mutate(candidate, user_cats, extra_cats, min_max, total_budget, mutation_rate=0.2, mutation_scale=0.1):
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
    new_candidate = repair_candidate(new_candidate, user_cats, extra_cats, min_max, total_budget)
    return new_candidate

def crossover(parent1, parent2, user_cats, extra_cats, total_budget, min_max):
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
    child1 = repair_candidate(child1, user_cats, extra_cats, min_max, total_budget)
    child2 = repair_candidate(child2, user_cats, extra_cats, min_max, total_budget)
    return child1, child2

def genetic_algorithm(user_cats, extra_cats, avg_prices, min_max, total_budget, population_size=50, generations=100):
    population = [initialize_candidate(user_cats, extra_cats, min_max, total_budget) for _ in range(population_size)]
    best = None
    for gen in range(generations):
        population = [repair_candidate(cand, user_cats, extra_cats, min_max, total_budget) for cand in population]
        fitnesses = [fitness(cand, avg_prices, min_max, total_budget) for cand in population]
        gen_best = min(population, key=lambda c: fitness(c, avg_prices, min_max, total_budget))
        if best is None or fitness(gen_best, avg_prices, min_max, total_budget) < fitness(best, avg_prices, min_max, total_budget):
            best = gen_best
        new_population = []
        while len(new_population) < population_size:
            tournament = random.sample(population, 3)
            parent1 = min(tournament, key=lambda c: fitness(c, avg_prices, min_max, total_budget))
            tournament = random.sample(population, 3)
            parent2 = min(tournament, key=lambda c: fitness(c, avg_prices, min_max, total_budget))
            child1, child2 = crossover(parent1, parent2, user_cats, extra_cats, total_budget, min_max)
            child1 = mutate(child1, user_cats, extra_cats, min_max, total_budget)
            child2 = mutate(child2, user_cats, extra_cats, min_max, total_budget)
            new_population.extend([child1, child2])
        population = new_population[:population_size]
    population.sort(key=lambda c: fitness(c, avg_prices, min_max, total_budget))
    return population[:5]
