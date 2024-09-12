import enum
import os
import logging

import random
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests


logger = logging.getLogger(__name__)


class GitHubScraper:
    BASE_URL = 'https://github.com/'

    class SearchType(enum.Enum):
        REPOSITORIES = 'repositories'
        ISSUES = 'issues'
        WIKIS = 'wikis'

        @classmethod
        def is_valid_value(cls, value):
            return value in cls._value2member_map_

    def __init__(self, proxies):
        self.proxies = [f'http://{proxy}' for proxy in proxies]

        self.session = requests.Session()
        self.session.headers.update({
            'Host': 'github.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)'
                ' Version/17.6 Safari/605.1.15'
            ),
        })

        user_session = os.environ.get('GITHUB_USER_SESSION')
        if user_session:
            self.session.cookies.update({
                '__Host-user_session_same_site': user_session,
                'user_session': user_session,
            })

    def crawl_search_page(self, search_terms, search_type):
        if not self.SearchType.is_valid_value(value=search_type):
            raise ValueError(f'Unsupported search type: {search_type}')

        search_query = ' OR '.join(search_terms)
        response = self._get(
            url='search',
            params={
                'q': search_query,
                'type': search_type,
            }
        )
        if not response.ok:
            logger.error('Failed to request github search page (status %s)', response.status_code)
            return []

        results = self._parse_response_data_for_search_results(data=response.text)
        if search_type == self.SearchType.REPOSITORIES.value:
            self._handle_repositories_search_results(results=results)
        else:
            self._handle_common_search_results(results=results)
        return results

    def crawl_repository_page(self, url):
        response = self._get(url)
        if not response.ok:
            logger.error('Failed to request github repository page (status %s)', response.status_code)
            return None

        return self._parse_response_data_for_repository_results(data=response.text)

    @staticmethod
    def _parse_response_data_for_search_results(data):
        soup = BeautifulSoup(data, 'html.parser')
        results = [
            {
                "url": element.get('href'),
            }
            for element in soup.css.select('a:has(.search-match)')
        ]
        return results

    @staticmethod
    def _parse_response_data_for_repository_results(data):
        soup = BeautifulSoup(data, 'html.parser')
        owner_element = (
            soup.css.select_one('span.author')
            or soup.css.select_one('nav[role="navigation"] ul li:first-child a')
        )

        language_stats = {}
        for element in soup.css.select('div.Layout-sidebar li > a.Link--secondary'):
            spans = element.find_all('span')
            try:
                name = spans[0].text
                value = spans[1].text.replace('%', '')
            except IndexError:
                continue
            else:
                try:
                    value = float(value)
                except ValueError:
                    value = None
                language_stats[name] = value

        return {
            'owner': owner_element.text.strip() if owner_element else None,
            'language_stats': language_stats,
        }

    def _handle_repositories_search_results(self, results):
        for result in results:
            url = result['url']
            extra = self.crawl_repository_page(url)
            result.update({
                'extra': extra,
                'url': urljoin(self.BASE_URL, url)
            })

    def _handle_common_search_results(self, results):
        for result in results:
            result['url'] = urljoin(self.BASE_URL, result['url'])

    def _get(self, url, params=None):
        absolute_url = urljoin(self.BASE_URL, url)
        if self.proxies:
            proxy = random.choice(self.proxies)
            proxies = {'http': proxy}
        else:
            proxies = None

        response = self.session.get(absolute_url, params=params, proxies=proxies)
        return response
