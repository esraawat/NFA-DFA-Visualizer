"""
nfa_to_dfa.py
=============
Production-ready Python module that converts a Nondeterministic Finite Automaton
(NFA) with ε-transitions into a Deterministic Finite Automaton (DFA) using the
Subset Construction (Powerset Construction) algorithm.

Author  : Expert Software Engineer / Theoretical CS
Version : 1.0.0

Theory recap
------------
Given NFA M = (Q, Σ, δ, q0, F):
  • ε-closure(S) — the set of all NFA states reachable from any state in S
                   by following *only* ε-transitions (zero or more).
  • move(S, a)   — the set of all NFA states reachable from any state in S
                   by following *exactly one* transition on symbol a.
  • Each DFA state D is a frozenset of NFA states.
  • DFA start state  = ε-closure({q0})
  • DFA transitions  = δ'(D, a) = ε-closure(move(D, a))
  • DFA accept states = {D | D ∩ F ≠ ∅}
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EPSILON: str = "epsilon"   # Sentinel string used as the ε-transition symbol.
DEAD_STATE_LABEL: str = "∅"  # Human-readable label for the dead / trap state.


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class NFA:
    """
    Represents a Nondeterministic Finite Automaton with ε-transitions.

    Attributes
    ----------
    states : set[str]
        The finite set of state names (e.g. {'q0', 'q1', 'q2'}).
    alphabet : set[str]
        The input alphabet Σ.  Must NOT contain EPSILON — epsilon transitions
        are encoded separately via the transition function.
    transitions : dict[str, dict[str, set[str]]]
        Nested mapping  state → symbol → {reachable states}.
        Use EPSILON as the symbol key to encode ε-transitions.
        Missing state/symbol pairs simply mean no transition exists.
    start_state : str
        The unique start state q0.
    accept_states : set[str]
        The set of accepting / final states F ⊆ Q.

    Example
    -------
    transitions = {
        'q0': {EPSILON: {'q1'}, 'a': {'q0'}},
        'q1': {'b': {'q2'}},
    }
    """

    states: Set[str]
    alphabet: Set[str]
    transitions: Dict[str, Dict[str, Set[str]]]
    start_state: str
    accept_states: Set[str]

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """
        Perform basic consistency checks and raise ValueError on violation.
        Call this before running the converter to catch data-entry mistakes early.
        """
        if self.start_state not in self.states:
            raise ValueError(
                f"Start state '{self.start_state}' is not in the states set."
            )
        unknown_accept = self.accept_states - self.states
        if unknown_accept:
            raise ValueError(
                f"Accept states {unknown_accept} are not in the states set."
            )
        if EPSILON in self.alphabet:
            raise ValueError(
                f"The alphabet must not contain the epsilon symbol '{EPSILON}'. "
                "Epsilon transitions are encoded inside the transitions dict."
            )
        for src, symbol_map in self.transitions.items():
            if src not in self.states:
                raise ValueError(
                    f"Transition source '{src}' is not in the states set."
                )
            for sym, targets in symbol_map.items():
                if sym != EPSILON and sym not in self.alphabet:
                    raise ValueError(
                        f"Transition symbol '{sym}' from state '{src}' is not "
                        "in the alphabet (and is not epsilon)."
                    )
                for tgt in targets:
                    if tgt not in self.states:
                        raise ValueError(
                            f"Transition target '{tgt}' (from '{src}' on '{sym}') "
                            "is not in the states set."
                        )

    # ------------------------------------------------------------------
    # Pretty-print
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        lines = [
            "NFA",
            f"  States       : {sorted(self.states)}",
            f"  Alphabet     : {sorted(self.alphabet)}",
            f"  Start state  : {self.start_state}",
            f"  Accept states: {sorted(self.accept_states)}",
            "  Transitions  :",
        ]
        for src in sorted(self.transitions):
            for sym in sorted(self.transitions[src]):
                targets = sorted(self.transitions[src][sym])
                lines.append(f"    δ({src}, {sym}) = {{{', '.join(targets)}}}")
        return "\n".join(lines)


@dataclass
class DFA:
    """
    Represents the Deterministic Finite Automaton produced by subset construction.

    Attributes
    ----------
    states : set[frozenset[str]]
        Each DFA state is a frozenset of NFA states.
        The special value frozenset() represents the dead / trap state.
    alphabet : set[str]
        Identical to the NFA alphabet.
    transitions : dict[frozenset[str], dict[str, frozenset[str]]]
        Complete transition function.  Every (state, symbol) pair has an entry
        (dead-state transitions are included for totality).
    start_state : frozenset[str]
        ε-closure of the NFA start state.
    accept_states : set[frozenset[str]]
        Every DFA state that contains at least one NFA accept state.
    dead_state : frozenset[str]
        The empty frozenset acting as the trap / sink state.
        Present in transitions only when actually reachable.
    """

    states: Set[FrozenSet[str]]
    alphabet: Set[str]
    transitions: Dict[FrozenSet[str], Dict[str, FrozenSet[str]]]
    start_state: FrozenSet[str]
    accept_states: Set[FrozenSet[str]]
    dead_state: FrozenSet[str] = field(default_factory=frozenset)

    # ------------------------------------------------------------------
    # Human-readable label helpers
    # ------------------------------------------------------------------

    @staticmethod
    def label_for(dfa_state: FrozenSet[str]) -> str:
        """
        Convert a frozenset DFA state into a deterministic, readable label.

        frozenset()           →  '∅'   (dead state)
        frozenset({'q0'})     →  'q0'
        frozenset({'q0','q1'})→  'q0_q1'  (sorted for determinism)
        """
        if not dfa_state:
            return DEAD_STATE_LABEL
        return "_".join(sorted(dfa_state))

    # ------------------------------------------------------------------
    # JSON-serialisable export
    # ------------------------------------------------------------------

    def to_serializable(self) -> dict:
        """
        Return a JSON-serialisable dict representation of the DFA, suitable
        for transmission to a React front-end graph renderer.

        Schema
        ------
        {
          "states": ["q0", "q0_q1", "∅", ...],
          "alphabet": ["a", "b"],
          "start_state": "q0",
          "accept_states": ["q0_q1", ...],
          "dead_state": "∅",
          "transitions": {
              "q0": {"a": "q0_q1", "b": "∅"},
              ...
          },
          "nodes": [{"id": "q0", "is_start": true, "is_accept": false}, ...],
          "edges": [{"from": "q0", "to": "q0_q1", "label": "a"}, ...]
        }

        The 'nodes' and 'edges' lists are ready to be consumed directly by a
        graph-rendering library such as React Flow or D3.
        """
        lbl = self.label_for

        # -- states --------------------------------------------------------
        state_labels = sorted(lbl(s) for s in self.states)

        # -- transitions ---------------------------------------------------
        trans_serialized: Dict[str, Dict[str, str]] = {}
        for src_set, symbol_map in self.transitions.items():
            src_label = lbl(src_set)
            trans_serialized[src_label] = {
                sym: lbl(tgt_set)
                for sym, tgt_set in symbol_map.items()
            }

        # -- nodes (graph vertices) ----------------------------------------
        nodes = []
        for s in self.states:
            nodes.append(
                {
                    "id": lbl(s),
                    "is_start": s == self.start_state,
                    "is_accept": s in self.accept_states,
                    "is_dead": s == self.dead_state and not s,
                }
            )
        nodes.sort(key=lambda n: n["id"])

        # -- edges (graph directed arcs) -----------------------------------
        # Merge parallel edges (same src→dst) into comma-separated labels.
        edge_map: Dict[Tuple[str, str], list] = {}
        for src_set, symbol_map in self.transitions.items():
            src_label = lbl(src_set)
            for sym, tgt_set in symbol_map.items():
                tgt_label = lbl(tgt_set)
                key = (src_label, tgt_label)
                edge_map.setdefault(key, []).append(sym)

        edges = [
            {"from": src, "to": tgt, "label": ", ".join(sorted(syms))}
            for (src, tgt), syms in sorted(edge_map.items())
        ]

        return {
            "states": state_labels,
            "alphabet": sorted(self.alphabet),
            "start_state": lbl(self.start_state),
            "accept_states": sorted(lbl(s) for s in self.accept_states),
            "dead_state": lbl(self.dead_state),
            "transitions": trans_serialized,
            "nodes": nodes,
            "edges": edges,
        }

    # ------------------------------------------------------------------
    # Pretty-print
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        lbl = self.label_for
        lines = [
            "DFA  (result of subset construction)",
            f"  States       : {sorted(lbl(s) for s in self.states)}",
            f"  Alphabet     : {sorted(self.alphabet)}",
            f"  Start state  : {lbl(self.start_state)}",
            f"  Accept states: {sorted(lbl(s) for s in self.accept_states)}",
            f"  Dead state   : {lbl(self.dead_state)}",
            "  Transitions  :",
        ]
        for src in sorted(self.transitions, key=lbl):
            for sym in sorted(self.transitions[src]):
                tgt = self.transitions[src][sym]
                lines.append(f"    δ'({lbl(src)}, {sym}) = {lbl(tgt)}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core Algorithm
# ---------------------------------------------------------------------------

class NFAtoDFAConverter:
    """
    Converts an NFA (with ε-transitions) to an equivalent DFA using the
    Subset Construction / Powerset Construction algorithm.

    Usage
    -----
    converter = NFAtoDFAConverter(nfa)
    dfa = converter.convert()
    """

    def __init__(self, nfa: NFA) -> None:
        """
        Parameters
        ----------
        nfa : NFA
            A fully constructed and validated NFA instance.
        """
        nfa.validate()
        self._nfa = nfa

    # ------------------------------------------------------------------
    # ε-closure
    # ------------------------------------------------------------------

    def epsilon_closure(self, states: Iterable[str]) -> FrozenSet[str]:
        """
        Compute ε-closure(S) — the set of NFA states reachable from any
        state in *states* by following zero or more ε-transitions.

        The implementation uses an iterative DFS with an explicit stack to
        avoid Python's recursion depth limit on large automata.

        Parameters
        ----------
        states : iterable of str
            Seed NFA states.

        Returns
        -------
        frozenset[str]
            Immutable set of reachable NFA states (always includes the seeds).
        """
        closure: Set[str] = set()
        stack: list[str] = []

        # Seed the stack with all starting states.
        for s in states:
            if s not in closure:
                closure.add(s)
                stack.append(s)

        while stack:
            current = stack.pop()
            # Retrieve ε-successors; default to empty set if none defined.
            eps_targets: Set[str] = (
                self._nfa.transitions
                .get(current, {})
                .get(EPSILON, set())
            )
            for target in eps_targets:
                if target not in closure:
                    closure.add(target)
                    stack.append(target)

        return frozenset(closure)

    # ------------------------------------------------------------------
    # move
    # ------------------------------------------------------------------

    def move(self, states: Iterable[str], symbol: str) -> FrozenSet[str]:
        """
        Compute move(S, a) — the set of NFA states reachable from any state
        in *states* by following exactly one transition on *symbol* (ignoring ε).

        Parameters
        ----------
        states : iterable of str
            Current set of NFA states.
        symbol : str
            An alphabet symbol (must not be EPSILON).

        Returns
        -------
        frozenset[str]
            Possibly empty set of reachable NFA states.
        """
        reachable: Set[str] = set()
        for s in states:
            targets: Set[str] = (
                self._nfa.transitions
                .get(s, {})
                .get(symbol, set())
            )
            reachable.update(targets)
        return frozenset(reachable)

    # ------------------------------------------------------------------
    # Subset Construction
    # ------------------------------------------------------------------

    def convert(self, include_dead_state: bool = True) -> DFA:
        """
        Run the Subset Construction algorithm and return the equivalent DFA.

        Parameters
        ----------
        include_dead_state : bool, default True
            When True, explicitly add the dead (trap) state and all transitions
            leading into it, producing a *total* DFA where every (state, symbol)
            pair has a defined successor.
            When False, omit the dead state (and transitions to it), producing a
            *partial* / incomplete DFA that may be preferred for minimisation
            or display purposes.

        Returns
        -------
        DFA
            The constructed deterministic finite automaton.

        Algorithm
        ---------
        1. dfa_start ← ε-closure({nfa.start_state})
        2. worklist  ← deque([dfa_start])
        3. visited   ← {dfa_start}
        4. While worklist not empty:
             D ← worklist.popleft()
             For each symbol a in Σ:
               T ← ε-closure(move(D, a))
               record transition D --a--> T
               If T ∉ visited:
                 visited.add(T)
                 worklist.append(T)
        5. Accept states ← {D | D ∩ F ≠ ∅}
        """
        nfa = self._nfa
        dead_state: FrozenSet[str] = frozenset()  # The ∅ trap state.

        # Step 1 — DFA start state.
        dfa_start: FrozenSet[str] = self.epsilon_closure({nfa.start_state})

        # Bookkeeping structures.
        dfa_states: Set[FrozenSet[str]] = set()
        dfa_transitions: Dict[FrozenSet[str], Dict[str, FrozenSet[str]]] = {}
        worklist: deque[FrozenSet[str]] = deque()
        dead_state_reached: bool = False

        # Initialise with the start state.
        dfa_states.add(dfa_start)
        worklist.append(dfa_start)

        # Step 4 — BFS over newly discovered DFA states.
        while worklist:
            current_dfa_state: FrozenSet[str] = worklist.popleft()
            dfa_transitions[current_dfa_state] = {}

            for symbol in sorted(nfa.alphabet):  # sorted for determinism
                # Compute the successor DFA state.
                moved: FrozenSet[str] = self.move(current_dfa_state, symbol)
                successor: FrozenSet[str] = self.epsilon_closure(moved)

                # --- Edge case: empty successor → dead / trap state ----------
                if not successor:
                    # successor is already frozenset() == dead_state.
                    if include_dead_state:
                        dead_state_reached = True
                        dfa_transitions[current_dfa_state][symbol] = dead_state
                    # else: simply do not record the transition (partial DFA).
                else:
                    dfa_transitions[current_dfa_state][symbol] = successor
                    if successor not in dfa_states:
                        dfa_states.add(successor)
                        worklist.append(successor)

        # Step 5 — If dead state was ever reached, add its self-loop transitions.
        if include_dead_state and dead_state_reached:
            dfa_states.add(dead_state)
            dfa_transitions[dead_state] = {
                symbol: dead_state for symbol in nfa.alphabet
            }

        # Step 5 — Identify DFA accept states.
        dfa_accept_states: Set[FrozenSet[str]] = {
            d for d in dfa_states
            if d & nfa.accept_states  # non-empty intersection
        }

        return DFA(
            states=dfa_states,
            alphabet=set(nfa.alphabet),
            transitions=dfa_transitions,
            start_state=dfa_start,
            accept_states=dfa_accept_states,
            dead_state=dead_state,
        )


# ---------------------------------------------------------------------------
# Simulation Utilities (optional, useful for testing)
# ---------------------------------------------------------------------------

def simulate_nfa(nfa: NFA, input_string: str) -> bool:
    """
    Simulate the NFA on *input_string* using the subset-tracking approach.
    Returns True iff the NFA accepts the string.

    This is independent of the DFA conversion — used to verify correctness.
    """
    converter = NFAtoDFAConverter(nfa)
    current: FrozenSet[str] = converter.epsilon_closure({nfa.start_state})

    for symbol in input_string:
        if symbol not in nfa.alphabet:
            return False  # Symbol not in alphabet → reject immediately.
        moved = converter.move(current, symbol)
        current = converter.epsilon_closure(moved)

    return bool(current & nfa.accept_states)


def simulate_dfa(dfa: DFA, input_string: str) -> bool:
    """
    Simulate the DFA on *input_string*.
    Returns True iff the DFA accepts the string.
    """
    current: FrozenSet[str] = dfa.start_state

    for symbol in input_string:
        if symbol not in dfa.alphabet:
            return False
        # If the state has no outgoing transition for this symbol, we are in
        # a dead configuration (possible in a partial DFA).
        current = dfa.transitions.get(current, {}).get(symbol, frozenset())

    return current in dfa.accept_states


# ---------------------------------------------------------------------------
# Pretty-print helper
# ---------------------------------------------------------------------------

def print_section(title: str, width: int = 72) -> None:
    """Print a clearly delimited section header."""
    bar = "=" * width
    print(f"\n{bar}")
    print(f"  {title}")
    print(bar)


# ---------------------------------------------------------------------------
# Main — concrete demonstration
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    """
    Demonstrate the NFA → DFA conversion on two example automata.

    Example 1 — NFA recognising strings over {a, b} that END in 'ab'
    -----------------------------------------------------------------
    Language: Σ* · 'ab'   (any string whose suffix is "ab")

    NFA construction (with ε):
      States : {q0, q1, q2}
      q0 — start state; loops on 'a' and 'b' (handles Σ*)
      q0 --a--> q1  (start of potential "ab" suffix)
      q1 --b--> q2  (complete "ab" suffix)
      q2 — accept state

    Example 2 — NFA with prominent ε-transitions
    ---------------------------------------------
    Language: strings of the form  a*  |  b+  (union via ε-NFA)

      States : {s, q0, q1, r0, r1}
      s  — start, ε-transitions to both q0 and r0
      q0 --a--> q1,  q1 --a--> q1,  q1 — accept   (a+)
      r0 --b--> r1,  r1 --b--> r1,  r1 — accept   (b+)
      s  also ε--> q1  to accept the empty string for the a* branch
    """

    # ------------------------------------------------------------------ #
    #  Example 1 : NFA recognising strings ending in 'ab'                 #
    # ------------------------------------------------------------------ #
    print_section("EXAMPLE 1 — NFA accepting strings ending in 'ab'")

    nfa1 = NFA(
        states={'q0', 'q1', 'q2'},
        alphabet={'a', 'b'},
        transitions={
            'q0': {
                'a': {'q0', 'q1'},   # stay in q0 (loop) or start suffix
                'b': {'q0'},         # stay in q0 on 'b'
            },
            'q1': {
                'b': {'q2'},         # complete the 'ab' suffix
            },
            # q2 has no outgoing transitions (it is an accept state)
        },
        start_state='q0',
        accept_states={'q2'},
    )

    print("\n--- Original NFA ---")
    print(nfa1)

    converter1 = NFAtoDFAConverter(nfa1)
    dfa1 = converter1.convert(include_dead_state=True)

    print("\n--- Resulting DFA ---")
    print(dfa1)

    print("\n--- DFA as JSON-serialisable dict (for React frontend) ---")
    print(json.dumps(dfa1.to_serializable(), indent=2))

    # Correctness cross-check (NFA simulation vs DFA simulation)
    print("\n--- Correctness verification ---")
    test_cases_1 = [
        ("ab", True),
        ("aab", True),
        ("bab", True),
        ("ababab", True),
        ("a", False),
        ("b", False),
        ("ba", False),
        ("aba", False),
        ("", False),
    ]
    all_pass = True
    for string, expected in test_cases_1:
        nfa_result = simulate_nfa(nfa1, string)
        dfa_result = simulate_dfa(dfa1, string)
        status = "PASS" if nfa_result == dfa_result == expected else "FAIL"
        if status == "FAIL":
            all_pass = False
        display = repr(string) if string else "'ε'"
        print(
            f"  {status}  input={display:<10} "
            f"expected={str(expected):<6} "
            f"nfa={str(nfa_result):<6} "
            f"dfa={str(dfa_result):<6}"
        )
    print("  All tests passed!" if all_pass else "  *** SOME TESTS FAILED ***")

    # ------------------------------------------------------------------ #
    #  Example 2 : ε-NFA for language  a*  |  b+                          #
    # ------------------------------------------------------------------ #
    print_section("EXAMPLE 2 — ε-NFA accepting  a*  (including ε)  or  b+")

    #  Language: { ε, a, aa, aaa, ... }  ∪  { b, bb, bbb, ... }
    #
    #  Automaton topology:
    #
    #     s --ε--> q0 --a--> q1(*) --a--> q1(*)
    #     s --ε--> q1(*)           <accepts ε via ε direct jump>
    #     s --ε--> r0 --b--> r1(*) --b--> r1(*)
    #
    #  where (*) denotes an accept state.

    nfa2 = NFA(
        states={'s', 'q0', 'q1', 'r0', 'r1'},
        alphabet={'a', 'b'},
        transitions={
            's': {
                EPSILON: {'q0', 'q1', 'r0'},
                #         ^^^   ^^^  ^^^
                #    start a*   ε∈a* start b+
            },
            'q0': {
                'a': {'q1'},
            },
            'q1': {
                'a': {'q1'},   # self-loop for a+
            },
            'r0': {
                'b': {'r1'},
            },
            'r1': {
                'b': {'r1'},   # self-loop for b+
            },
        },
        start_state='s',
        accept_states={'q1', 'r1'},
    )

    print("\n--- Original NFA ---")
    print(nfa2)

    converter2 = NFAtoDFAConverter(nfa2)
    dfa2 = converter2.convert(include_dead_state=True)

    print("\n--- Resulting DFA ---")
    print(dfa2)

    print("\n--- DFA as JSON-serialisable dict (for React frontend) ---")
    print(json.dumps(dfa2.to_serializable(), indent=2))

    # Correctness cross-check
    print("\n--- Correctness verification ---")
    test_cases_2 = [
        ("", True),          # ε ∈ a*
        ("a", True),
        ("aa", True),
        ("aaa", True),
        ("b", True),
        ("bb", True),
        ("bbb", True),
        ("ab", False),       # mixed — not in language
        ("ba", False),
        ("aab", False),
        ("abb", False),
    ]
    all_pass2 = True
    for string, expected in test_cases_2:
        nfa_result = simulate_nfa(nfa2, string)
        dfa_result = simulate_dfa(dfa2, string)
        status = "PASS" if nfa_result == dfa_result == expected else "FAIL"
        if status == "FAIL":
            all_pass2 = False
        display = repr(string) if string else "'ε'"
        print(
            f"  {status}  input={display:<10} "
            f"expected={str(expected):<6} "
            f"nfa={str(nfa_result):<6} "
            f"dfa={str(dfa_result):<6}"
        )
    print("  All tests passed!" if all_pass2 else "  *** SOME TESTS FAILED ***")

    # ------------------------------------------------------------------ #
    #  Example 3 : Minimal NFA — single ε-loop edge case                  #
    # ------------------------------------------------------------------ #
    print_section("EXAMPLE 3 — Stress test: NFA with only ε-transitions and dead states")

    #  NFA accepting only 'b':  q0 --ε--> q1 --b--> q2(accept)
    #  On any other input → dead state.

    nfa3 = NFA(
        states={'q0', 'q1', 'q2'},
        alphabet={'a', 'b'},
        transitions={
            'q0': {EPSILON: {'q1'}},
            'q1': {'b': {'q2'}},
        },
        start_state='q0',
        accept_states={'q2'},
    )

    print("\n--- Original NFA ---")
    print(nfa3)

    converter3 = NFAtoDFAConverter(nfa3)
    dfa3 = converter3.convert(include_dead_state=True)

    print("\n--- Resulting DFA ---")
    print(dfa3)

    print("\n--- DFA as JSON-serialisable dict ---")
    print(json.dumps(dfa3.to_serializable(), indent=2))

    print("\n--- Correctness verification ---")
    test_cases_3 = [
        ("b", True),
        ("a", False),
        ("bb", False),
        ("ab", False),
        ("", False),
    ]
    all_pass3 = True
    for string, expected in test_cases_3:
        nfa_result = simulate_nfa(nfa3, string)
        dfa_result = simulate_dfa(dfa3, string)
        status = "PASS" if nfa_result == dfa_result == expected else "FAIL"
        if status == "FAIL":
            all_pass3 = False
        display = repr(string) if string else "'ε'"
        print(
            f"  {status}  input={display:<10} "
            f"expected={str(expected):<6} "
            f"nfa={str(nfa_result):<6} "
            f"dfa={str(dfa_result):<6}"
        )
    print("  All tests passed!" if all_pass3 else "  *** SOME TESTS FAILED ***")

    print("\n" + "=" * 72)
    print("  All examples completed successfully.")
    print("=" * 72 + "\n")
