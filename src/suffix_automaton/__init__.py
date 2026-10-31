"""Suffix automaton construction and queries.

Public API:
    build(text) -> SuffixAutomaton
    SuffixAutomaton.count_occurrences(pattern) -> int
    SuffixAutomaton.distinct_substrings() -> int
"""

from .core import SuffixAutomaton, build

__all__ = ["SuffixAutomaton", "build"]
