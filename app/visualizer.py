import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import collections
from app.type_icons import TYPE_EMOJIS


def visualize_synergy_scores(synergy_scores):
    sorted_scores = sorted(enumerate(synergy_scores), key=lambda x: x[1], reverse=True)
    indices, scores = zip(*sorted_scores)

    # Create a DataFrame for Seaborn
    data = {"Team": [f"Team {i+1}" for i in indices], "Synergy Score": scores}

    # Create the plot
    sns.set_theme(style="whitegrid")  # Set Seaborn theme
    fig, ax = plt.subplots(figsize=(4, 2))  # Adjust size as needed
    sns.barplot(x="Team", y="Synergy Score", data=data, ax=ax, palette="BuPu")

    # Customize the plot
    ax.set_title("Team Synergy Scores", fontsize=14)
    ax.set_xlabel("Team", fontsize=12)
    ax.set_ylabel("Synergy Score", fontsize=12)
    ax.bar_label(ax.containers[0], fmt="%.2f", fontsize=10)  # Add labels above bars

    st.pyplot(fig)

def visualize_team_composition(covered_types, uncovered_types):
    st.subheader("✅ Covered Types")
    if covered_types:
        st.markdown(", ".join(covered_types))
    else:
        st.markdown("✅ None")

    st.subheader("❌Uncovered Types")
    if uncovered_types:
        st.markdown(", ".join(uncovered_types))
    else:
        st.markdown("None")



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
