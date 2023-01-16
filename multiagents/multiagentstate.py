from dataclasses import dataclass
from enum import Enum
from typing import Optional, List


class MultiAgentRunningState(Enum):
    RUNNING = 0
    SUCCESS = 1
    CANCELLED = 2
    TERMINATED = 3
    DECEASED = 4
    TIMEOUT = 5


@dataclass
class MultiAgentState:
    role: int
    running_state: MultiAgentRunningState
    completion_time: Optional[float]
    position: List[float]
    blueprint_results: List[List[bool]]
