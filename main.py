from resdb_orm import ResDBORM
import fire
import json
from dataclasses import asdict
from hypothesis import given
from hypothesis.strategies import lists

from src.datatype import Vote
from src.vote_server import VoteServer
from src.generator import vote_list_gen
from src.json_utils import save_votes_to_json
from src.visualization import (
    plot_candidate_distribution,
    plot_attribute_distribution,
    plot_grouped_bar_chart,
    plot_candidate_time_series
)

def generate_votes() -> list[Vote]:
    return vote_list_gen.example()


# Wrapper function to plot for multiple attributes
def plot_grouped_bar_multiple_attributes(votes, attributes = ["gender", "age", "region", "race", "education"], output_dir: str = "data/"):
    """
    Plot grouped bar charts for multiple attributes.

    Parameters:
        votes: List of votes with attributes and candidate names.
        attributes: List of attributes to analyze.
        output_dir: Directory to save the output images.
    """
    for attribute in attributes:
        output_image = f"{output_dir}{attribute}_grouped_bar_chart.png"
        plot_grouped_bar_chart(votes, attribute, output_image=output_image)
        
def plot_multiple_attributes(votes, attributes = ["gender", "age", "region", "race", "education"]):
    for attribute in attributes:
        plot_attribute_distribution(votes, attribute=attribute)
        
def main(config_path: str = "config.yaml", server_log_path: str | None = None, output_json: str = "data/random_output.json") -> None:
    server = VoteServer(config_path, server_log_path)
    vs = generate_votes() 
    ids = server.create_all(vs)
    print(server.record_ids)
    all_ = server.read_all()
        # for a in all_:
        # print(a)
    # Export the vote data to a JSON file
    save_votes_to_json(all_, output_json)
    
    # Different Visualization
    # Load the JSON data file
    
    with open(output_json, "r", encoding="utf-8") as f:
        votes = json.load(f)

    # # votes is a list of vote records as described


    # 1. Candidate Vote Distribution (Bar Chart)
    plot_candidate_distribution(votes, output_image="data/candidate_distribution.png")

    # 2. Attribute Distribution for Total Number(Pie/Donut Chart)
    plot_multiple_attributes(votes)
    
    # 3. Attribute Distribution for Different Candidates(Grouped Bar Chart)
    plot_grouped_bar_multiple_attributes(votes)

    # 3. Time Series Analysis (Line Chart)
    plot_candidate_time_series(votes, output_image="data/time_series.png", freq='D')

    # After running main.py, you will find the generated charts in the current directory
 

    

if __name__ == "__main__":
    fire.Fire(main)
