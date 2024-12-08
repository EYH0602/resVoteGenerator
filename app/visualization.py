import fire
import json
from dataclasses import asdict
from hypothesis import given
from hypothesis.strategies import lists

from src.datatype import Vote
from src.resdb import ResDBServer
from src.generator import vote_list_gen
from src.json_utils import save_votes_to_json
from src.visualization import (
    plot_candidate_distribution,
    plot_attribute_distribution,
    plot_stacked_bar,
    plot_time_series,
)


def generate_votes() -> list[Vote]:
    return vote_list_gen.example()


def main(
    config_path: str = "config.yaml",
    server_log_path: str | None = None,
    generated_json="data/generated_votes.json",
    real_json="data/real_votes.json",
) -> None:
    server = ResDBServer(config_path, server_log_path)

    # Generate and store generated votes
    generated_votes = generate_votes()  # Use the original generate_votes function
    server.create_all(generated_votes, source="generated")  # Mark as generated
    print(f"Stored {len(generated_votes)} generated votes.")

    # Step 2: Simulate real votes and store them
    ######### TO DO: Replace this with actual frontend votes in production
    real_votes = [
        Vote(
            transaction_id="real_001",
            election_id="PRESIDENTIAL_2024",
            candidate="Alice",
            state="California",
        ),
        Vote(
            transaction_id="real_002",
            election_id="PRESIDENTIAL_2024",
            candidate="Bob",
            state="Texas",
        ),
    ]
    server.create_all(real_votes, source="real")  # Mark as real
    print(f"Stored {len(real_votes)} real votes.")

    # Read and save generated votes to JSON
    read_generated_votes = server.read_generated()
    save_votes_to_json(read_generated_votes, generated_json)
    print(f"Saved {len(read_generated_votes)} generated votes to {generated_json}.")

    # Read and save real votes to JSON
    read_real_votes = server.read_real()
    save_votes_to_json(read_real_votes, real_json)
    print(f"Saved {len(read_real_votes)} real votes to {real_json}.")

    ##### TO DO: Implement the function to decide when the generated or the real shows

    # Different Visualization
    # Load the JSON data file
    # with open(output_json, "r", encoding="utf-8") as f:
    #     votes = json.load(f)

    # # votes is a list of vote records as described
    # # Now we call the visualization functions with the loaded data

    # # 1. Candidate Vote Distribution (Bar Chart)
    # plot_candidate_distribution(votes, output_image="candidate_distribution.png")

    # # 2. Attribute Distribution (Pie/Donut Chart)
    # # Example: Distribution of gender
    # plot_attribute_distribution(votes, attribute="gender", output_image="gender_distribution.png")

    # # 3. Multi-dimension Analysis (Stacked Bar)
    # # Example: gender + region combined
    # plot_stacked_bar(votes, attribute1="gender", attribute2="region", output_image="stacked_bar.png")

    # # 4. Time Series Analysis (Line Chart)
    # plot_time_series(votes, output_image="time_series.png", freq='H')

    #### TO DO: Decide how to interact with the front end
    # Fetch a specific vote
    # vote_result = server.get(election_id=election_id, voter_id=voter_id)
    # if vote_result.is_some():
    #     print(f"Vote found: {vote_result.unwrap()}")
    # else:
    #     print("Vote not found.")

    # Get total votes in an election
    # total = server.total_votes(election_id=election_id)
    # print(f"Total votes in election {election_id}: {total}")

    # Get votes per candidate
    # candidate_counts = server.votes_per_candidate(election_id=election_id)
    # print(f"Votes per candidate in election {election_id}:")
    # for candidate, count in candidate_counts.items():
    #     print(f"  {candidate}: {count} votes")


if __name__ == "__main__":
    fire.Fire(main)
