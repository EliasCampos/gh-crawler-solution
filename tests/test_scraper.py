import pytest

from scraper import GitHubScraper


class TestGitHubScraper:

    @pytest.mark.vcr
    def test_crawl_search_results_issues(self):
        scraper = GitHubScraper(proxies=[
            "148.72.140.24:30127",
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
            "url": "https://github.com/ferdiunal/nova-settings/issues/3"
        }
        assert results[1] == {
            "url": "https://github.com/canonical/stsstack-bundles/issues/229"
        }

    @pytest.mark.vcr
    def test_crawl_search_results_repositories(self):
        scraper = GitHubScraper(proxies=[
            "148.72.140.24:30127",
        ])

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
