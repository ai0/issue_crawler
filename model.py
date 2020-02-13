from dataclasses import dataclass


@dataclass
class Issue:
    id: int
    title: str
    url: str
    date: str
    labels: list
