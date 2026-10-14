import requests

from api.resources.base import BaseResource


class PostsApi(BaseResource):
    path = "/posts"

    def comments(self, post_id: int | str) -> requests.Response:
        return self.http.get(self._url(post_id, "comments"))
