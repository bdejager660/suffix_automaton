import unittest

from suffix_automaton import build
from suffix_automaton.core import SuffixAutomaton


class BuildTests(unittest.TestCase):
    def test_build_returns_automaton(self):
        sa = build("abc")
        self.assertIsInstance(sa, SuffixAutomaton)

    def test_build_rejects_non_string(self):
        with self.assertRaises(TypeError):
            build(b"abc")

    def test_empty_text_has_only_root(self):
        sa = build("")
        self.assertEqual(len(sa), 1)
        self.assertEqual(sa.distinct_substrings(), 0)

    def test_single_character(self):
        sa = build("a")
        self.assertEqual(len(sa), 2)
        self.assertEqual(sa.distinct_substrings(), 1)
        self.assertEqual(sa.count_occurrences("a"), 1)

    def test_repeated_character(self):
        sa = build("aaaa")
        self.assertEqual(sa.distinct_substrings(), 4)
        self.assertEqual(sa.count_occurrences("a"), 4)
        self.assertEqual(sa.count_occurrences("aa"), 3)
        self.assertEqual(sa.count_occurrences("aaa"), 2)
        self.assertEqual(sa.count_occurrences("aaaa"), 1)
        self.assertEqual(sa.count_occurrences("aaaaa"), 0)


class OccurrenceTests(unittest.TestCase):
    def test_banana(self):
        sa = build("banana")
        self.assertEqual(sa.count_occurrences("a"), 3)
        self.assertEqual(sa.count_occurrences("an"), 2)
        self.assertEqual(sa.count_occurrences("ana"), 2)
        self.assertEqual(sa.count_occurrences("banana"), 1)
        self.assertEqual(sa.count_occurrences("bananas"), 0)
        self.assertEqual(sa.count_occurrences("nana"), 1)

    def test_overlapping_occurrences(self):
        sa = build("abababa")
        self.assertEqual(sa.count_occurrences("aba"), 3)
        self.assertEqual(sa.count_occurrences("bab"), 2)
        self.assertEqual(sa.count_occurrences("abab"), 2)

    def test_empty_pattern(self):
        sa = build("abc")
        # The empty string occurs at every position including after the end.
        self.assertEqual(sa.count_occurrences(""), 4)

    def test_empty_pattern_on_empty_text(self):
        sa = build("")
        self.assertEqual(sa.count_occurrences(""), 1)

    def test_missing_substring(self):
        sa = build("abc")
        self.assertEqual(sa.count_occurrences("d"), 0)
        self.assertEqual(sa.count_occurrences("abcd"), 0)

    def test_case_sensitivity(self):
        sa = build("aAb")
        self.assertEqual(sa.count_occurrences("a"), 1)
        self.assertEqual(sa.count_occurrences("A"), 1)
        self.assertEqual(sa.count_occurrences("ab"), 0)


class DistinctSubstringTests(unittest.TestCase):
    def test_abc(self):
        sa = build("abc")
        # "a", "b", "c", "ab", "bc", "abc"
        self.assertEqual(sa.distinct_substrings(), 6)

    def test_banana(self):
        sa = build("banana")
        self.assertEqual(sa.distinct_substrings(), 15)

    def test_all_same_character(self):
        sa = build("zzzz")
        self.assertEqual(sa.distinct_substrings(), 4)

    def test_abab(self):
        sa = build("abab")
        # "a", "b", "ab", "ba", "aba", "bab", "abab"
        self.assertEqual(sa.distinct_substrings(), 7)


class StateCountTests(unittest.TestCase):
    def test_state_count_is_linear(self):
        # For a string of length n the automaton has at most 2n - 1 states
        # (n >= 1).  This is the standard bound and is what makes the
        # structure useful.
        for text in ("a", "ab", "abc", "banana", "ababab", "mississippi"):
            sa = build(text)
            self.assertLessEqual(len(sa), max(1, 2 * len(text)))

    def test_state_count_matches_known_values(self):
        self.assertEqual(len(build("a")), 2)
        self.assertEqual(len(build("ab")), 3)
        self.assertEqual(len(build("aa")), 3)
        self.assertEqual(len(build("abab")), 5)


if __name__ == "__main__":
    unittest.main()
