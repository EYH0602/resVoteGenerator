import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Any
import plotly.express as px
import pandas as pd



# Set a modern and clean style for charts
sns.set_theme(style="whitegrid")
#finished maybe more beautiful
def plot_candidate_distribution(votes: List[Dict[str, Any]], output_image: str = "candidate_distribution.png"):
    """
    Plot a bar chart showing total votes for each candidate.
    X-axis: Candidates
    Y-axis: Vote counts
    """
    # Count votes per candidate
    candidate_counts = Counter(v['candidate_name'] for v in votes)
    
    candidates = list(candidate_counts.keys())
    counts = list(candidate_counts.values())
    
    plt.figure(figsize=(8,6))
    sns.barplot(x=candidates, y=counts, palette="viridis")
    plt.title("Candidate Vote Distribution", fontsize=16)
    plt.xlabel("Candidates", fontsize=14)
    plt.ylabel("Number of Votes", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_image, dpi=300)
    plt.close()


    
def plot_attribute_distribution(votes: List[Dict[str, Any]], attribute: str = "gender", output_image: str = "attribute_distribution.png"):
    """
    Plot a pie chart (or donut chart) showing the distribution of a single voter attribute.
    For example, gender distribution or region distribution. 
    If the attribute is 'age', group ages into ranges.
    """
    # Special handling for age attribute
    if attribute == "age":
        # Define age ranges
        def age_range(age):
            if age < 18:
                return "Under 18"
            elif 18 <= age <= 24:
                return "18-24"
            elif 25 <= age <= 34:
                return "25-34"
            elif 35 <= age <= 44:
                return "35-44"
            elif 45 <= age <= 54:
                return "45-54"
            elif 55 <= age <= 64:
                return "55-64"
            elif age >= 65:
                return "65+"
            return "Unknown"

        attr_counts = Counter(age_range(v['attributes'].get(attribute, -1)) for v in votes)
    else:
        # General case for other attributes
        attr_counts = Counter(v['attributes'].get(attribute, "Unknown") for v in votes)
    
    # Extract labels and sizes
    labels = list(attr_counts.keys())
    sizes = list(attr_counts.values())
    
    # Plotting
    if(attribute == "region"):
        plt.figure(figsize=(15, 15)) 
    else:
        plt.figure(figsize=(6, 6))
    wedges, texts, autotexts = plt.pie(
        sizes, 
        labels=labels, 
        autopct="%1.1f%%", 
        startangle=90, 
        pctdistance=0.85
    )
    # Draw a circle in the center to make it a donut
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    
    # Title and save
    plt.title(f"Distribution of {attribute.capitalize()}", fontsize=16)
    plt.tight_layout()
    plt.savefig(f"data/{attribute}_{output_image}", dpi=300)
    plt.close()
    


def plot_grouped_bar_chart(votes: List[Dict[str, Any]], attribute: str, output_image: str = "grouped_bar_chart.png"):
    """
    Plot a grouped bar chart for a specific attribute, showing its distribution among different candidates.

    Parameters:
        votes: List of votes with attributes and candidate names.
        attribute: The attribute to analyze ("gender", "age", "race", "education", "region").
        output_image: The file name for the output image.
    """
    # Process age attribute into ranges if selected
    def process_age(age):
        if age is None or age == "Unknown":
            return "Unknown"
        if age < 18:
            return "Under 18"
        elif 18 <= age <= 24:
            return "18-24"
        elif 25 <= age <= 34:
            return "25-34"
        elif 35 <= age <= 44:
            return "35-44"
        elif 45 <= age <= 54:
            return "45-54"
        elif 55 <= age <= 64:
            return "55-64"
        else:
            return "65+"

    # Extract the specified attribute and candidate
    data = []
    for v in votes:
        value = v['attributes'].get(attribute, "Unknown")
        if attribute == "age":
            value = process_age(value)
        data.append((value, v['candidate_name']))
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=[attribute.capitalize(), "Candidate"])
    
    # Count votes by attribute and candidate
    vote_counts = df.groupby([attribute.capitalize(), "Candidate"]).size().reset_index(name="Votes")
    vote_counts = vote_counts.pivot(index=attribute.capitalize(), columns="Candidate", values="Votes").fillna(0)
    
    # Sort by total votes for readability
    vote_counts["Total"] = vote_counts.sum(axis=1)
    vote_counts = vote_counts.sort_values("Total", ascending=False).drop(columns=["Total"])
    
    # Plot grouped bar chart
    vote_counts.plot(kind="bar", figsize=(14, 8), width=0.8)
    plt.title(f"Distribution of {attribute.capitalize()} by Candidate", fontsize=16)
    plt.xlabel(attribute.capitalize(), fontsize=14)
    plt.ylabel("Number of Votes", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Candidate", fontsize=12)
    plt.tight_layout()
    plt.savefig(output_image, dpi=300)
    plt.close()
    
    
def plot_candidate_time_series(votes: List[Dict[str, Any]], output_image: str = "time_series_candidates.png", freq: str = 'H'):
    """
    Plot a line chart showing how total votes and votes for each candidate evolve over time.
    
    Parameters:
        votes: List of votes with timestamps and candidate names.
        output_image: Output image file name.
        freq: Resampling frequency ('H' for hour, 'D' for day, etc.).
    """
    # Convert timestamps to datetime objects
    times = [datetime.fromisoformat(v['timestamp']) for v in votes]
    candidates = [v['candidate_name'] for v in votes]
    
    # Create a DataFrame
    df = pd.DataFrame({"time": times, "candidate": candidates})
    
    # Set time as the index and sort
    df = df.set_index('time').sort_index()
    
    # Resample and count overall votes
    total_count = df.resample(freq).size()
    
    # Resample and count votes for each candidate
    candidate_counts = df.groupby('candidate').resample(freq).size().unstack(level=0, fill_value=0)
    
    # Plot the time series
    plt.figure(figsize=(12, 6))
    
    # Plot overall votes
    sns.lineplot(x=total_count.index, y=total_count.values, label="Total Votes", color="black", linestyle="--", linewidth=2)
    
    # Plot votes for each candidate
    for candidate in candidate_counts.columns:
        sns.lineplot(x=candidate_counts.index, y=candidate_counts[candidate], label=f"{candidate} Votes")
    
    # Chart formatting
    plt.title("Voting Trend Over Time (Total and By Candidate)", fontsize=16)
    plt.xlabel("Time", fontsize=14)
    plt.ylabel("Number of Votes", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Legend", fontsize=12)
    plt.tight_layout()
    plt.savefig(output_image, dpi=300)
    plt.close()
