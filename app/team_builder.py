
from itertools import combinations
import random
from itertools import islice, combinations

def sample_combinations(pool, k, n_samples):
    seen = set()
    generator = combinations(pool, k)
    for combo in generator:
        if len(seen) >= n_samples:
            break
        seen.add(combo)
        yield combo

# Define evaluate_team at the top level of the module
def evaluate_team(combo, locked_indices, pokemon_data):
    team_indices = locked_indices + list(combo)
    team = [pokemon_data[i] for i in team_indices]
    synergy_score = sum(pokemon["total_stats"] for pokemon in team)
    return team, synergy_score

def generate_top_team_candidates(
    pokemon_df,
    team_size=6,
    top_n=5,
    max_teams=1000,
    locked_pokemon=None,
    progress_callback=None
):
    if locked_pokemon is None:
        locked_pokemon = []

    # Normalize names for comparison
    locked_lower = [p.lower() for p in locked_pokemon]
    locked_df = pokemon_df[pokemon_df["name"].str.lower().isin(locked_lower)]
    remaining_pool = pokemon_df[~pokemon_df["name"].str.lower().isin(locked_lower)]

    num_remaining = team_size - len(locked_pokemon)
    if num_remaining < 0:
        return []

    # Shuffle pool for pseudo-randomness
    pool = list(remaining_pool.index)
    random.shuffle(pool)

    # Use generator to sample combinations efficiently
    sampled_combos = list(islice(combinations(pool, num_remaining), max_teams))

    locked_indices = list(locked_df.index)
    pokemon_data = pokemon_df.to_dict(orient="records")

    scored_teams = []
    for i, combo in enumerate(sampled_combos):
        team, synergy_score = evaluate_team(combo, locked_indices, pokemon_data)
        scored_teams.append((team, synergy_score))

        if progress_callback:
            progress_callback((i + 1) / len(sampled_combos))

    scored_teams.sort(key=lambda x: x[1], reverse=True)
    return [team for team, _ in scored_teams[:top_n]]