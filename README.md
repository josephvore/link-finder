# Gather URLs

A Python tool to crawl websites and gather all valid URLs.

## Installation

You can install the package after building or from PyPI:

```bash
pip install link-finder
```

## Usage

Once installed, you can use it from the command line as follows:

```bash
gather_urls -u https://example.com
```

This will crawl the website starting from the provided URL and return all valid URLs it finds, including those from the sitemap (if available).

## Features

- Crawls a website starting from the base URL.
- Parses sitemaps for additional URLs.
- Filters out invalid or unsupported file types (e.g., images, PDFs).

## Dependencies

The following packages are required and will be installed automatically:

- hrequests
- usp
- courlan