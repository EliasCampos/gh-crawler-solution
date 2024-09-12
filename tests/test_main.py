import pytest
import json

from main import run_github_search_crawler
from scraper import GitHubScraper


@pytest.fixture
def temp_config_file(tmp_path):
    config_path = tmp_path / "config.json"

    config = {
        "keywords": [
            "flask",
            "fastapi",
        ],
        "proxies": [
            "194.126.37.94:8080",
            "13.78.125.167:8080"
        ],
        "type": "Repositories"
    }
    with config_path.open('w') as f:
        json.dump(config, f)

    return config_path


def test_run_github_search_crawler(mocker, temp_config_file):
    crawl_mock = mocker.patch.object(GitHubScraper, 'crawl_search_page', return_value=[])

    run_github_search_crawler(args=[str(temp_config_file)])

    assert crawl_mock.called
    assert crawl_mock.call_args.kwargs == {
        'search_terms': ['flask', 'fastapi'],
        'search_type': GitHubScraper.SearchType.REPOSITORIES.value,
    }
