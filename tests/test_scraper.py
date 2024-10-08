import pytest
from http import HTTPStatus

from github_crawler.scraper import GitHubScraper


class TestGitHubScraper:

    @pytest.mark.vcr
    def test_crawl_search_results_issues(self):
        scraper = GitHubScraper(proxies=[
            "4.234.78.115:8080",
        ])

        results = scraper.crawl_search_page(
            search_terms=[
                'openstack',
                'nova',
                'css',
            ],
            search_type=GitHubScraper.SearchType.ISSUES.value,
        )
        assert len(results) == 10
        assert results[0] == {
            "url": "https://github.com/canonical/stsstack-bundles/issues/229"
        }
        assert results[1] == {
            "url": "https://github.com/openstack-exporter/openstack-exporter/issues/395"
        }

    @pytest.mark.vcr
    def test_crawl_search_results_repositories(self):
        scraper = GitHubScraper(proxies=[])

        results = scraper.crawl_search_page(
            search_terms=[
                'wagtail-json-widget',
            ],
            search_type=GitHubScraper.SearchType.REPOSITORIES.value,
        )
        assert len(results) == 2
        assert results[0] == {
            "url": "https://github.com/cursive-works/wagtail-json-widget",
            "extra": {
                "owner": "cursive-works",
                "language_stats": {
                    "Python": 46.4,
                    "JavaScript": 34.8,
                    "CSS": 16.6,
                    "HTML": 2.2,
                }
            }
        }
        assert results[1] == {
            "url": "https://github.com/conda-forge/wagtail-json-widget-feedstock",
            "extra": {
                "owner": "conda-forge",
                "language_stats": {}
            }
        }

    def test_crawl_search_results_invalid_type(self):
        scraper = GitHubScraper(proxies=[])

        with pytest.raises(ValueError) as exc_info:
            scraper.crawl_search_page(
                search_terms=[
                    'django',
                ],
                search_type='invalid',
            )
        assert str(exc_info.value) == 'Unsupported search type: invalid'

    def test_crawl_search_results_response_error(self, requests_mock):
        requests_mock.get(
            'https://github.com/search',
            status_code=HTTPStatus.TOO_MANY_REQUESTS.value,
        )

        scraper = GitHubScraper(proxies=[])

        results = scraper.crawl_search_page(
            search_terms=[
                'django',
            ],
            search_type=GitHubScraper.SearchType.WIKIS.value,
        )
        assert not results
