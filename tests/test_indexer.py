import os
import sys
import unittest

# Allow running tests directly via `python tests/test_indexer.py`.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.indexer import Indexer


class TestIndexer(unittest.TestCase):
	def test_build_index_positions(self):
		pages = {
			"https://example.com/a": "Hello world hello",
		}
		indexer = Indexer()
		index = indexer.build(pages)

		self.assertEqual(index["hello"]["https://example.com/a"], [0, 2])
		self.assertEqual(index["world"]["https://example.com/a"], [1])

	def test_index_multiple_pages(self):
		pages = {
			"https://example.com/a": "Alpha beta",
			"https://example.com/b": "Beta gamma beta",
		}
		indexer = Indexer()
		index = indexer.build(pages)

		self.assertEqual(index["beta"]["https://example.com/a"], [1])
		self.assertEqual(index["beta"]["https://example.com/b"], [0, 2])
		self.assertEqual(index["gamma"]["https://example.com/b"], [1])

	def test_tokenizer_strips_punctuation(self):
		pages = {
			"https://example.com/a": "Hello, world! 42 times.",
		}
		indexer = Indexer()
		index = indexer.build(pages)

		self.assertEqual(index["hello"]["https://example.com/a"], [0])
		self.assertEqual(index["world"]["https://example.com/a"], [1])
		self.assertEqual(index["42"]["https://example.com/a"], [2])
		self.assertEqual(index["times"]["https://example.com/a"], [3])

	def test_build_clears_previous_state(self):
		indexer = Indexer()
		indexer.build({"https://example.com/a": "First doc"})
		index = indexer.build({"https://example.com/b": "Second doc"})

		self.assertNotIn("https://example.com/a", index.get("first", {}))
		self.assertIn("https://example.com/b", index["second"])


if __name__ == "__main__":
	unittest.main()
