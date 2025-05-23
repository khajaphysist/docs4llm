from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright, Browser
import requests
import html2text
import os
from markdownify import markdownify as md
from collections import deque
import argparse

def visit_url_using_browser(url: str, browser: Browser)->str:
    page = browser.new_page()
    page.goto(url)
    html_content = page.inner_html('body')
    page.close()
    return html_content

def visit_url_simple(url: str)->str:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.text

def parse_urls(html_body: str)->List[str]:
    soup = BeautifulSoup(html_body, 'html.parser')
    urls = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        parsed_href = urlparse(href)
        # Reconstruct the URL with only scheme, netloc, and path
        clean_url = parsed_href._replace(fragment="", query="").geturl()
        urls.append(clean_url)
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

def html_to_md_html2text(html_body: str)-> str:
    h = html2text.HTML2Text()
    h.ignore_links = False
    return h.handle(html_body)

def html_to_md_markdownify(html_body:str)->str:
    return md(html_body)

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

def crawl_all_urls_and_save_to_md(start_url: str, base_url: str, data_dir: str, max_pages: int = None):
    visited_urls = set()
    urls_to_visit = deque([start_url])
    pages_visited_count = 0

    with sync_playwright() as p:
        browser = p.chromium.launch()

        while urls_to_visit:
            if max_pages is not None and pages_visited_count >= max_pages:
                print(f"Max pages ({max_pages}) reached. Stopping crawl.")
                break

            current_url = urls_to_visit.popleft()

            if current_url in visited_urls:
                continue

            print(f"Visiting: {current_url}")
            visited_urls.add(current_url)
            pages_visited_count += 1

            try:
                html_body = visit_url_using_browser(current_url, browser)
                md_body = html_to_md_markdownify(html_body)
                file_name = get_file_name_from_url(current_url, base_url)
                write_file(md_body, os.path.join(data_dir, file_name))
                print(f"Saved: {os.path.join(data_dir, file_name)}")

                next_urls = filter_urls(parse_urls(html_body), base_url)
                for next_url in next_urls:
                    if next_url not in visited_urls:
                        urls_to_visit.append(next_url)

            except Exception as e:
                print(f"Error visiting {current_url}: {e}")

        browser.close()

def create_a_singe_md(data_dir: str, output_file_path: str):
    with open(output_file_path, "w") as outfile:
        for root, _, files in os.walk(data_dir):
            for file in files:
                if file.endswith(".md") and file != os.path.basename(output_file_path):
                    filepath = os.path.join(root, file)
                    # Add a header to indicate the original file path
                    relative_filepath = os.path.relpath(filepath, data_dir)
                    outfile.write(f"# File: {relative_filepath}\n\n")
                    with open(filepath, "r") as infile:
                        outfile.write(infile.read())
                    outfile.write("\n\n---\n\n") # Separator between files

def main():
    parser = argparse.ArgumentParser(description="Crawl a website and save content as markdown.")
    parser.add_argument("start_url", help="The starting URL for the crawl.")
    parser.add_argument("base_url", help="The base URL to filter links.")
    parser.add_argument("output_file_path", help="The path to the output markdown file.")
    parser.add_argument("--max-pages", type=int, help="Maximum number of pages to visit.")
    args = parser.parse_args()

    data_directory = "data"
    crawl_all_urls_and_save_to_md(args.start_url, args.base_url, data_directory, args.max_pages)
    create_a_singe_md(data_directory, args.output_file_path)


if __name__ == "__main__":
    main()
