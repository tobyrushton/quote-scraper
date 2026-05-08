import math
import re


class Searcher:
	"""BM25-based search over a positional inverted index."""
	def __init__(self, index, k1=1.5, b=0.75, phrase_boost=1.0):
		self._index = index or {}
		self._k1 = k1
		self._b = b
		self._phrase_boost = phrase_boost
		# Precompute document lengths and corpus stats for BM25 scoring.
		self._doc_lengths = self._build_doc_lengths()
		self._doc_count = len(self._doc_lengths)
		self._avgdl = (
			sum(self._doc_lengths.values()) / self._doc_count
			if self._doc_count
			else 0.0
		)

	def search(self, query, top_k=10):
		# Tokenize the query into normalized terms.
		tokens = self._tokenize(query)
		# Short-circuit on empty queries or empty index.
		if not tokens or not self._index:
			return []

		# Gather postings lists only for terms that exist in the index.
		postings = {
			term: self._sorted_postings(term)
			for term in tokens
			if term in self._index
		}
		# If none of the query terms appear, return no results.
		if not postings:
			return []

		# Merge postings by URL using per-term pointers (multi-way merge).
		pointers = {term: 0 for term in postings}
		scores = {}

		while True:
			# Identify the next URL among the current postings heads.
			current_urls = []
			for term, term_postings in postings.items():
				ptr = pointers[term]
				if ptr < len(term_postings):
					current_urls.append(term_postings[ptr][0])
			if not current_urls:
				break

			# Score the lexicographically smallest URL to keep merge stable.
			current_url = min(current_urls)
			doc_len = self._doc_lengths.get(current_url, 0)
			score = 0.0

			for term, term_postings in postings.items():
				ptr = pointers[term]
				if ptr < len(term_postings) and term_postings[ptr][0] == current_url:
					positions = term_postings[ptr][1]
					# Term frequency is the number of positions for this term in the doc.
					tf = len(positions)
					# Document frequency is number of docs containing the term.
					df = len(self._index.get(term, {}))
					score += self._bm25(tf, df, doc_len)
					# Advance pointer for this term once current_url is consumed.
					pointers[term] += 1

			# Boost documents that contain the full query as a phrase.
			if len(tokens) > 1 and self._has_phrase(tokens, current_url):
				score += self._phrase_boost

			# Store the final score for this URL.
			scores[current_url] = score

		# Sort by score (desc) then URL (asc) to keep results deterministic.
		results = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
		return [url for url, _ in results[:top_k]]

	def _sorted_postings(self, term):
		# Each postings list item is (url, [positions]).
		urls = self._index.get(term, {})
		return sorted(urls.items(), key=lambda item: item[0])

	def _bm25(self, tf, df, doc_len):
		# BM25 with length normalization; uses corpus-level avg document length.
		if self._doc_count == 0 or df == 0:
			return 0.0
		idf = math.log((self._doc_count - df + 0.5) / (df + 0.5) + 1.0)
		denominator = tf + self._k1 * (1 - self._b + self._b * doc_len / self._avgdl)
		return idf * (tf * (self._k1 + 1)) / (denominator if denominator else 1.0)

	def _has_phrase(self, tokens, url):
		# Phrase match: look for aligned positions across all terms.
		positions_lists = []
		for term in tokens:
			url_positions = self._index.get(term, {}).get(url)
			if not url_positions:
				return False
			positions_lists.append(url_positions)

		# Start with positions of the first term, then intersect shifted positions.
		candidates = set(positions_lists[0])
		for offset, positions in enumerate(positions_lists[1:], start=1):
			shifted = {pos - offset for pos in positions}
			candidates &= shifted
			if not candidates:
				return False
		return True

	def _build_doc_lengths(self):
		# Sum per-document term counts by aggregating positions lists.
		doc_lengths = {}
		for _, url_map in self._index.items():
			for url, positions in url_map.items():
				doc_lengths[url] = doc_lengths.get(url, 0) + len(positions)
		return doc_lengths

	@staticmethod
	def _tokenize(text):
		# Normalize to lowercase alphanumeric tokens.
		return re.findall(r"[a-z0-9]+", text.lower())
