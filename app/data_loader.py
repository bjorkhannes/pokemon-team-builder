import json
import pandas as pd

def fetch_pokemon_data():
    with open("data/pokemon_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    
    
    return df

