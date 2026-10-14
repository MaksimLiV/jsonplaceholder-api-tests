from uuid import uuid4


def new_post(**overrides) -> dict:
    """A valid post body. Override any field: new_post(title="custom")."""
    payload = {
        "title": f"qa-post-{uuid4().hex[:8]}",
        "body": "Created by an automated API test",
        "userId": 1,
    }
    payload.update(overrides)
    return payload


def without(payload: dict, *fields: str) -> dict:
    """Copy of the payload with some fields removed - for "missing field" tests."""
    return {key: value for key, value in payload.items() if key not in fields}
