
from itertools import combinations
import random

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
    progress_callback=None  # Add progress callback
):
    if locked_pokemon is None:
        locked_pokemon = []

    locked_df = pokemon_df[pokemon_df["name"].str.lower().isin([p.lower() for p in locked_pokemon])]
    remaining_pool = pokemon_df[~pokemon_df["name"].str.lower().isin([p.lower() for p in locked_pokemon])]

    num_remaining = team_size - len(locked_pokemon)
    if num_remaining < 0:
        return []

    # Directly sample a subset of combinations without generating all of them
    if len(remaining_pool) >= num_remaining:
        sampled_combos = random.sample(
            list(combinations(remaining_pool.index, num_remaining)),
            min(max_teams, len(list(combinations(remaining_pool.index, num_remaining))))
        )
    else:
        sampled_combos = list(combinations(remaining_pool.index, num_remaining))

    locked_indices = list(locked_df.index)
    pokemon_data = pokemon_df.to_dict(orient="records")

    scored_teams = []
    for i, combo in enumerate(sampled_combos):
        team, synergy_score = evaluate_team(combo, locked_indices, pokemon_data)
        scored_teams.append((team, synergy_score))

        # Update progress if callback is provided
        if progress_callback:
            progress_callback((i + 1) / len(sampled_combos))  # Fraction of progress

    scored_teams = sorted(scored_teams, key=lambda x: x[1], reverse=True)
    return [team for team, _ in scored_teams[:top_n]]