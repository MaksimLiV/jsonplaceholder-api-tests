from typing import Any

import requests

from api.http_client import HttpClient


class BaseResource:
    """One subclass per API resource. Knows the paths, not how HTTP works.

    CRUD operations shared by every resource live here, so a new resource
    only needs to declare its `path`.
    """

    path = ""

    def __init__(self, http: HttpClient):
        self.http = http

    def _url(self, *parts: object) -> str:
        return "/".join([self.path, *(str(part) for part in parts)])

    def get_all(self, **filters: object) -> requests.Response:
        return self.http.get(self.path, params=filters)

    def get(self, resource_id: int | str) -> requests.Response:
        return self.http.get(self._url(resource_id))

    def create(self, payload: dict | None = None, **kwargs: Any) -> requests.Response:
        return self.http.post(self.path, json=payload, **kwargs)

    def update(self, resource_id: int | str, payload: dict | None = None, **kwargs: Any) -> requests.Response:
        return self.http.put(self._url(resource_id), json=payload, **kwargs)

    def patch(self, resource_id: int | str, payload: dict | None = None, **kwargs: Any) -> requests.Response:
        return self.http.patch(self._url(resource_id), json=payload, **kwargs)

    def delete(self, resource_id: int | str, **kwargs: Any) -> requests.Response:
        return self.http.delete(self._url(resource_id), **kwargs)
