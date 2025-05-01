
from itertools import combinations
import random
from itertools import islice, combinations
import pandas as pd
from app.team_metrics import calculate_synergy_score

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
    locked_lower = [p.strip().lower() for p in locked_pokemon]
    locked_df = pokemon_df[pokemon_df["name"].str.strip().str.lower().isin(locked_lower)]
    remaining_pool = pokemon_df[~pokemon_df["name"].str.strip().str.lower().isin(locked_lower)]

    # Debugging: Print locked Pokémon and DataFrame
    print("Locked Pokémon:", locked_pokemon)
    print("Locked Pokémon DataFrame:")
    print(locked_df)

    # Ensure the number of locked Pokémon does not exceed the team size
    num_locked = len(locked_pokemon)
    if num_locked > team_size:
        raise ValueError("The number of locked Pokémon exceeds the team size.")

    # Calculate the number of remaining Pokémon needed to complete the team
    num_remaining = team_size - num_locked
    if num_remaining < 0:
        return []

    # Shuffle the remaining pool for randomness
    pool = list(remaining_pool.index)

    # Generate random teams by sampling from the remaining pool
    sampled_combos = [
        random.sample(pool, num_remaining) for _ in range(max_teams)
    ]

    # Convert locked Pokémon to indices
    locked_indices = list(locked_df.index)

    pokemon_data = pokemon_df.to_dict(orient="records")

    scored_teams = []
    for i, combo in enumerate(sampled_combos):
        # Combine locked Pokémon with the generated combination
        full_team_indices = list(set(locked_indices + combo))  # Ensure unique indices
        full_team = [pokemon_data[idx] for idx in full_team_indices]
        print(f"Full Team: {[pokemon['name'] for pokemon in full_team]}")

        # Ensure the team size is correct
        if len(full_team) != team_size:
            raise ValueError(f"Generated team size is incorrect: {len(full_team)} (expected {team_size})")

        # Debugging: Print the full team
        
        # Convert the full team to a DataFrame
        full_team_df = pd.DataFrame(full_team)

        # Calculate synergy score (or other metrics)
        synergy_score = calculate_synergy_score(full_team_df)  # Pass the DataFrame
        scored_teams.append((full_team, synergy_score))

        if progress_callback:
            progress_callback((i + 1) / len(sampled_combos))

    # Sort teams by synergy score in descending order
    scored_teams.sort(key=lambda x: x[1], reverse=True)

    # Return the top N teams
    return [team for team, _ in scored_teams[:top_n]]