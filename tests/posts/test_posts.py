import pytest

from assertions.response import (
    assert_fields_equal,
    assert_json_content_type,
    assert_status,
    parse_as,
    parse_list_as,
)
from data.constants import EXISTING_POST_ID, NEXT_POST_ID, TOTAL_POSTS, TOTAL_USERS
from data.payloads import new_post
from models.post import Post

pytestmark = pytest.mark.posts


@pytest.mark.smoke
def test_get_all_posts(posts_api):
    response = posts_api.get_all()

    assert_status(response, 200)
    assert_json_content_type(response)
    assert len(parse_list_as(response, Post)) == TOTAL_POSTS


@pytest.mark.parametrize("user_id", [1, 7, TOTAL_USERS])
def test_filter_posts_by_user(posts_api, user_id):
    posts = parse_list_as(posts_api.get_all(userId=user_id), Post)

    assert posts, f"User {user_id} has no posts"
    assert all(post.user_id == user_id for post in posts)


@pytest.mark.smoke
def test_create_post(posts_api):
    payload = new_post()

    response = posts_api.create(payload)

    assert_status(response, 201)
    created = parse_as(response, Post)
    assert_fields_equal(response.json(), payload)
    assert created.id == NEXT_POST_ID, "New post should get the next free id"


@pytest.mark.smoke
def test_update_post(posts_api):
    payload = new_post(userId=2)

    response = posts_api.update(EXISTING_POST_ID, payload)

    assert_status(response, 200)
    updated = parse_as(response, Post)
    assert_fields_equal(response.json(), payload)
    assert updated.id == EXISTING_POST_ID


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", "patched title"),
        ("body", "patched body"),
        ("userId", 3),
    ],
)
def test_patch_post_changes_only_given_field(posts_api, field, value):
    original = posts_api.get(EXISTING_POST_ID)
    assert_status(original, 200)

    response = posts_api.patch(EXISTING_POST_ID, {field: value})

    assert_status(response, 200)
    parse_as(response, Post)
    assert_fields_equal(response.json(), {**original.json(), field: value})


def test_delete_post(posts_api):
    response = posts_api.delete(EXISTING_POST_ID)

    assert_status(response, 200)
    assert response.json() == {}
