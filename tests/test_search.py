import os
import sys
import unittest

# Allow running tests directly via `python tests/test_search.py`.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.indexer import Indexer
from src.search import Searcher


class TestSearcher(unittest.TestCase):
	def _build_searcher(self, pages, **kwargs):
		indexer = Indexer()
		index = indexer.build(pages)
		return Searcher(index, **kwargs)

	def test_empty_query_returns_empty(self):
		pages = {"https://example.com/a": "Alpha beta"}
		searcher = self._build_searcher(pages)

		self.assertEqual(searcher.search("   "), [])

	def test_unknown_term_returns_empty(self):
		pages = {"https://example.com/a": "Alpha beta"}
		searcher = self._build_searcher(pages)

		self.assertEqual(searcher.search("gamma"), [])

	def test_ranks_by_term_frequency(self):
		pages = {
			"https://example.com/a": "Alpha alpha beta",
			"https://example.com/b": "Alpha beta",
		}
		searcher = self._build_searcher(pages)

		self.assertEqual(
			searcher.search("alpha", top_k=2),
			["https://example.com/a", "https://example.com/b"],
		)

	def test_phrase_boost_prefers_ordered_match(self):
		pages = {
			"https://example.com/a": "Hello world",
			"https://example.com/b": "World hello",
		}
		searcher = self._build_searcher(pages, phrase_boost=2.0)

		self.assertEqual(
			searcher.search("hello world", top_k=2),
			["https://example.com/a", "https://example.com/b"],
		)


if __name__ == "__main__":
	unittest.main()
