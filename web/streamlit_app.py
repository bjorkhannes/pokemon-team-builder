import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import collections
import matplotlib.pyplot as plt
from app.data_loader import fetch_pokemon_data
from app.team_builder import generate_top_team_candidates
from app.team_metrics import calculate_synergy_score, evaluate_team_coverage
from app.visualizer import visualize_team_composition
from app.radar_chart import plot_team_radar_chart
import time
from app.type_icons import TYPE_EMOJIS

@st.cache_data

def time_function(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        st.write(f"Function {func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

def load_pokemon_data():
    return fetch_pokemon_data()

def get_type_emojis(pokemon_types):
    return " ".join(TYPE_EMOJIS.get(t.lower(), t.title()) for t in pokemon_types)

def visualize_synergy_scores(synergy_scores):
    sorted_scores = sorted(enumerate(synergy_scores), key=lambda x: x[1], reverse=True)
    indices, scores = zip(*sorted_scores)

    fig, ax = plt.subplots()
    bars = ax.bar(range(len(scores)), scores, color='skyblue')

    ax.set_title("Team Synergy Scores", fontsize=14)
    ax.set_xlabel("Team", fontsize=12)
    ax.set_ylabel("Synergy Score", fontsize=12)
    ax.set_xticks(range(len(scores)))
    ax.set_xticklabels([f"Team {i+1}" for i in indices])

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.2, f"{yval:.2f}", ha='center', fontsize=10)

    st.pyplot(fig)

def visualize_weakness_resistance(team):
    all_weaknesses = []
    all_resistances = []
    for _, row in team.iterrows():
        all_weaknesses.extend(row.get("weaknesses", []))
        all_resistances.extend(row.get("resistances", []))

    weakness_count = collections.Counter(all_weaknesses)
    resistance_count = collections.Counter(all_resistances)

    types = sorted(set(weakness_count) | set(resistance_count))
    weak_vals = [weakness_count.get(t, 0) for t in types]
    resist_vals = [resistance_count.get(t, 0) for t in types]
    labels = [f"{TYPE_EMOJIS.get(t.lower(), '')} {t.title()}" for t in types]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(labels, weak_vals, label="Weak", color='salmon')
    ax.bar(labels, resist_vals, bottom=weak_vals, label="Resistant", color='lightgreen')
    ax.set_title("Team Weakness vs Resistance by Type")
    ax.set_ylabel("Count")
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend()
    st.pyplot(fig)

def main():
    st.title("Pokémon Team Builder")

    if "pokemon_data" not in st.session_state:
        st.session_state.pokemon_data = None
    if "pokemon_loaded" not in st.session_state:
        st.session_state.pokemon_loaded = False
    if "teams_generated" not in st.session_state:
        st.session_state.teams_generated = False
    if "top_teams" not in st.session_state:
        st.session_state.top_teams = []

    if st.session_state.pokemon_loaded:
        pokemon_df = st.session_state.pokemon_data
        button_label = "Generate Team"
    else:
        button_label = "Start Calculation"

    if not st.session_state.pokemon_loaded:
        if st.button(button_label):
            with st.spinner("Fetching Pokémon data..."):
                pokemon_df = load_pokemon_data()
                pokemon_df = pokemon_df[pokemon_df["is_final_evolution"] == True].reset_index(drop=True)
                st.session_state.pokemon_data = pokemon_df
                st.session_state.pokemon_loaded = True
            st.rerun()
    else:
        st.header("🔧 Team Filters")

        pokemon_df['games'] = pokemon_df['games'].apply(lambda x: x if isinstance(x, list) else [])
        game_options = [game.title() for game in pokemon_df['games'].explode().dropna().unique()]

        with st.expander("🔍 Filters", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                game_choice = st.selectbox("🎮 Select Pokémon Game", game_options)
            with col2:
                is_final_evolution = st.checkbox("🧬 Only Final Evolutions", value=True)

        filtered_df = pokemon_df.copy()
        filtered_df["name"] = filtered_df["name"].apply(lambda x: x.title())

        if game_choice:
            filtered_df = filtered_df[filtered_df["games"].apply(lambda games: game_choice.lower() in [game.lower() for game in games])]

        if is_final_evolution:
            filtered_df = filtered_df[filtered_df["is_final_evolution"] == True]

        if filtered_df.empty:
            st.error("No Pokémon match your filter criteria. Please adjust the filters and try again.")
            return

        filtered_df["types_display"] = filtered_df["types"].apply(
            lambda types: " | ".join(f"{TYPE_EMOJIS.get(t.lower(), '')} {t.title()}" for t in types)
        )

        all_names = filtered_df["name"].unique()
        locked_pokemon = st.multiselect("🔍 Lock-in Pokémon (Optional)", options=sorted(all_names))

        if st.button("⚔️ Generate Optimal Teams"):
            st.subheader("Generating Top 5 Teams")
            progress = st.progress(0.2)
            status_text = st.empty()

            def progress_callback(progress_fraction):
                progress.progress(progress_fraction)
                status_text.text(f"Generating teams... {int(progress_fraction * 100)}%")

            top_teams = generate_top_team_candidates(
                filtered_df,
                team_size=6,
                top_n=5,
                max_teams=10000,
                progress_callback=progress_callback,
                locked_pokemon=locked_pokemon
            )

            formatted_teams = []
            for team in top_teams:
                formatted_team = team.reset_index(drop=True)
                formatted_teams.append(formatted_team)

            st.session_state.top_teams = formatted_teams
            st.session_state.teams_generated = True

            st.subheader("Team Synergy Scores")
            synergy_scores = [calculate_synergy_score(team) for team in formatted_teams]
            visualize_synergy_scores(synergy_scores)

            # Create tabs for each team
            tabs = st.tabs([f"Team {i+1}" for i in range(len(formatted_teams))])
            
            for i, team in enumerate(st.session_state.top_teams):
                with tabs[i]:
                    st.subheader(f"Team {i+1} Pokémon:")
                    team["types_display"] = team["types"].apply(
                        lambda types: " | ".join(f"{TYPE_EMOJIS.get(t.lower(), '')} {t.title()}" for t in types)
                    )

                    st.dataframe(team[["name", "types_display", "total_stats"]].rename(columns={"types_display": "types"}).reset_index(drop=True))

                    cols = st.columns(len(team))
                    for col, (_, row) in zip(cols, team.iterrows()):
                        with col:
                            st.image(row["sprite_url"], width=80, caption=row["name"].title())
                            st.markdown(get_type_emojis(row["types"]))

                    covered_types, uncovered_types = evaluate_team_coverage(team)

                    def format_types_with_emojis(types):
                        return [f"{TYPE_EMOJIS.get(t.lower(), '')} {t.title()}" for t in types]

                    covered_display = format_types_with_emojis(covered_types)
                    uncovered_display = format_types_with_emojis(uncovered_types)
                    visualize_team_composition(covered_display, uncovered_display)

                    st.subheader(f"Team {i+1} Stats")
                    fig = plot_team_radar_chart(team, i, team_name=f"Team {i+1}")
                    st.pyplot(fig)

            

        elif st.session_state.teams_generated:
            st.session_state.teams_generated = False
            st.rerun()

if __name__ == "__main__":
    main()
