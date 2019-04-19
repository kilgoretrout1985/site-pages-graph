import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import url


def find_links(html: str) -> list:
    soup = BeautifulSoup(html, "html5lib")
    links = []
    for link in soup.findAll('a'):
        href = link.get('href')
        if href:
            links.append(href)
    return links


def normalize_links(links: list, base_url: str) -> list:
    normalized_links = []
    for link in links:
        # relative links to absolute
        if not re.match(r'https?\:\/\/', link, flags=re.I):
            try:
                link = url.parse(base_url).relative(link)
            except ValueError:
                continue
        # normalize link and remove #anchor
        try:
            link = str(url.parse(link).defrag().abspath())
        except ValueError:
            continue
        normalized_links.append(link)
    return normalized_links


def filter_links(links: list, base_url: str) -> list:
    base_host = re.sub(r'^www\.', '', urlparse(base_url).netloc, flags=re.I) 
    base_host = re.escape(base_host)
    
    links = list(set(links))
    filtered_links = []
    for link in links:
        # filter mailto: javascript: and external links
        if re.match(r'https?\:\/\/(?:www\.)?' + base_host, link, flags=re.I):
            filtered_links.append(link)
    return filtered_links
