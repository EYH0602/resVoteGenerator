# type: ignore
import xmlrpc.client
from dataclasses import asdict
import fire
from src.datatype import Vote
from src.resdb import ResDBServer
from src.generator import generate_votes
from src.json_utils import save_votes_to_json
from src.util import load_server_config
from src.visualization import (
    plot_candidate_distribution,
    plot_attribute_distribution,
    plot_stacked_bar,
    plot_time_series,
)


def main(config_path: str = "config.yaml") -> None:
    host, port = load_server_config(config_path).unwrap()

    url = f"http://{host}:{port}"
    s = xmlrpc.client.ServerProxy(url)

    username = "admin"
    password = "admin"

    if not s.login(username, password, True):
        s.register(username, password, True)

    def vote2dict(vote: Vote) -> dict:
        d = asdict(vote)
        voter_attributes = s.get_voter(vote.voter_id)
        assert voter_attributes is not None
        d["attributes"] = asdict(voter_attributes)
        return d

    elections = s.get_elections()
    all_votes = []
    for eid in elections:
        all_votes += [vote2dict(v) for v in s.get_votes(eid)]

    # 1. Candidate Vote Distribution (Bar Chart)
    plot_candidate_distribution(votes, output_image="candidate_distribution.png")

    # 2. Attribute Distribution (Pie/Donut Chart)
    # Example: Distribution of gender
    plot_attribute_distribution(
        votes, attribute="gender", output_image="gender_distribution.png"
    )

    # 3. Multi-dimension Analysis (Stacked Bar)
    # Example: gender + region combined
    plot_stacked_bar(
        votes, attribute1="gender", attribute2="region", output_image="stacked_bar.png"
    )

    # 4. Time Series Analysis (Line Chart)
    plot_time_series(votes, output_image="time_series.png", freq="H")


if __name__ == "__main__":
    fire.Fire(main)
