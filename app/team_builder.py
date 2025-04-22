import numpy as np
from app.team_metrics import calculate_synergy_score
import streamlit as st
from itertools import combinations
import random
from multiprocessing import Pool

# Separate the evaluate_team function outside of generate_top_team_candidates
def evaluate_team(combo, locked_df, pokemon_df):
    # Combine the locked Pokémon with the current combination
    team_indices = list(locked_df.index) + list(combo)
    team_df = pokemon_df.loc[team_indices]
    
    # Calculate the synergy score for the team
    return team_df, calculate_synergy_score(team_df)

def generate_top_team_candidates(
    pokemon_df,
    team_size=6,
    top_n=5,
    max_teams=1000,  # Reduced max_teams
    progress_callback=None,
    locked_pokemon=None
):
    if locked_pokemon is None:
        locked_pokemon = []

    # Prepare the data for locked and remaining Pokémon
    locked_df = pokemon_df[pokemon_df["name"].str.lower().isin([p.lower() for p in locked_pokemon])]
    remaining_pool = pokemon_df[~pokemon_df["name"].str.lower().isin([p.lower() for p in locked_pokemon])]

    # Calculate the number of Pokémon needed to complete the team
    num_remaining = team_size - len(locked_pokemon)
    if num_remaining < 0:
        return []

    # Randomly sample combinations instead of generating all
    all_combos = list(combinations(remaining_pool.index, num_remaining))
    random.shuffle(all_combos)
    sampled_combos = all_combos[:max_teams]

    # Use multiprocessing to evaluate teams
    with Pool() as pool:
        # Pass locked_df and pokemon_df to the evaluate_team function using a lambda
        scored_teams = pool.map(lambda combo: evaluate_team(combo, locked_df, pokemon_df), sampled_combos)

    # Sort by synergy score
    scored_teams = sorted(scored_teams, key=lambda x: x[1], reverse=True)
    
    # Return the top_n teams based on synergy score
    return [team for team, _ in scored_teams[:top_n]]

