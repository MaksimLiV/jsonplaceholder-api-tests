import logging

import pytest

from api.http_client import HttpClient
from api.resources.comments import CommentsApi
from api.resources.posts import PostsApi
from api.resources.users import UsersApi
from config.settings import Settings


def pytest_addoption(parser):
    parser.addoption(
        "--base-url", action="store", default=None, help="API base URL (overrides the API_BASE_URL env variable)"
    )


def pytest_report_header(config):
    settings = Settings.load(config.getoption("--base-url"))
    return f"API under test: {settings.base_url} (timeout {settings.timeout}s, retries {settings.retries})"


def pytest_collection_modifyitems(items):
    for item in items:
        # Every test belongs to the full regression scope, so nobody has to remember to tag it.
        item.add_marker(pytest.mark.full)
        if bug := item.get_closest_marker("known_bug"):
            reason = bug.args[0] if bug.args else "Known API defect, see FINDINGS.md"
            item.add_marker(pytest.mark.xfail(reason=reason))


def pytest_runtest_logstart(nodeid, location):
    # Without this the log file has no test names, so a request can't be traced back to its test.
    logging.getLogger("tests").info("=== %s", nodeid)


@pytest.fixture(scope="session")
def settings(pytestconfig) -> Settings:
    return Settings.load(pytestconfig.getoption("--base-url"))


@pytest.fixture(scope="session")
def http(settings):
    with HttpClient(settings) as client:
        yield client


@pytest.fixture(scope="session")
def users_api(http):
    return UsersApi(http)


@pytest.fixture(scope="session")
def posts_api(http):
    return PostsApi(http)


@pytest.fixture(scope="session")
def comments_api(http):
    return CommentsApi(http)
