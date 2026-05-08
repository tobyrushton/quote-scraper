import math
import re


class Searcher:
	def __init__(self, index, k1=1.5, b=0.75, phrase_boost=1.0):
		self._index = index or {}
		self._k1 = k1
		self._b = b
		self._phrase_boost = phrase_boost
		self._doc_lengths = self._build_doc_lengths()
		self._doc_count = len(self._doc_lengths)
		self._avgdl = (
			sum(self._doc_lengths.values()) / self._doc_count
			if self._doc_count
			else 0.0
		)

	def search(self, query, top_k=10):
		tokens = self._tokenize(query)
		if not tokens or not self._index:
			return []

		postings = {
			term: self._sorted_postings(term)
			for term in tokens
			if term in self._index
		}
		if not postings:
			return []

		pointers = {term: 0 for term in postings}
		scores = {}

		while True:
			current_urls = []
			for term, term_postings in postings.items():
				ptr = pointers[term]
				if ptr < len(term_postings):
					current_urls.append(term_postings[ptr][0])
			if not current_urls:
				break

			current_url = min(current_urls)
			doc_len = self._doc_lengths.get(current_url, 0)
			score = 0.0

			for term, term_postings in postings.items():
				ptr = pointers[term]
				if ptr < len(term_postings) and term_postings[ptr][0] == current_url:
					positions = term_postings[ptr][1]
					tf = len(positions)
					df = len(self._index.get(term, {}))
					score += self._bm25(tf, df, doc_len)
					pointers[term] += 1

			if len(tokens) > 1 and self._has_phrase(tokens, current_url):
				score += self._phrase_boost

			scores[current_url] = score

		results = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
		return [url for url, _ in results[:top_k]]

	def _sorted_postings(self, term):
		urls = self._index.get(term, {})
		return sorted(urls.items(), key=lambda item: item[0])

	def _bm25(self, tf, df, doc_len):
		if self._doc_count == 0 or df == 0:
			return 0.0
		idf = math.log((self._doc_count - df + 0.5) / (df + 0.5) + 1.0)
		denominator = tf + self._k1 * (1 - self._b + self._b * doc_len / self._avgdl)
		return idf * (tf * (self._k1 + 1)) / (denominator if denominator else 1.0)

	def _has_phrase(self, tokens, url):
		positions_lists = []
		for term in tokens:
			url_positions = self._index.get(term, {}).get(url)
			if not url_positions:
				return False
			positions_lists.append(url_positions)

		candidates = set(positions_lists[0])
		for offset, positions in enumerate(positions_lists[1:], start=1):
			shifted = {pos - offset for pos in positions}
			candidates &= shifted
			if not candidates:
				return False
		return True

	def _build_doc_lengths(self):
		doc_lengths = {}
		for _, url_map in self._index.items():
			for url, positions in url_map.items():
				doc_lengths[url] = doc_lengths.get(url, 0) + len(positions)
		return doc_lengths

	@staticmethod
	def _tokenize(text):
		return re.findall(r"[a-z0-9]+", text.lower())
