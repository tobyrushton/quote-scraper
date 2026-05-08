import json
from crawler import Crawler
from indexer import Indexer
from search import Searcher

def build(url):
    crawler = Crawler(url, 6)
    pages = crawler.crawl()

    indexer = Indexer()
    index = indexer.build(pages)

    with open("./data/index.json", "w") as f:
        json.dump(index, f)
    
    print(f"Indexed {len(pages)} pages.")

def load_index():
    try:
        with open("./data/index.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Index file not found. Please run 'build' command first.")
        return {}

def search(index, query):
    searcher = Searcher(index)
    results = searcher.search(query, top_k=10)

    if not results:
        print("No results found.")
        return

    print("Top results:")
    for url in results:
        print(f"- {url}")

def print_index(word):
    index = load_index()
    if word in index:
        print(f"Pages containing '{word}':")
        for url, positions in index[word].items():
            print(f"- {url} (positions: {positions})")
    else:
        print(f"No pages contain the word '{word}'.")

if __name__ == "__main__":
   seed_url = "https://quotes.toscrape.com/" 
    # In-memory index is loaded explicitly via the `load` command.
   index = {}
   
   while True:
        # Commands are space-delimited; `search` consumes the rest of the line.
      command = input("").split()

      match command[0]:
        case "build":
            build(seed_url)
        case "load":
            # Refresh the in-memory index from disk.
            index = load_index()
        case "search":
            if not index:
                print("No index loaded. Please run 'load' command first.")
                continue
            query = " ".join(command[1:])
            search(index, query)
        case "print":
            if len(command) < 2:
                print("Please provide a word to print.")
                continue
            print_index(command[1])
        case _:
            print("Unknown command.")
