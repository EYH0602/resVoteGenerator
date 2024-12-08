# type: ignore
import xmlrpc.client
import fire
from src.util import load_server_config


def main(config_path: str = "config.yaml"):
    host, port = load_server_config(config_path).unwrap()

    url = f"http://{host}:{port}"
    s = xmlrpc.client.ServerProxy(url)

    username = "yfhe"
    password = "aaaa"

    s.register(username, password, True)
    s.login(username, password, True)

    assert s.create_election(username, "election0", "Alice,Bob,Charlie")
    assert s.create_election(username, "election2", "aa,bb,cc")

    election_ids: list[str] = s.get_elections()
    print(election_ids)
    for election_id in election_ids:
        print(election_id)
        candidates = s.get_candidates(election_id)
        print(candidates)

    election_id = "election0"
    s.generate_random_votes(election_id)

    # voters = s.get_voters()
    # for v in voters:
    #     print(v)

    votes = s.get_votes(election_id)
    for v in votes:
        print(v)


if __name__ == "__main__":
    fire.Fire(main)
