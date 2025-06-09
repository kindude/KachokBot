import random
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin


class Parser:
    def __init__(self):
        self.base_url = "https://eleatnutrition.com/blog/"

    def parse_all(self):
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, "lxml")

        articles = soup.find_all("article")
        clean_base_url = self.base_url.replace("/blog/", "/")

        results = []
        for article in articles:
            a_tag = article.find("a")
            title = article.find("h1").text.strip()
            if a_tag and "href" in a_tag.attrs:
                url = urljoin(clean_base_url, a_tag["href"])
                results.append((title, url))

        return results
