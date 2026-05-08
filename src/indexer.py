import re
from collections import defaultdict


class Indexer:
	def __init__(self):
		self._index = defaultdict(dict)

	def build(self, pages):
		"""
		Build a reverse index for a dict of {url: text}.
		The index maps term -> {url: [positions]}.
		"""
		self._index.clear()
		for url, text in pages.items():
			self.add_document(url, text)
		return self.get_index()

	def add_document(self, url, text):
		for position, term in enumerate(self._tokenize(text)):
			urls = self._index[term]
			if url not in urls:
				urls[url] = []
			urls[url].append(position)

	def get_index(self):
		return {term: dict(urls) for term, urls in self._index.items()}

	@staticmethod
	def _tokenize(text):
		# Keep letters and digits, lowercased, as tokens.
		return re.findall(r"[a-z0-9]+", text.lower())
