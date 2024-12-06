from dataclasses import dataclass, field
from typing import Any, Dict
from datetime import datetime
import random
from datetime import datetime, timedelta

def generate_random_timestamp(start_date, end_date):
    delta = end_date - start_date
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)

@dataclass
class Vote:
    election_id: str
    candidate_name: str
    voter_id: str
    attributes: Dict[str, str] = field(default_factory=dict)
    #transfer datetime to json format
    timestamp: datetime = generate_random_timestamp(datetime(2024, 10, 16, 0, 0, 0), datetime(2024, 11, 5, 23, 59, 59)).isoformat()
    
    @property
    def transaction_id(self):
        return f"{self.election_id}++{self.voter_id}"



