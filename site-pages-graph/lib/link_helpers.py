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


def is_internal_link(link: str, base_url: str) -> bool:
    base_host = re.sub(r'^www\.', '', urlparse(base_url).netloc, flags=re.I) 
    base_host = re.escape(base_host)
    if re.match(r'https?\:\/\/(?:www\.)?' + base_host, link, flags=re.I):
        return True
    return False


def filter_links(links: list, base_url: str) -> list:
    links = list(set(links))
    filtered_links = []
    for link in links:
        # filter mailto: javascript: and external links
        if is_internal_link(link, base_url):
            filtered_links.append(link)
    return filtered_links