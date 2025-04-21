import os
import json
import time
import requests
from tqdm import tqdm

API_BASE_URL = "https://pokeapi.co/api/v2"
DATA_FILE_PATH = os.path.join("data", "pokemon_data.json")

def fetch_all_pokemon(limit=492):  # You can increase this limit if desired
    response = requests.get(f"{API_BASE_URL}/pokemon?limit={limit}")
    response.raise_for_status()
    return response.json()["results"]

def get_evolution_chain(url):
    response = requests.get(url)
    response.raise_for_status()
    species_data = response.json()

    evolution_chain_url = species_data["evolution_chain"]["url"]
    response = requests.get(evolution_chain_url)
    response.raise_for_status()
    evolution_chain = response.json()["chain"]

    return flatten_evolution_chain(evolution_chain)

def flatten_evolution_chain(chain):
    """
    Recursively flattens the evolution chain into a list of names.
    Returns a list of all evolutions in order.
    """
    evo_list = [chain["species"]["name"]]
    evolves_to = chain.get("evolves_to", [])

    if evolves_to:
        for evo in evolves_to:
            evo_list.extend(flatten_evolution_chain(evo))

    return evo_list

def fetch_pokemon_details(url):
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
    total_stats = sum(stats.values())

    # Extract game indices
    game_indices = data.get("game_indices", [])
    games = [game["version"]["name"] for game in game_indices]

    # Get species info to later get evolution chain
    species_url = data["species"]["url"]
    species_response = requests.get(species_url)
    species_response.raise_for_status()
    species_data = species_response.json()

    # Evolution data
    try:
        evolution_names = get_evolution_chain(species_url)
        is_final = (data["name"] == evolution_names[-1])
    except Exception as e:
        print(f"Failed to get evolution chain for {data['name']}: {e}")
        evolution_names = []
        is_final = False

    return {
        "id": data["id"],
        "name": data["name"],
        "types": [t["type"]["name"] for t in data["types"]],
        "hp": stats.get("hp", 0),
        "attack": stats.get("attack", 0),
        "defense": stats.get("defense", 0),
        "special-attack": stats.get("special-attack", 0),
        "special-defense": stats.get("special-defense", 0),
        "speed": stats.get("speed", 0),
        "total_stats": total_stats,
        "sprite_url": data.get("sprites", {}).get("front_default", None),
        "games": games,
        "evolution_chain": evolution_names,
        "is_final_evolution": is_final
    }

def cache_data():
    os.makedirs("data", exist_ok=True)

    print("Fetching Pokémon list...")
    pokemon_list = fetch_all_pokemon()

    print("Fetching detailed data for each Pokémon...")
    all_data = []
    for pokemon in tqdm(pokemon_list):
        try:
            details = fetch_pokemon_details(pokemon["url"])
            all_data.append(details)
            time.sleep(0.2)  # Be nice to the API
        except Exception as e:
            print(f"Failed to fetch {pokemon['name']}: {e}")

    with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)

    print(f"✅ Pokémon data cached to {DATA_FILE_PATH}")

if __name__ == "__main__":
    cache_data()
