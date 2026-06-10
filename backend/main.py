"""
main.py
=======
FastAPI application exposing the NFA→DFA conversion and simulation endpoints.

Run with:
    uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import NFAInput, ConvertResponse, GraphData, GraphNode, GraphEdge
from nfa_to_dfa import NFA, NFAtoDFAConverter, EPSILON
from simulation import build_simulation_trace

app = FastAPI(
    title="NFA → DFA Visualizer API",
    description="Converts NFA (with ε-transitions) to DFA and simulates string acceptance step-by-step.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

def _nfa_graph_data(nfa: NFA) -> GraphData:
    """Build GraphData for the NFA directly from its definition."""
    nodes = [
        GraphNode(
            id=s,
            label=s,
            is_start=(s == nfa.start_state),
            is_accept=(s in nfa.accept_states),
            is_dead=False,
        )
        for s in sorted(nfa.states)
    ]

    # Flatten transitions, merge parallel labels, render ε nicely
    edge_map: dict[tuple[str, str], list[str]] = {}
    for src, sym_map in nfa.transitions.items():
        for sym, targets in sym_map.items():
            display_sym = "ε" if sym == EPSILON else sym
            for tgt in targets:
                edge_map.setdefault((src, tgt), []).append(display_sym)

    edges = [
        GraphEdge(
            id=f"e{i}",
            source=src,
            target=tgt,
            label=", ".join(sorted(syms)),
        )
        for i, ((src, tgt), syms) in enumerate(sorted(edge_map.items()))
    ]

    return GraphData(nodes=nodes, edges=edges)


def _dfa_graph_data(dfa_serial: dict) -> GraphData:
    """Convert the DFA's to_serializable() output into GraphData."""
    nodes = [
        GraphNode(
            id=n["id"],
            label=n["id"],
            is_start=n["is_start"],
            is_accept=n["is_accept"],
            is_dead=n.get("is_dead", False),
        )
        for n in dfa_serial["nodes"]
    ]

    edges = [
        GraphEdge(
            id=f"e{i}",
            source=e["from"],
            target=e["to"],
            label=e["label"],
        )
        for i, e in enumerate(dfa_serial["edges"])
    ]

    return GraphData(nodes=nodes, edges=edges)


# -------------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/api/convert", response_model=ConvertResponse)
def convert(body: NFAInput):
    """
    Accept an NFA definition (and optional input string) and return:
    - The NFA as a graph (nodes + edges)
    - The equivalent DFA as a graph (nodes + edges)
    - (Optional) Step-by-step simulation trace if input_string was provided
    """
    # Re-hydrate transitions: JSON arrays → Python sets
    transitions = {
        state: {sym: set(targets) for sym, targets in sym_map.items()}
        for state, sym_map in body.transitions.items()
    }

    try:
        nfa = NFA(
            states=set(body.states),
            alphabet=set(body.alphabet),
            transitions=transitions,
            start_state=body.start_state,
            accept_states=set(body.accept_states),
        )
        nfa.validate()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Run subset construction
    converter = NFAtoDFAConverter(nfa)
    dfa = converter.convert(include_dead_state=True)
    dfa_serial = dfa.to_serializable()

    # Optional simulation
    simulation = None
    if body.input_string is not None:
        simulation = build_simulation_trace(nfa, body.input_string)

    return ConvertResponse(
        nfa=_nfa_graph_data(nfa),
        dfa=_dfa_graph_data(dfa_serial),
        simulation=simulation,
    )


@app.post("/api/simulate")
def simulate_only(body: NFAInput):
    """
    Run simulation only (without full DFA conversion).
    Useful for testing a string against an existing NFA quickly.
    Requires input_string to be set.
    """
    if body.input_string is None:
        raise HTTPException(status_code=422, detail="input_string is required for /api/simulate")

    transitions = {
        state: {sym: set(targets) for sym, targets in sym_map.items()}
        for state, sym_map in body.transitions.items()
    }

    try:
        nfa = NFA(
            states=set(body.states),
            alphabet=set(body.alphabet),
            transitions=transitions,
            start_state=body.start_state,
            accept_states=set(body.accept_states),
        )
        nfa.validate()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return build_simulation_trace(nfa, body.input_string)
