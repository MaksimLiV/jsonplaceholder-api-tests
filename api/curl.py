import shlex

import requests


def to_curl(prepared: requests.PreparedRequest) -> str:
    """Turn a sent request into a curl command you can paste into a terminal or a bug report."""
    parts = ["curl", "-X", prepared.method]
    for name, value in prepared.headers.items():
        if name in ("Accept-Encoding", "Content-Length"):
            continue
        parts += ["-H", f"{name}: {value}"]
    if prepared.body:
        body = prepared.body.decode() if isinstance(prepared.body, bytes) else prepared.body
        parts += ["-d", body]
    parts.append(prepared.url)
    return shlex.join(parts)
