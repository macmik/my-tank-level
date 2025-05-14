import dataclasses
from datetime import datetime as DT


@dataclasses.dataclass(frozen=True)
class Measurement:
    ts: DT
    distance: int
