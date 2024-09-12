import os
import logging

import random
from urllib.parse import urljoin, quote_plus

from bs4 import BeautifulSoup
import requests


logger = logging.getLogger(__name__)


class GitHubScraper:
    BASE_URL = 'https://github.com/'

    def __init__(self, proxies):
        self.proxies = [
            f'http://{proxy}'
            for proxy in proxies
        ]

        self.session = requests.Session()
        self.session.headers.update({
            'Host': 'github.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15',
        })

        user_session = os.environ.get('GITHUB_USER_SESSION')
        if user_session:
            self.session.cookies.update({
                '__Host-user_session_same_site': user_session,
                'user_session': user_session,
            })

    def crawl_search_results(self, search_terms):
        search_query = ' OR '.join(search_terms)
        response = self._get(
            url='search',
            params={
                'q': search_query,
                'type': 'repositories',
            }
        )
        if not response.ok:
            logger.error('Failed to request github search page (status %s)', response.status_code)
            return []

        return self._parse_response_data_for_search_results(data=response.text)

    def _parse_response_data_for_search_results(self, data):
        soup = BeautifulSoup(data, 'html.parser')
        results = [
            {
                "url": urljoin(self.BASE_URL, element.get('href')),
            }
            for element in soup.css.select('a:has(.search-match)')
        ]
        return results

    def _get(self, url, params):
        absolute_url = urljoin(self.BASE_URL, url)
        if self.proxies:
            proxy = random.choice(self.proxies)
            proxies = {'http': proxy}
        else:
            proxies = None

        response = self.session.get(absolute_url, params=params, proxies=proxies)
        return response


def main():
    result = GitHubScraper(proxies=[]).crawl_search_results(search_terms=['openstack', 'css'])
    print(result)


if __name__ == '__main__':
    main()
