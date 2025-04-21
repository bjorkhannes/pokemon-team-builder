import numpy as np
from app.team_metrics import calculate_synergy_score
import streamlit as st

def generate_top_team_candidates(pokemon_df, team_size=6, top_n=5, max_teams=10000, progress_callback=None):
    top_teams = []

    for i in range(top_n):
        team_indices = np.random.choice(pokemon_df.index, size=team_size, replace=False)
        team_data = pokemon_df.loc[team_indices].copy()  # <- KEEP all columns

        synergy_score = calculate_synergy_score(team_data)

        if progress_callback:
            progress_callback((i + 1) / top_n)

        team_data['synergy_score'] = synergy_score
        top_teams.append(team_data)

    return top_teams
