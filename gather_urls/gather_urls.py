import hrequests
from urllib.parse import urlparse
import re
from usp.tree import sitemap_tree_for_homepage
from courlan import clean_url, check_url, get_base_url
import logging
import json
import time
import os


def initialize_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def exception_handler(request, exception):
    logging.error(f"Request failed for {request.url}: {exception}")


def is_same_domain(url, domain):
    return urlparse(url).netloc == domain


def valid_link(link):
    if re.search(r"\.(jpg|jpeg|png|gif|bmp|pdf|docx|ppt|xls)$", link, re.IGNORECASE):
        logging.debug(f"Skipping {link} - file type not supported")
        return False
    return True


def clean_and_normalize_url(url):
    try:
        checked_url = check_url(url, strict=True, trailing_slash=False)
        if checked_url:
            return clean_url(checked_url[0])
    except Exception as e:
        logging.error(f"Error cleaning and normalizing URL: {e}")
    return None


def parse_sitemap(homepage_url):
    links = set()
    try:
        tree = sitemap_tree_for_homepage(homepage_url)
        links = {
            clean_and_normalize_url(page.url)
            for page in tree.all_pages()
            if clean_and_normalize_url(page.url)
        }
        logging.info(f"Found {len(links)} links in sitemap from {homepage_url}")
    except Exception as e:
        logging.error(f"Error parsing sitemap from {homepage_url}: {e}")
    return links


def crawl_website(base_url):
    domain = urlparse(base_url).netloc
    visited = set()
    all_links = set()
    to_visit = {clean_and_normalize_url(base_url)}

    while to_visit:
        logging.info(f"Crawling: {len(to_visit)} URLs")
        current_batch = list(to_visit)
        results = hrequests.map(
            [hrequests.async_get(url) for url in current_batch],
            size=20,
            exception_handler=exception_handler,
        )

        new_links = set()
        for resp in results:
            if resp and resp.ok:
                links = {
                    clean_and_normalize_url(link)
                    for link in resp.html.absolute_links
                    if is_same_domain(link, domain) and valid_link(link)
                }
                new_links.update(filter(None, links))

        visited.update(current_batch)
        to_visit = new_links - visited
        all_links.update(new_links)

    logging.info(f"Completed crawling, found {len(all_links)} links")
    return list(all_links)


def export_to_json(url, links):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    sanitized_url = re.sub(r"[^\w\s-]", '', urlparse(url).netloc)  # Sanitize URL to be filename-friendly
    filename = f"{sanitized_url}-{timestamp}.jsonl"

    try:
        with open(filename, 'w') as f:
            for link in links:
                json_line = json.dumps({"url": link})
                f.write(json_line + '\n')
        logging.info(f"Exported URLs to {filename} in JSON Lines format")
        return filename
    except Exception as e:
        logging.error(f"Error exporting to JSON Lines: {e}")
        return None


def gather_urls(url, crawl=False, export=False):
    if not url:
        raise ValueError("A valid URL must be provided.")

    initialize_logging()
    url = get_base_url(url)
    logging.info(f"Gathering URLs using Base URL: {url}")
    
    # Parse sitemap links
    sitemap_links = parse_sitemap(url)

    # If crawl is enabled, crawl the website with the base URL
    crawled_links = []
    if crawl:
        crawled_links = crawl_website(url)

    all_links = sitemap_links.union(crawled_links)

    if export:
        export_to_json(url, list(all_links))

    return list(all_links)


def main():
    import argparse

    initialize_logging()

    parser = argparse.ArgumentParser(
        description="Crawl a website and return all valid URLs."
    )
    parser.add_argument(
        "-u", "--url", required=True, help="The base URL to start gathering or crawling URLs from"
    )
    parser.add_argument(
        "-e", "--export", action="store_true", help="Export the URLs to a JSON file"
    )
    parser.add_argument(
        "-c", "--crawl", action="store_true", help="Enable crawling of the website after sitemap parsing"
    )

    args = parser.parse_args()

    if not args.url:
        raise ValueError("You must provide a URL with the -u or --url argument.")
    
    links = gather_urls(args.url, crawl=args.crawl, export=args.export)

    for link in links:
        print(link)


if __name__ == "__main__":
    main()
