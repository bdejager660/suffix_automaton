# suffix_automaton

Build a deterministic suffix automaton from a string and answer substring
occurrence and distinct-substring queries in linear space.

```python
from suffix_automaton import build

sa = build("banana")
print(sa.count_occurrences("ana"))   # 2
print(sa.count_occurrences("xyz"))   # 0
print(sa.distinct_substrings())      # 15
print(len(sa))                       # number of states
```

## Why this exists

Counting how many times a pattern occurs in a text, and counting how many
distinct substrings the text has, are both easy to do naively in O(n^2) or
worse.  A suffix automaton answers both in time proportional to the pattern
length (for occurrences) or in time proportional to the number of states (for
distinct substrings), using O(n) states and transitions.  The trade-off is
construction cost: building the automaton is O(n) but with a larger constant
than a suffix array, and the structure stores one dictionary per state.  For
short-lived queries over one string it is a good fit; for a corpus of many
strings a suffix tree or suffix array may be preferable.

The implementation keeps all state data in parallel lists inside a single
`SuffixAutomaton` object.  This avoids allocating a Python object per state and
makes the whole structure cheap to iterate over in tests.

## API

- `build(text: str) -> SuffixAutomaton` — construct the automaton.  Raises
  `TypeError` if `text` is not a `str`.
- `SuffixAutomaton.count_occurrences(pattern: str) -> int` — number of
  (possibly overlapping) occurrences of `pattern`.  An empty pattern occurs
  `len(text) + 1` times, once at every position including the end.  A pattern
  that is not a substring returns `0`.
- `SuffixAutomaton.distinct_substrings() -> int` — number of distinct
  non-empty substrings of the text.
- `len(sa)` — number of states in the automaton, including the root.

## The awkward edge

Occurrence counts are computed once at construction time by propagating counts
along suffix links in decreasing order of state length.  This means the count
for a state is the number of end positions of its longest string, and therefore
the count returned for a pattern is the number of occurrences of that exact
pattern.  If you need counts for a different text, build a new automaton;
there is no mutation API.  Also note that the empty pattern is special-cased to
`len(text) + 1` rather than `0`, because the empty string occurs at every
boundary of the text.
