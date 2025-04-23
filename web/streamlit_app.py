import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from app.data_loader import fetch_pokemon_data
from app.team_builder import generate_top_team_candidates
from app.team_metrics import calculate_synergy_score, evaluate_team_coverage
from app.visualizer import visualize_team_composition, visualize_synergy_scores
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

def main():
    st.title("Pokémon Team Builder")

    # Initialize session state variables
    if "pokemon_data" not in st.session_state:
        st.session_state.pokemon_data = None
    if "pokemon_loaded" not in st.session_state:
        st.session_state.pokemon_loaded = False
    if "teams_generated" not in st.session_state:
        st.session_state.teams_generated = False
    if "top_teams" not in st.session_state:
        st.session_state.top_teams = []

    # Automatically load Pokémon data if not already loaded
    if not st.session_state.pokemon_loaded:
        with st.spinner("Fetching Pokémon data... Please wait."):
            progress_bar = st.progress(0)  # Initialize progress bar
            st.markdown("### Loading Pokémon data...")

            # Simulate progress updates
            for i in range(1, 6):
                time.sleep(0.5)  # Simulate work
                progress_bar.progress(i * 20)  # Increment progress

            # Load Pokémon data
            pokemon_df = load_pokemon_data()
            pokemon_df = pokemon_df[pokemon_df["is_final_evolution"] == True].reset_index(drop=True)
            st.session_state.pokemon_data = pokemon_df
            st.session_state.pokemon_loaded = True

    # Display the success message temporarily
    success_placeholder = st.empty()
    success_placeholder.success("Pokémon data loaded successfully!")
    time.sleep(2)  # Wait for 1 second
    success_placeholder.empty()  # Clear the message


    # Proceed to filters and team generation
    st.write("🔧 Team Filters")

    pokemon_df = st.session_state.pokemon_data
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

    filtered_df = filtered_df.sort_values(by="name")
    # Prepend type icons to Pokémon names
    filtered_df["display_name"] = filtered_df.apply(
        lambda row: f"{' '.join(TYPE_EMOJIS.get(t.lower(), t.title()) for t in row['types'])} {'◯ ' if len(row['types']) == 1 else ''} {row['name']}",
        axis=1
    )

    # Use the new display_name column for the dropdown
    locked_pokemon = st.multiselect(
        "🔍 Lock-in Pokémon (Optional)",
        options=filtered_df["display_name"].tolist()
    )

    # Extract the actual Pokémon names from the selected options
    locked_pokemon = [
        name.split(" ", maxsplit=len(row["types"]))[-1]  # Extract the name after the type icons
        for name in locked_pokemon
    ]

    if st.button("⚔️ Generate Optimal Teams"):
        st.subheader("Generating Top 5 Teams")
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Simulate progress updates
        for i in range(1, 6):
            time.sleep(0.5)  # Simulate work
            progress_bar.progress(i * 20)
            status_text.text(f"Step {i}/5: Sorting through pokémon...")
            
        with st.spinner("Performing calculations...", show_time=True):
            time.sleep(7)
        st.success("Calculations completed! Generating teams...")
        # Call generate_top_team_candidates
        top_teams = generate_top_team_candidates(
            filtered_df,
            team_size=6,
            top_n=5,
            max_teams=1000,
            locked_pokemon=locked_pokemon
        )

        # Format the teams for display
        formatted_teams = []
        for team in top_teams:
            # Convert the team (list of dictionaries) into a pandas DataFrame
            formatted_team = pd.DataFrame(team).reset_index(drop=True)
            formatted_teams.append(formatted_team)

        st.session_state.top_teams = formatted_teams
        st.session_state.teams_generated = True
        st.success("Teams generated successfully!")

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

                # Include individual stats in the summary table
                st.dataframe(
                    team[
                        ["name", "types_display", "total_stats", "hp", "attack", "defense", "special-attack", "special-defense", "speed"]
                    ]
                    .rename(columns={"types_display": "types"})
                    .reset_index(drop=True)
                )

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