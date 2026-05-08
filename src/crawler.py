from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urljoin, urlparse

class Crawler:
    __visited = set() 
    __queue = []

    def __init__(self, url, politeness_delay):
        self.start_url = url
        self.politeness_delay = politeness_delay
        self._base_netloc = urlparse(url).netloc
        self.__pages = {}

    def crawl(self):
        self.__queue.append(self.start_url)

        while len(self.__queue) > 0:
            url = self.__queue.pop(0)
            result = self.__crawl(url)

            if result is not None:
                for link in result["links"]:
                    if link not in self.__visited:
                        self.__queue.append(link)

        return dict(self.__pages)

    def __crawl(self, url):
        if url in self.__visited:
            return None
        print(f"Crawling: {url}")

        self.__visited.add(url)

        if self.politeness_delay:
            time.sleep(self.politeness_delay)

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(" ", strip=True)
        self.__pages[url] = text
        links = []
        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href")
            if not href:
                continue

            # Make the URL absolute and ensure it's within the same domain
            absolute = urljoin(url, href)
            if urlparse(absolute).netloc != self._base_netloc:
                continue

            links.append(absolute)

        return {
            "url": url,
            "text": text,
            "links": links,
        }
    