"""Negative scenarios for write operations.

The tests assert what a well-behaved API SHOULD return. JSONPlaceholder does not
validate input, so tests that hit a known defect are marked known_bug with the bug id
from FINDINGS.md. xfail_strict makes a fixed bug XPASS and fail the run, so we know
to remove the marker.
"""

import json

import pytest

from assertions.response import assert_status
from data.constants import NONEXISTENT_ID
from data.payloads import new_post, without

pytestmark = [pytest.mark.posts, pytest.mark.negative]

MISSING_FIELDS = pytest.mark.known_bug("BUG-01: POST /posts accepts a payload with missing required fields")
INVALID_VALUES = pytest.mark.known_bug("BUG-02: POST /posts accepts fields with a wrong type or invalid value")
MISSING_POST_WRITE = pytest.mark.known_bug("BUG-06: PATCH/DELETE on a missing post return 200 instead of 404")

MALFORMED_JSON = "{not valid json"


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(None, id="no-body", marks=MISSING_FIELDS),
        pytest.param({}, id="empty-object", marks=MISSING_FIELDS),
        pytest.param(without(new_post(), "title"), id="missing-title", marks=MISSING_FIELDS),
        pytest.param(without(new_post(), "body"), id="missing-body", marks=MISSING_FIELDS),
        pytest.param(without(new_post(), "userId"), id="missing-userId", marks=MISSING_FIELDS),
        pytest.param(new_post(title=123), id="title-is-number", marks=INVALID_VALUES),
        pytest.param(new_post(body=None), id="body-is-null", marks=INVALID_VALUES),
        pytest.param(new_post(userId="abc"), id="userId-is-string", marks=INVALID_VALUES),
        pytest.param(new_post(userId=-1), id="userId-is-negative", marks=INVALID_VALUES),
    ],
)
def test_create_post_rejects_invalid_payload(posts_api, payload):
    response = posts_api.create(payload)

    assert_status(response, 400)


@pytest.fixture
def malformed_json_response(posts_api):
    return posts_api.create(data=MALFORMED_JSON, headers={"Content-Type": "application/json"})


@pytest.mark.known_bug("BUG-03: malformed JSON returns 500 instead of 400")
def test_malformed_json_returns_400(malformed_json_response):
    assert_status(malformed_json_response, 400)


@pytest.mark.known_bug("BUG-04: error response leaks a server stack trace")
def test_error_response_does_not_leak_internals(malformed_json_response):
    assert "node_modules" not in malformed_json_response.text, "Server stack trace exposed to the client"


@pytest.mark.parametrize(
    "write",
    [
        pytest.param(
            lambda api: api.update(NONEXISTENT_ID, new_post()),
            id="PUT",
            marks=pytest.mark.known_bug("BUG-05: PUT on a missing post returns 500 instead of 404"),
        ),
        pytest.param(lambda api: api.patch(NONEXISTENT_ID, {"title": "patched"}), id="PATCH", marks=MISSING_POST_WRITE),
        pytest.param(lambda api: api.delete(NONEXISTENT_ID), id="DELETE", marks=MISSING_POST_WRITE),
    ],
)
def test_write_to_nonexistent_post_returns_404(posts_api, write):
    response = write(posts_api)

    assert_status(response, 404)


@pytest.mark.known_bug("BUG-07: a body sent without Content-Type is silently ignored")
def test_body_without_content_type_is_rejected(posts_api):
    response = posts_api.create(data=json.dumps(new_post()))

    assert_status(response, 400, 415)
