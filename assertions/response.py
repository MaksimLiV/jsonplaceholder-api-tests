from typing import TypeVar

import requests
from pydantic import BaseModel

from api.curl import to_curl

Model = TypeVar("Model", bound=BaseModel)

MAX_BODY_IN_MESSAGE = 500


def _context(response: requests.Response) -> str:
    """Request and response details appended to every failure message."""
    body = response.text
    if len(body) > MAX_BODY_IN_MESSAGE:
        body = body[:MAX_BODY_IN_MESSAGE] + "... (truncated)"
    return f"\n  Reproduce: {to_curl(response.request)}\n  Response {response.status_code}: {body}"


def assert_status(response: requests.Response, expected: int, *alternatives: int) -> None:
    """The status must be `expected` or one of `alternatives`: assert_status(response, 400, 415)."""
    allowed = (expected, *alternatives)
    message = f"Expected status {' or '.join(map(str, allowed))}, got {response.status_code}"
    assert response.status_code in allowed, message + _context(response)


def assert_json_content_type(response: requests.Response) -> None:
    content_type = response.headers.get("Content-Type", "")
    assert content_type.startswith("application/json"), (
        f"Expected a JSON response, got Content-Type '{content_type}'" + _context(response)
    )


def parse_as(response: requests.Response, model: type[Model]) -> Model:
    """Validate the response body against a model and return the parsed object."""
    try:
        return model.model_validate(response.json())
    # Covers both a body that is not JSON and pydantic's ValidationError (a ValueError subclass).
    except ValueError as error:
        raise AssertionError(f"Response does not match {model.__name__}:\n{error}" + _context(response)) from None


def parse_list_as(response: requests.Response, model: type[Model]) -> list[Model]:
    """Same as parse_as, for endpoints that return a JSON array."""
    try:
        data = response.json()
        assert isinstance(data, list), f"Expected a JSON list, got {type(data).__name__}" + _context(response)
        return [model.model_validate(item) for item in data]
    except ValueError as error:
        raise AssertionError(f"Response does not match list[{model.__name__}]:\n{error}" + _context(response)) from None


def assert_fields_equal(actual: dict, expected: dict) -> None:
    """Every key in `expected` must be in `actual` with the same value. Extra keys are fine."""
    mismatches = {
        key: {"expected": value, "actual": actual.get(key, "<missing>")}
        for key, value in expected.items()
        if key not in actual or actual[key] != value
    }
    assert not mismatches, f"Fields differ from expected: {mismatches}"
