import streamlit as st
import pandas as pd
from app.data_loader import fetch_pokemon_data
from app.team_builder import generate_top_team_candidates
from app.team_metrics import calculate_synergy_score, evaluate_team_coverage
from app.visualizer import visualize_synergy_scores, visualize_team_composition
from app.radar_chart import plot_team_radar_chart
from app.type_icons import TYPE_EMOJIS


@st.cache_data
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

    # Check if data is loaded
    if st.session_state.pokemon_loaded:
        pokemon_df = st.session_state.pokemon_data
        button_label = "Generate Team"
    else:
        button_label = "Start Calculation"

    # Show only the "Generate Team" button initially
    if not st.session_state.pokemon_loaded:
        if st.button(button_label):
            with st.spinner("Fetching Pokémon data..."):
                pokemon_df = load_pokemon_data()

                # Show columns after loading data
                st.write("Columns in DataFrame:", pokemon_df.columns.tolist())

                # ✅ Filter only final evolutions
                pokemon_df = pokemon_df[pokemon_df["is_final_evolution"] == True].reset_index(drop=True)

                st.session_state.pokemon_data = pokemon_df
                st.session_state.pokemon_loaded = True

            st.rerun()

    else:
        # Add Filters (Game selection & Evolution checkbox)
        st.sidebar.header("Filters")
        
        # Clean the 'games' column to exclude NaN values and handle cases where it's not a list
        pokemon_df['games'] = pokemon_df['games'].apply(lambda x: x if isinstance(x, list) else [])
        
        # Extract distinct game names for the dropdown
        game_options = pokemon_df['games'].explode().dropna().unique()  # Get unique game names from the data
        
        # Format game names in "proper" case
        game_options = [game.title() for game in game_options]  # Capitalize first letter of each word

        game_choice = st.sidebar.selectbox("Select Pokémon Game", game_options)

        # Evolution checkbox to filter only final evolutions
        is_final_evolution = st.sidebar.checkbox("Only Final Evolutions", value=True)

        # Filter data based on selected options
        filtered_df = pokemon_df.copy()

        filtered_df["name"] = filtered_df["name"].apply(lambda x: x.title())  # Apply .title() to Pokémon names


        # Filter by selected game
        if game_choice:
            filtered_df = filtered_df[filtered_df["games"].apply(lambda games: game_choice.lower() in [game.lower() for game in games])]

        # Apply evolution checkbox filter
        if is_final_evolution:
            filtered_df = filtered_df[filtered_df["is_final_evolution"] == True]

        # Check if the filtered DataFrame is empty
        if filtered_df.empty:
            st.error("No Pokémon match your filter criteria. Please adjust the filters and try again.")
            return  # Stop further execution
        
        # Add a display-only column for types with emojis
        filtered_df["types_display"] = filtered_df["types"].apply(
            lambda types: " | ".join(f"{TYPE_EMOJIS.get(t.lower(), '')} {t.title()}" for t in types)
        )       


        # Display filtered data
        st.write(f"Filtered Pokémon (Game: {game_choice}, Final Evolution: {is_final_evolution}):")


        # Button to generate teams after selecting filters
        if st.button("Generate Optimal Teams"):
            st.subheader("Generating Top 5 Teams")
            progress = st.progress(0)
            status_text = st.empty()

            def progress_callback(progress_fraction):
                progress.progress(progress_fraction)
                status_text.text(f"Generating teams... {int(progress_fraction * 100)}%")

            # Generate the top 5 teams
            top_teams = generate_top_team_candidates(
                filtered_df,
                team_size=6,
                top_n=5,
                max_teams=10000,
                progress_callback=progress_callback
            )

            # Format the teams into DataFrames for better presentation
            formatted_teams = []
            for team in top_teams:
                # Keep all necessary columns, especially for radar charts
                formatted_team = team.reset_index(drop=True)
                formatted_teams.append(formatted_team)

            # Store generated teams in session state
            st.session_state.top_teams = formatted_teams
            st.session_state.teams_generated = True

            st.subheader("Team Stat Radar Charts")
            
            for i, team in enumerate(st.session_state.top_teams):
                st.subheader(f"Team {i+1} Pokémon:")
                # Add emoji-enhanced types display for this team
                team["types_display"] = team["types"].apply(
                    lambda types: " | ".join(f"{TYPE_EMOJIS.get(t.lower(), '')} {t.title()}" for t in types)
                )

                st.dataframe(team[["name", "types_display", "total_stats"]].rename(columns={"types_display": "types"}).reset_index(drop=True))

                  


                # Display the sprite for each Pokémon in the team
                cols = st.columns(len(team))
                for col, (_, row) in zip(cols, team.iterrows()):
                    with col:
                        # Properly format Pokémon names
                        pokemon_name = row["name"].title()  # Format Pokémon name
                        st.image(row["sprite_url"], width=80, caption=pokemon_name)
                        st.markdown(get_type_emojis(row["types"]))

                covered_types, uncovered_types = evaluate_team_coverage(team)
                visualize_team_composition(covered_types, uncovered_types)

                # Display the radar chart with the team name
                st.subheader(f"Team {i+1}")
                fig = plot_team_radar_chart(team, i, team_name=f"Team {i+1}")
                st.pyplot(fig)

            st.subheader("Team Synergy Scores")
            synergy_scores = []
            for i, team in enumerate(formatted_teams):
                score = calculate_synergy_score(team)
                synergy_scores.append(score)

            # Visualize synergy scores as a bar chart
            visualize_synergy_scores(synergy_scores)

        elif st.session_state.teams_generated:
            # If teams have been generated previously, allow user to regenerate teams again
            st.session_state.teams_generated = False  # Reset flag to regenerate teams

            st.write("Regenerating teams...")
            st.rerun()  # This will trigger the regeneration process again


if __name__ == "__main__":
    main()
