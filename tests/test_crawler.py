import os
import sys
import unittest
from unittest.mock import patch

# Allow running tests directly via `python tests/test_crawler.py`.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.crawler import Crawler


class FakeResponse:
	def __init__(self, text, status_code=200):
		self.text = text
		self.status_code = status_code

	def raise_for_status(self):
		if self.status_code >= 400:
			raise RuntimeError(f"HTTP {self.status_code}")


def _reset_crawler_state():
	# Reset class-level state between tests.
	Crawler._Crawler__visited = set()
	Crawler._Crawler__queue = []


class TestCrawler(unittest.TestCase):
	def test_crawl_extracts_text_and_links(self):
		_reset_crawler_state()
		html = """
		<html>
		  <head><title>Example</title></head>
		  <body>
			<p>Hello <b>world</b>!</p>
			<a href="/relative">Relative</a>
			<a href="https://example.com/abs">Absolute</a>
			<a>Missing href</a>
		  </body>
		</html>
		"""

		with patch("src.crawler.requests.get") as mock_get:
			mock_get.return_value = FakeResponse(html)
			crawler = Crawler("https://example.com/base", politeness_delay=0)
			result = crawler._Crawler__crawl("https://example.com/base")

		self.assertEqual(result["url"], "https://example.com/base")
		self.assertIn("Hello world", result["text"])
		self.assertIn("Example", result["text"])
		self.assertEqual(
			result["links"],
			[
				"https://example.com/relative",
				"https://example.com/abs",
			],
		)

	def test_crawl_skips_visited_urls(self):
		_reset_crawler_state()
		html = "<html><body><p>Once</p></body></html>"

		with patch("src.crawler.requests.get") as mock_get:
			mock_get.return_value = FakeResponse(html)
			crawler = Crawler("https://example.com", politeness_delay=0)
			first = crawler._Crawler__crawl("https://example.com")
			second = crawler._Crawler__crawl("https://example.com")

		self.assertIsNotNone(first)
		self.assertIsNone(second)
		self.assertEqual(mock_get.call_count, 1)

	def test_crawl_respects_politeness_delay(self):
		_reset_crawler_state()
		html = "<html><body><p>Delayed</p></body></html>"

		with patch("src.crawler.requests.get") as mock_get, patch(
			"src.crawler.time.sleep"
		) as mock_sleep:
			mock_get.return_value = FakeResponse(html)
			crawler = Crawler("https://example.com", politeness_delay=0.25)
			crawler._Crawler__crawl("https://example.com")

		mock_sleep.assert_called_once_with(0.25)

	def test_crawl_multiple_pages_with_link_graph(self):
		_reset_crawler_state()
		pages = {
			"https://example.com/a": """
			<html>
			  <body>
				<p>Page A</p>
				<a href="/b">To B</a>
				<a href="/c">To C</a>
			  </body>
			</html>
			""",
			"https://example.com/b": """
			<html>
			  <body>
				<p>Page B</p>
				<a href="/c">To C</a>
			  </body>
			</html>
			""",
			"https://example.com/c": """
			<html>
			  <body>
				<p>Page C</p>
			  </body>
			</html>
			""",
		}

		def fake_get(url, timeout=10):
			return FakeResponse(pages[url])

		with patch("src.crawler.requests.get", side_effect=fake_get) as mock_get:
			crawler = Crawler("https://example.com/a", politeness_delay=0)
			result_a = crawler._Crawler__crawl("https://example.com/a")
			result_b = crawler._Crawler__crawl("https://example.com/b")
			result_c = crawler._Crawler__crawl("https://example.com/c")

		self.assertIn("Page A", result_a["text"])
		self.assertIn("Page B", result_b["text"])
		self.assertIn("Page C", result_c["text"])
		self.assertEqual(
			result_a["links"],
			[
				"https://example.com/b",
				"https://example.com/c",
			],
		)
		self.assertEqual(result_b["links"], ["https://example.com/c"])
		self.assertEqual(result_c["links"], [])
		self.assertEqual(mock_get.call_count, 3)


if __name__ == "__main__":
	unittest.main()
