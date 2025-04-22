import matplotlib.pyplot as plt
import streamlit as st
import collections
import seaborn as sns

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

    # Add labels above bars
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.2, f"{yval:.2f}", ha='center', fontsize=10)

    st.pyplot(fig)

def visualize_team_composition(covered_types, uncovered_types):
    st.subheader("Covered Types")
    if covered_types:
        st.markdown("✅ " + ", ".join(covered_types))
    else:
        st.markdown("✅ None")

    st.subheader("Uncovered Types")
    if uncovered_types:
        st.markdown("❌ " + ", ".join(uncovered_types))
    else:
        st.markdown("❌ None")



def visualize_weakness_resistance(team):
    all_weaknesses = []
    all_resistances = []
    for _, row in team.iterrows():
        all_weaknesses.extend(row.get("weaknesses", []))
        all_resistances.extend(row.get("resistances", []))

    # Count each type
    weakness_count = collections.Counter(all_weaknesses)
    resistance_count = collections.Counter(all_resistances)

    types = list(set(weakness_count.keys()) | set(resistance_count.keys()))
    types.sort()

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
