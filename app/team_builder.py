import numpy as np
from app.team_metrics import calculate_synergy_score
import streamlit as st
from itertools import combinations
import random

def generate_top_team_candidates(
    pokemon_df,
    team_size=6,
    top_n=5,
    max_teams=10000,
    progress_callback=None,
    locked_pokemon=None  # ✅ Add this
):
    # Default to empty list if locked_pokemon is None
    if locked_pokemon is None:
        locked_pokemon = []

    # Ensure locked Pokémon exist in the filtered dataframe
    locked_df = pokemon_df[pokemon_df["name"].str.lower().isin([p.lower() for p in locked_pokemon])]
    remaining_pool = pokemon_df[~pokemon_df["name"].str.lower().isin([p.lower() for p in locked_pokemon])]

    candidates = []
    num_remaining = team_size - len(locked_pokemon)

    # If there are no more remaining Pokémon to form a team, return empty list
    if num_remaining < 0:
        return []

    # Generate all possible combinations of remaining Pokémon
    all_combos = list(combinations(remaining_pool.index, num_remaining))
    random.shuffle(all_combos)

    for i, combo in enumerate(all_combos[:max_teams]):
        team_indices = list(locked_df.index) + list(combo)
        team_df = pokemon_df.loc[team_indices]
        candidates.append(team_df)

        # Progress tracking
        if progress_callback and i % 100 == 0:
            progress_callback(i / min(len(all_combos), max_teams))

    # Calculate synergy for sorting
    scored_teams = sorted(candidates, key=calculate_synergy_score, reverse=True)

    return scored_teams[:top_n]
