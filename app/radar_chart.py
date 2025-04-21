import numpy as np
import matplotlib.pyplot as plt

# Dark mode styling
plt.style.use("dark_background")

STAT_CATEGORIES = [
    "hp", "attack", "defense", "special-attack", "special-defense", "speed"
]

COLOR_PALETTE = [
    "#ff6384", "#36a2eb", "#cc65fe", "#ffce56", "#4bc0c0"
]

def plot_team_radar_chart(team_df, team_index, team_name="Team"):
    # Average stats for the team
    avg_stats = team_df[STAT_CATEGORIES].mean().values
    labels = STAT_CATEGORIES

    # Radar chart setup
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats = np.concatenate((avg_stats, [avg_stats[0]]))
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw=dict(polar=True))
    ax.plot(angles, stats, color=COLOR_PALETTE[team_index % len(COLOR_PALETTE)], linewidth=2)
    ax.fill(angles, stats, color=COLOR_PALETTE[team_index % len(COLOR_PALETTE)], alpha=0.4)

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color='white', fontsize=9)

    # Include team_name in the title for clarity
    ax.set_title(f"{team_name} Stat Profile", color="white", fontsize=12, pad=20)

    return fig

