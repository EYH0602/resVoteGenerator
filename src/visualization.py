import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Any
import pandas as pd

# Set a modern and clean style for charts
sns.set_theme(style="whitegrid")


def plot_candidate_distribution(
    votes: List[Dict[str, Any]], output_image: str = "candidate_distribution.png"
):
    """
    Plot a bar chart showing total votes for each candidate.
    X-axis: Candidates
    Y-axis: Vote counts
    """
    # Count votes per candidate
    candidate_counts = Counter(v["candidate_name"] for v in votes)

    candidates = list(candidate_counts.keys())
    counts = list(candidate_counts.values())

    plt.figure(figsize=(8, 6))
    sns.barplot(x=candidates, y=counts, palette="viridis")
    plt.title("Candidate Vote Distribution", fontsize=16)
    plt.xlabel("Candidates", fontsize=14)
    plt.ylabel("Number of Votes", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_image, dpi=500)
    plt.close()


def plot_attribute_distribution(
    votes: List[Dict[str, Any]],
    attribute: str = "gender",
    output_image: str = "attribute_distribution.png",
):
    """
    Plot a pie chart (or donut chart) showing the distribution of a single voter attribute.
    For example, gender distribution or region distribution.
    """
    attr_counts = Counter(v["attributes"].get(attribute, "Unknown") for v in votes)

    labels = list(attr_counts.keys())
    sizes = list(attr_counts.values())

    plt.figure(figsize=(6, 6))
    # Create a donut chart by adding a white circle in the center
    wedges, texts, autotexts = plt.pie(
        sizes, labels=labels, autopct="%1.1f%%", startangle=90, pctdistance=0.85
    )
    # Draw a circle in the center to make it a donut
    centre_circle = plt.Circle((0, 0), 0.70, fc="white")
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    plt.title(f"Distribution of {attribute.capitalize()}", fontsize=16)
    plt.tight_layout()
    plt.savefig(output_image, dpi=500)
    plt.close()


def plot_stacked_bar(
    votes: List[Dict[str, Any]],
    attribute1: str = "gender",
    attribute2: str = "region",
    output_image: str = "stacked_bar.png",
):
    """
    Plot a stacked bar chart or grouped bar chart to show the influence of two attributes on candidate preference.
    For example, how does (gender, region) combination affect votes for each candidate?
    """
    # We'll create a structure: {candidate: {(attr1, attr2): count}}
    combo_counts = defaultdict(Counter)
    for v in votes:
        a1 = v["attributes"].get(attribute1, "Unknown")
        a2 = v["attributes"].get(attribute2, "Unknown")
        combo_counts[v["candidate_name"]][(a1, a2)] += 1

    candidates = list(combo_counts.keys())
    # Extract all combinations of (attr1, attr2)
    all_combos = set()
    for c in candidates:
        all_combos.update(combo_counts[c].keys())
    all_combos = list(all_combos)

    # Convert to a dataframe-like structure for plotting
    # rows: candidates, columns: combination of (attr1, attr2)

    data = []
    for c in candidates:
        row = {}
        for combo in all_combos:
            row[combo] = combo_counts[c][combo]
        row["candidate"] = c
        data.append(row)

    df = pd.DataFrame(data).set_index("candidate")

    # df columns are tuples (a1, a2). For readability, rename them
    df.columns = [f"{a1}_{a2}" for (a1, a2) in df.columns]

    # Plot a stacked bar chart
    plt.figure(figsize=(10, 6))
    df.plot(kind="bar", stacked=True, colormap="viridis", width=0.8)
    plt.title(
        f"Votes by {attribute1.capitalize()} and {attribute2.capitalize()} for Each Candidate",
        fontsize=16,
    )
    plt.xlabel("Candidates", fontsize=14)
    plt.ylabel("Number of Votes", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.legend(
        title=f"{attribute1.capitalize()}_{attribute2.capitalize()}",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
    )
    plt.tight_layout()
    plt.savefig(output_image, dpi=500)
    plt.close()


def plot_time_series(
    votes: List[Dict[str, Any]], output_image: str = "time_series.png", freq: str = "H"
):
    """
    Plot a line chart to show how total votes evolve over time.
    freq: 'H' for hour, 'D' for day, etc.
    """
    # Convert timestamps to datetime objects
    times = [datetime.fromisoformat(v["timestamp"]) for v in votes]
    # Count how many votes occurred in each time bucket

    df = pd.DataFrame({"time": times})
    df = df.set_index("time").sort_index()

    # Resample and count
    df_count = df.resample(freq).size()

    plt.figure(figsize=(10, 5))
    sns.lineplot(x=df_count.index, y=df_count.values, marker="o", color="royalblue")
    plt.title("Voting Trend Over Time", fontsize=16)
    plt.xlabel("Time", fontsize=14)
    plt.ylabel("Number of Votes", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_image, dpi=500)
    plt.close()
