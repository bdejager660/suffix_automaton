"""Deterministic suffix automaton in O(n) states and O(n) transitions.

The automaton is built incrementally in the standard way: every prefix of the
text corresponds to a state, and the transitions spell out substrings.  This
module deliberately keeps the state representation flat (parallel lists) so
that construction does not allocate one dict per state and so that the whole
structure can be inspected cheaply in tests.

Occurrence counting uses the classic `cnt` propagation: each non-clone state
starts with cnt = 1 (it was created by extending a prefix), clones start at 0,
and then states are visited in decreasing order of `length` while pushing their
count into the link target.  After that pass, `cnt[v]` is the number of times
the longest string of state `v` occurs in the text.
"""

from __future__ import annotations

from typing import Dict, List


class SuffixAutomaton:
    """A suffix automaton over a single immutable string.

    Instances are built by :func:`build` and should not be constructed directly.
    """

    __slots__ = ("text", "next", "link", "length", "cnt", "_finalized")

    def __init__(self, text: str) -> None:
        self.text = text
        # `next[i]` maps a character to the index of the target state.
        self.next: List[Dict[str, int]] = [{}]
        # link[i] is the suffix link of state i; the root (state 0) links to -1.
        self.link: List[int] = [-1]
        # length[i] is the length of the longest string in state i.
        self.length: List[int] = [0]
        # cnt[i] is the number of end positions of the longest string of state i.
        # It is only meaningful after `_finalize` has run.
        self.cnt: List[int] = [0]
        self._finalized = False

        last = 0
        for ch in text:
            last = self._extend(last, ch)
        self._finalize()

    # -- construction -----------------------------------------------------

    def _extend(self, last: int, ch: str) -> int:
        """Add `ch` to the automaton, returning the new `last` state."""
        cur = len(self.next)
        self.next.append({})
        self.link.append(-1)
        self.length.append(self.length[last] + 1)
        self.cnt.append(1)

        p = last
        while p != -1 and ch not in self.next[p]:
            self.next[p][ch] = cur
            p = self.link[p]

        if p == -1:
            self.link[cur] = 0
            return cur

        q = self.next[p][ch]
        if self.length[p] + 1 == self.length[q]:
            self.link[cur] = q
            return cur

        # Clone q: the clone represents the shorter strings that are now shared.
        clone = len(self.next)
        self.next.append(dict(self.next[q]))
        self.link.append(self.link[q])
        self.length.append(self.length[p] + 1)
        self.cnt.append(0)  # a clone is not an end position of any prefix

        while p != -1 and self.next[p].get(ch) == q:
            self.next[p][ch] = clone
            p = self.link[p]

        self.link[q] = clone
        self.link[cur] = clone
        return cur

    def _finalize(self) -> None:
        """Propagate occurrence counts from longer states to their links."""
        if self._finalized:
            return
        order = sorted(range(len(self.next)), key=lambda i: self.length[i], reverse=True)
        for v in order:
            parent = self.link[v]
            if parent >= 0:
                self.cnt[parent] += self.cnt[v]
        self._finalized = True

    # -- queries ----------------------------------------------------------

    def count_occurrences(self, pattern: str) -> int:
        """Return the number of (possibly overlapping) occurrences of `pattern`.

        An empty pattern occurs `len(text) + 1` times, matching the usual
        definition of the empty substring occurring at every position including
        the end.  A pattern that is not a substring returns 0.
        """
        if not pattern:
            return len(self.text) + 1
        state = 0
        for ch in pattern:
            nxt = self.next[state].get(ch)
            if nxt is None:
                return 0
            state = nxt
        return self.cnt[state]

    def distinct_substrings(self) -> int:
        """Return the number of distinct non-empty substrings of the text.

        Each state contributes `length[v] - length[link[v]]` new substrings.
        """
        total = 0
        for v in range(1, len(self.next)):
            total += self.length[v] - self.length[self.link[v]]
        return total

    def __len__(self) -> int:
        """Number of states in the automaton, including the root."""
        return len(self.next)


def build(text: str) -> SuffixAutomaton:
    """Build a suffix automaton for `text`.

    The input is treated as an immutable sequence of characters; no
    normalisation is performed, so `"A"` and `"a"` are distinct.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    return SuffixAutomaton(text)
