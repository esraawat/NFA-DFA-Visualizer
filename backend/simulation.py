"""
simulation.py
=============
Builds a step-by-step execution trace for NFA simulation.
Each step captures the active NFA states after reading one symbol,
enabling the frontend to animate the traversal one character at a time.
"""

from __future__ import annotations
from nfa_to_dfa import NFA, NFAtoDFAConverter


def build_simulation_trace(nfa: NFA, input_string: str) -> dict:
    """
    Simulate *nfa* on *input_string* and return a structured trace.

    Returns
    -------
    dict with keys:
        input_string : str
        accepted     : bool
        steps        : list of step dicts (one per symbol + initial step)
    """
    converter = NFAtoDFAConverter(nfa)
    steps = []

    # Step 0 — before reading any symbol
    current = converter.epsilon_closure({nfa.start_state})
    state_str = "{" + ", ".join(sorted(current)) + "}" if current else "∅"
    steps.append({
        "step_index": 0,
        "symbol_read": None,
        "active_states": sorted(current),
        "description": f"Initial: ε-closure({{{nfa.start_state}}}) = {state_str}",
    })

    # One step per symbol in the input string
    for i, symbol in enumerate(input_string, start=1):
        if symbol not in nfa.alphabet:
            # Symbol not in alphabet — machine dies immediately
            steps.append({
                "step_index": i,
                "symbol_read": symbol,
                "active_states": [],
                "description": f"Symbol '{symbol}' not in alphabet — rejected",
            })
            current = frozenset()
            break

        moved = converter.move(current, symbol)
        current = converter.epsilon_closure(moved)

        moved_str = "{" + ", ".join(sorted(moved)) + "}" if moved else "∅"
        next_str  = "{" + ", ".join(sorted(current)) + "}" if current else "∅"

        steps.append({
            "step_index": i,
            "symbol_read": symbol,
            "active_states": sorted(current),
            "description": (
                f"Read '{symbol}': "
                f"move → {moved_str}, "
                f"ε-closure → {next_str}"
            ),
        })

        if not current:
            # Dead configuration — no point continuing
            break

    accepted = bool(current & nfa.accept_states)
    return {
        "input_string": input_string,
        "accepted": accepted,
        "steps": steps,
    }
