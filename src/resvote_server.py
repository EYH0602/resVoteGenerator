"""resVote Backend Server
"""

from .resdb import ResDBServer
from .datatype import Vote, Voter, Election
from .generator import generate_votes
from .util import to_vote_id
from tqdm import tqdm
from typing import Optional


class resVoteServer:
    def __init__(self, config_path: str) -> None:
        self.resdb = ResDBServer(config_path)

        # NOTE: store everything in memory for now
        # should consider using a database in the future
        self.users: dict[str, Voter] = {}
        self.elections: dict[str, Election] = {}
        self.votes: dict[str, Vote] = {}

        self._load__from_resdb()

    def _load__from_resdb(self):
        print("loading history data from ResDB")
        all_data = self.resdb.db_read_all()
        if all_data is None:
            return

        for d in tqdm(all_data):
            if d is None:
                continue

            try:
                if d["type"] == "Voter":
                    self.users[d["id"]] = Voter(**d["data"])
                elif d["type"] == "Election":
                    self.elections[d["id"]] = Election(**d["data"])
                elif d["type"] == "Vote":
                    self.votes[d["id"]] = Vote(**d["data"])
            except KeyError:
                continue

    def register(self, username: str, password: str, is_admin: bool) -> bool:
        """Register a new user. If the user already exists, return False."""
        if username in self.users:
            return False

        # add user to local cache
        new_user = Voter(voter_id=username, password=password, is_admin=is_admin)
        self.users[new_user.transaction_id] = new_user
        # add user in ResDB
        # ! ignoring whether the record is created successfully for now
        _ = self.resdb.create(new_user)

        return True

    def login(self, username: str, password: str, is_admin: bool) -> bool:
        """Login a user.
        If the user does not exist or the password is incorrect,
        return False.
        """
        if username not in self.users:
            return False

        # block non-admin users from logging in as admin
        if not self.users[username].is_admin and is_admin:
            return False

        # NOTE: should send request to ResDB to verify the password for security reasons
        # ! ignoring the verification for now
        if self.users[username].password != password:
            return False

        return True

    def create_election(self, creator: str, election_id: str, candidates: str) -> bool:
        """Create a new election.
        candidates is string separated by comma.
        If the election already exists, return False.
        If the creator is not an admin, return False.
        """
        # check if creator is an admin
        if creator not in self.users and not self.users[creator].is_admin:
            return False

        if election_id in self.elections:
            return False

        candidates_list = candidates.split(",")
        new_election = Election(
            election_id=election_id,
            candidates=candidates_list,
            creator=creator,
        )

        # add election to local cache
        self.elections[new_election.transaction_id] = new_election
        # add election in ResDB
        # ! ignoring whether the record is created successfully for now
        _ = self.resdb.create(new_election)
        return True

    def get_elections(self) -> list[str]:
        """Get a list of election IDs."""
        return list(self.elections.keys())

    def get_candidates(self, election_id: str) -> list[str]:
        """Get a list of candidate names for a given election."""
        if election_id not in self.elections:
            return []

        candidates = self.elections[election_id].candidates
        return candidates

    def create_vote(self, voter_id: str, election_id: str, candidate_name: str) -> bool:
        """Cast a vote for a candidate in an election.
        if the election, candidate, or voter does not exist, return False.
        If the voter has already voted in this election, return False.
        """
        if election_id not in self.elections:
            print(f"election_id {election_id} not in self.elections")
            return False

        if candidate_name not in self.elections[election_id].candidates:
            print(f"candidate_name {candidate_name} not in self.elections")
            return False

        # NOTE: admin can also vote
        if voter_id not in self.users and not self.users[voter_id].is_admin:
            print(f"voter_id {voter_id} not in the users")
            return False

        new_vote = Vote(
            election_id=election_id,
            candidate_name=candidate_name,
            voter_id=voter_id,
        )

        if new_vote.transaction_id in self.votes:
            return False

        # add vote to local cache
        self.votes[new_vote.transaction_id] = new_vote
        # add vote in ResDB
        # ! ignoring whether the record is created successfully for now
        _ = self.resdb.create(new_vote)
        return True

    def get_votes(self, election_id: str) -> list[Vote]:
        """Get a list of votes for a given election."""
        return [vote for vote in self.votes.values() if vote.election_id == election_id]

    def visualization(self, election_id: str):
        # ToDo - query visualization data from the ResDBServer
        pass

    def generate_random_votes(self, election_id: str) -> bool:
        """generate fake votes for visualization and testing"""

        if election_id not in self.elections:
            return False

        vs = generate_votes(election_id, self.elections[election_id].candidates)

        for voter, vote in vs:
            if voter.voter_id not in self.users:
                self.users[voter.voter_id] = voter
                _ = self.resdb.create(voter)

                self.votes[vote.transaction_id] = vote
                _ = self.resdb.create(vote)

        return True

    def get_user_vote(self, election_id: str, voter_id: str) -> Optional[str]:
        """Retrieve a vote by election_id and voter_id.

        Args:
            election_id (str): The election ID.
            voter_id (str): The voter ID.

        Returns:
            Optional[str]: The candidate name if the vote exists, None otherwise.
        """
        transaction_id = to_vote_id(election_id, voter_id)
        try:
            return self.votes[transaction_id].candidate_name
        except KeyError:
            return None

    def _get_election_votes(self, election_id: str) -> list[Vote]:
        """Get a list of votes for a given election."""
        return [vote for vote in self.votes.values() if vote.election_id == election_id]

    def total_votes(self, election_id: str) -> Optional[int]:
        """Get the total number of votes in an election.

        Args:
            election_id (str): The election ID.

        Returns:
            Optional[int]: The total number of votes if the election exists, None otherwise.
        """
        if election_id not in self.elections:
            return None

        return len(self._get_election_votes(election_id))

    def votes_per_candidate(self, election_id: str) -> Optional[dict[str, int]]:
        """Get the number of votes each candidate received in an election.

        Args:
            election_id (str): The election ID.

        Returns:
            dict[str, int]: A dictionary with candidates as keys and their vote counts as values.
        """
        if election_id not in self.elections:
            return None

        votes = self._get_election_votes(election_id)
        candidate_votes: dict[str, int] = {
            candidate: 0 for candidate in self.elections[election_id].candidates
        }
        for vote in votes:
            if vote and vote.election_id == election_id:
                candidate_votes[vote.candidate_name] += 1
        return candidate_votes

    def get_user(self, voter_id: str) -> Optional[Voter]:
        """Get the voter object by voter_id.

        Args:
            voter_id (str): The voter ID.

        Returns:
            Optional[Voter]: The voter object if the voter exists, None otherwise.
        """
        return self.users.get(voter_id, None)
