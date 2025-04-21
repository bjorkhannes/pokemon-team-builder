import matplotlib.pyplot as plt
import streamlit as st

def visualize_synergy_scores(synergy_scores):
    fig, ax = plt.subplots()
    ax.bar(range(len(synergy_scores)), synergy_scores)
    ax.set_title("Team Synergy Scores")
    ax.set_xlabel("Team Index")
    ax.set_ylabel("Synergy Score")
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
