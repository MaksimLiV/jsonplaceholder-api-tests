import pytest

from assertions.response import assert_json_content_type, assert_status, parse_as, parse_list_as
from data.constants import NONEXISTENT_ID, TOTAL_USERS
from models.user import User

pytestmark = pytest.mark.users


@pytest.mark.smoke
def test_get_all_users(users_api):
    response = users_api.get_all()

    assert_status(response, 200)
    assert_json_content_type(response)
    users = parse_list_as(response, User)
    assert len(users) == TOTAL_USERS
    assert len({user.id for user in users}) == TOTAL_USERS, "User ids are not unique"


@pytest.mark.parametrize(
    "user_id",
    [
        pytest.param(1, marks=pytest.mark.smoke),
        5,
        TOTAL_USERS,
    ],
)
def test_get_user_by_id(users_api, user_id):
    response = users_api.get(user_id)

    assert_status(response, 200)
    assert parse_as(response, User).id == user_id


@pytest.mark.negative
@pytest.mark.parametrize("user_id", [NONEXISTENT_ID, 0, -1, "abc"], ids=["too-big", "zero", "negative", "not-a-number"])
def test_get_nonexistent_user_returns_404(users_api, user_id):
    response = users_api.get(user_id)

    assert_status(response, 404)
    assert response.json() == {}
