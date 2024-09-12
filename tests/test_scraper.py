import pytest

from scraper import GitHubScraper


class TestGitHubScraper:

    @pytest.mark.vcr
    def test_crawl_search_results_success(self):
        scraper = GitHubScraper(proxies=[
            "148.72.140.24:30127",
        ])

        results = scraper.crawl_search_results(search_terms=[
            'openstack',
            'nova',
            'css',
        ])
        assert len(results) == 10
        assert results[0] == {"url": "https://github.com/openstack/nova"}
