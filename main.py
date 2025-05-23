from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright
import requests
import html2text
import os

def visit_url_using_browser(url: str)->str:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        html_content = page.content()
        browser.close()
    return html_content

def visit_url_simple(url: str)->str:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.text

def parse_urls(html_body: str)->List[str]:
    soup = BeautifulSoup(html_body, 'html.parser')
    urls = []
    for link in soup.find_all('a', href=True):
        urls.append(link['href'])
    return list(set(urls))

def filter_urls(urls: List[str], base_url: str)-> List[str]:
    parsed_base_url = urlparse(base_url)
    base_domain_path = f"{parsed_base_url.scheme}://{parsed_base_url.netloc}{parsed_base_url.path}"
    filtered = []
    for url in urls:
        full_url = urljoin(base_url, url)
        if full_url.startswith(base_domain_path):
            filtered.append(full_url)
    return filtered

def html_to_md(html_body: str)-> str:
    h = html2text.HTML2Text()
    h.ignore_links = False
    return h.handle(html_body)

def write_file(text: str, path: str):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "w") as f:
        f.write(text)

def get_file_name_from_url(url: str, base_url:str)-> str:
    parsed_url = urlparse(url)
    parsed_base_url = urlparse(base_url)
    # Get the path relative to the base URL's path
    relative_path = os.path.relpath(parsed_url.path, parsed_base_url.path)
    # Split the path components and take the last two
    path_components = relative_path.split('/')
    if len(path_components) >= 2:
        file_name = '/'.join(path_components[-2:])
    else:
        file_name = path_components[-1] if path_components else ""

    # Append .md if it's not already there and not an empty string
    if file_name and not file_name.endswith(".md"):
        file_name += ".md"
    elif not file_name:
        file_name = "index.md" # Handle the case where the relative path is empty

    return file_name


def main():
    start_url = "https://docs.trychroma.com/docs/overview/introduction"
    base_url = "https://docs.trychroma.com/docs"
    html_body = visit_url_using_browser(start_url)
    next_urls = filter_urls(parse_urls(html_body), base_url)
    print(next_urls)
    md_body = html_to_md(html_body)
    file_name = get_file_name_from_url(start_url, base_url)
    write_file(md_body, f"data/{file_name}")
    print(md_body)


if __name__ == "__main__":
    main()
