"""Checks that different endpoints tell the same story about the same data."""

import pytest

from assertions.response import assert_status, parse_list_as
from models.post import Post
from models.user import User

pytestmark = pytest.mark.posts


@pytest.mark.comments
@pytest.mark.parametrize("post_id", [1, 42])
def test_nested_and_filtered_comments_match(posts_api, comments_api, post_id):
    nested = posts_api.comments(post_id)
    filtered = comments_api.get_all(postId=post_id)

    assert_status(nested, 200)
    assert_status(filtered, 200)
    # Guard against a false pass: two empty lists are equal, but prove nothing.
    assert nested.json(), f"No comments returned for post {post_id}"
    assert nested.json() == filtered.json()


@pytest.mark.users
def test_every_post_belongs_to_existing_user(posts_api, users_api):
    user_ids = {user.id for user in parse_list_as(users_api.get_all(), User)}
    posts = parse_list_as(posts_api.get_all(), Post)

    orphans = [post.id for post in posts if post.user_id not in user_ids]
    assert not orphans, f"Posts with unknown userId: {orphans}"
