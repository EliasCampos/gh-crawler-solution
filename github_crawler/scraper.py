from concurrent.futures import ThreadPoolExecutor
import enum
import os
import logging

import random
from operator import itemgetter
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import certifi
import requests


logger = logging.getLogger(__name__)


class GitHubScraper:
    BASE_URL = 'https://github.com/'
    REPOSITORIES_CRAWLING_WORKERS_NUMBER = 10  # corresponding to the number of search search_results on a page

    class SearchType(enum.Enum):
        REPOSITORIES = 'repositories'
        ISSUES = 'issues'
        WIKIS = 'wikis'

        @classmethod
        def is_valid_value(cls, value):
            return value in cls._value2member_map_

    def __init__(self, proxies):
        self.proxies = proxies

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

        self._set_random_proxy()

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
            results = self._handle_repositories_search_results(search_results=results)
        else:
            results = self._handle_common_search_results(search_results=results)
        return results

    def fetch_repository_page(self, url):
        response = self._get(url)
        if not response.ok:
            logger.error('Failed to request github repository page (status %s)', response.status_code)
            return None

        return response.text

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

    def _handle_repositories_search_results(self, search_results):
        repository_urls = list(map(itemgetter('url'), search_results))

        with ThreadPoolExecutor(max_workers=self.REPOSITORIES_CRAWLING_WORKERS_NUMBER) as executor:
            repository_pages = executor.map(self.fetch_repository_page, repository_urls)

        results = []
        for url, repository_page in zip(repository_urls, repository_pages):
            if repository_page:
                extra = self._parse_response_data_for_repository_results(data=repository_page)
            else:
                extra = None

            results.append({
                'url': urljoin(self.BASE_URL, url),
                'extra': extra,
            })

        return results

    def _handle_common_search_results(self, search_results):
        return [
            {'url': urljoin(self.BASE_URL, search_result['url'])}
            for search_result in search_results
        ]

    def _get(self, url, params=None):
        absolute_url = urljoin(self.BASE_URL, url)

        response = self.session.get(absolute_url, params=params, verify=certifi.where())
        return response

    def _set_random_proxy(self):
        if self.proxies:
            proxy = random.choice(self.proxies)
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}',
            }
            self.session.proxies.update(proxies)
