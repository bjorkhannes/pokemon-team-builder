

def calculate_synergy_score(team_df):
    synergy_score = team_df['total_stats'].sum()
    return synergy_score

# Modify your evaluate_team_coverage function to account for the full list of types
def evaluate_team_coverage(team_df):
    all_types = set()

    # Collect types for each Pokémon in the team
    for idx, row in team_df.iterrows():
        # Assume that types are stored as a list of strings
        pokemon_types = row['types']
        all_types.update(pokemon_types)  # Add all types to the set (sets automatically handle duplicates)

    # List of all possible types (for simplicity, we're using a fixed list here)
    all_possible_types = [
        'bug', 'dark', 'dragon', 'electric', 'fairy', 'fighting', 'fire', 'flying',
        'ghost', 'grass', 'ground', 'ice', 'normal', 'poison', 'psychic', 'rock', 'steel', 'water'
    ]

    # Find uncovered types by subtracting the covered types from the full set
    uncovered_types = [t for t in all_possible_types if t not in all_types]
    covered_types = [t for t in all_possible_types if t in all_types]

    return covered_types, uncovered_types


