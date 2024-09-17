import argparse
import json
import pathlib
import sys

from github_crawler.scraper import GitHubScraper


def run_github_search_crawler(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=pathlib.Path)

    arguments = parser.parse_args(args)

    with open(arguments.config) as f:
        config = json.load(f)

    keywords = config['keywords']
    search_type = config['type'].lower()
    proxies = config.get('proxies')

    scraper = GitHubScraper(proxies=proxies)
    return scraper.crawl_search_page(search_terms=keywords, search_type=search_type)


def run_github_search_crawler_from_command_line():
    crawl_results = run_github_search_crawler()
    json.dump(crawl_results, sys.stdout, indent=4)
