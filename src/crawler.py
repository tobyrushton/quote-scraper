from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urljoin

class Crawler:
    __visited = set() 
    __queue = []

    def __init__(self, url, politeness_delay):
        self.start_url = url
        self.politeness_delay = politeness_delay

    def crawl(self):
       self.__qeueue.append(self.start_url) 
       
       while len(self.__queue) > 0:
           url = self.__qeueue.pop(0)
           result = self.__crawl(url)

           if result is not None:
               for link in result["links"]:
                   if link not in self.__visited:
                       self.__qeueue.append(link)

    def __crawl(self, url):
        if url in self.__visited:
            return None

        self.__visited.add(url)

        if self.politeness_delay:
            time.sleep(self.politeness_delay)

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(" ", strip=True)
        links = []
        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href")
            if not href:
                continue

            links.append(urljoin(url, href))

        return {
            "url": url,
            "text": text,
            "links": links,
        }
    