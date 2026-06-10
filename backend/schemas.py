"""
schemas.py
==========
Pydantic v2 request and response models for the NFA→DFA API.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class NFAInput(BaseModel):
    states: list[str] = Field(..., min_length=1)
    alphabet: list[str] = Field(..., min_length=1)
    # JSON has no set type — transitions use list[str] for targets
    transitions: dict[str, dict[str, list[str]]]
    start_state: str
    accept_states: list[str]
    input_string: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def start_must_be_in_states(self) -> "NFAInput":
        if self.start_state not in self.states:
            raise ValueError(f"start_state '{self.start_state}' not in states")
        return self


class GraphNode(BaseModel):
    id: str
    label: str
    is_start: bool
    is_accept: bool
    is_dead: bool = False


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str


class GraphData(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class SimulationStep(BaseModel):
    step_index: int
    symbol_read: Optional[str]
    active_states: list[str]
    description: str


class SimulationResult(BaseModel):
    input_string: str
    accepted: bool
    steps: list[SimulationStep]


class ConvertResponse(BaseModel):
    nfa: GraphData
    dfa: GraphData
    simulation: Optional[SimulationResult] = None
