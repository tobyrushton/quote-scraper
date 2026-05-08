# Quotes Scraper

This projects demonstrates a basic web crawler, indexer and search engine. It crawls https://quotes.toscrape.com/, and allows for multi term lookup.

## Setup

To set the project up, the following steps should be followed:
- Clone this repository.
- Install the requirements.txt

## Usage

Start the interactive CLI:

```bash
python src/main.py
```

Then enter one of the commands below.

### build

Builds the inverted index from the seed URL.

```text
build
```

### load

Loads the index from disk into memory for searching.

```text
load
```

### search

Searches the loaded index for a query.

```text
search life
```

```text
search love and wisdom
```

### print

Prints the postings list for a single word.

```text
print truth
```

## Testing 

Run the testing suite:
```bash
python tests/run_tests.py
```