import pytest

from assertions.response import assert_status, parse_list_as
from data.constants import COMMENTS_PER_POST, NONEXISTENT_ID, TOTAL_POSTS
from models.comment import Comment

pytestmark = pytest.mark.comments


@pytest.mark.parametrize(
    "post_id",
    [
        pytest.param(1, marks=pytest.mark.smoke),
        50,
        TOTAL_POSTS,
    ],
)
def test_get_comments_for_post(posts_api, post_id):
    response = posts_api.comments(post_id)

    assert_status(response, 200)
    comments = parse_list_as(response, Comment)
    assert len(comments) == COMMENTS_PER_POST
    assert all(comment.post_id == post_id for comment in comments)


@pytest.mark.negative
def test_comments_for_nonexistent_post_are_empty(posts_api):
    response = posts_api.comments(NONEXISTENT_ID)

    assert_status(response, 200)
    assert response.json() == []
