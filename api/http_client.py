import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from api.curl import to_curl
from config.settings import Settings

log = logging.getLogger("api")


class HttpClient:
    """Thin wrapper around requests.Session: base URL, timeout, retries, logging."""

    def __init__(self, settings: Settings):
        self.base_url = settings.base_url
        self.timeout = settings.timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

        retry = Retry(
            total=settings.retries,
            read=False,
            backoff_factor=0.5,
            # Only transient errors: rate limiting and gateway errors. A 500 here is a real bug -
            # retrying would hide it.
            status_forcelist=(429, 502, 503, 504),
            # POST and PATCH are not idempotent, so they are never retried.
            allowed_methods=frozenset({"GET", "PUT", "DELETE", "HEAD", "OPTIONS"}),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self.session.request(method, url, **kwargs)
        except requests.RequestException as error:
            # Timeouts and connection errors are exactly the failures the log is needed for.
            log.error("%s %s failed: %s", method, url, error)
            raise
        log.info("%s %s -> %s (%d ms)", method, url, response.status_code, response.elapsed.total_seconds() * 1000)
        log.debug("Reproduce with: %s", to_curl(response.request))
        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs) -> requests.Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.request("DELETE", path, **kwargs)

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
