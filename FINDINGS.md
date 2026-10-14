# Bugs found in JSONPlaceholder

I found these while writing the tests.

JSONPlaceholder is a fake API and doesn't validate input on purpose, so this behavior is expected for this
service. I still wrote the bugs up as if it were a real product, because on a real API each of them would
need a fix.

Every bug has a test in `tests/negative/test_invalid_payloads.py`. The test checks the correct behavior and
has a `known_bug` marker, so it shows as xfail until the bug is fixed (see the README for how this works).
To run only these tests:

```bash
pytest -m known_bug
```

| ID | Bug | Severity |
|---|---|---|
| BUG-01 | POST /posts accepts a body with missing fields | High |
| BUG-02 | POST /posts accepts wrong types and invalid values | High |
| BUG-03 | Invalid JSON returns 500 instead of 400 | Medium |
| BUG-04 | Error responses show the server stack trace | Medium |
| BUG-05 | PUT on a post that doesn't exist returns 500 instead of 404 | Medium |
| BUG-06 | PATCH and DELETE on a post that doesn't exist return 200 instead of 404 | Medium |
| BUG-07 | A body without Content-Type is ignored, but the API returns 201 | Low |

Severity is how I would rate it for a real API.

## BUG-01: POST /posts accepts a body with missing fields

```bash
curl -X POST -H 'Content-Type: application/json' -d '{}' https://jsonplaceholder.typicode.com/posts
```

Expected: 400 with a message that `title`, `body` and `userId` are missing.

Actual: 201, response `{"id": 101}`.

The same happens with no body at all, or when only one of the fields is missing.

Test: `test_create_post_rejects_invalid_payload` (cases `no-body`, `empty-object`, `missing-*`).

## BUG-02: POST /posts accepts wrong types and invalid values

```bash
curl -X POST -H 'Content-Type: application/json' \
  -d '{"title": 123, "body": null, "userId": "abc"}' https://jsonplaceholder.typicode.com/posts
```

Expected: 400 with a validation error for each field.

Actual: 201, and the wrong values come back as if they were saved:

```json
{"title": 123, "body": null, "userId": "abc", "id": 101}
```

A negative `userId` (`-1`) is accepted too.

Test: `test_create_post_rejects_invalid_payload` (cases `title-is-number`, `body-is-null`, `userId-*`).

## BUG-03: Invalid JSON returns 500 instead of 400

```bash
curl -X POST -H 'Content-Type: application/json' -d '{not valid json' https://jsonplaceholder.typicode.com/posts
```

Expected: 400. The client sent broken JSON, so it's a client error.

Actual: 500 Internal Server Error.

Test: `test_malformed_json_returns_400`

## BUG-04: Error responses show the server stack trace

Same request as in BUG-03. The response body is the full Node.js stack trace:

```
SyntaxError: Expected property name or '}' in JSON at position 1 (line 1 column 2)
    at JSON.parse (<anonymous>)
    at parse (/app/node_modules/body-parser/lib/types/json.js:89:19)
    ...
```

The 500 from BUG-05 shows a stack trace too.

Expected: a short error message without internal details.

Actual: the stack trace, with file paths on the server and the names of the libraries it uses
(express, body-parser, json-server). This is a security issue: it tells anyone what the server runs on.

Test: `test_error_response_does_not_leak_internals`

## BUG-05: PUT on a post that doesn't exist returns 500 instead of 404

```bash
curl -X PUT -H 'Content-Type: application/json' \
  -d '{"title": "t", "body": "b", "userId": 1}' https://jsonplaceholder.typicode.com/posts/9999
```

Expected: 404.

Actual: 500 with `TypeError: Cannot read properties of undefined (reading 'id')`. It looks like the server
doesn't check that the post exists before updating it.

Test: `test_write_to_nonexistent_post_returns_404[PUT]`

## BUG-06: PATCH and DELETE on a post that doesn't exist return 200 instead of 404

```bash
curl -X PATCH -H 'Content-Type: application/json' -d '{"title": "t"}' https://jsonplaceholder.typicode.com/posts/9999
curl -X DELETE https://jsonplaceholder.typicode.com/posts/9999
```

Expected: 404, the same as `GET /posts/9999` returns.

Actual: 200. PATCH even returns the sent data back (`{"title": "t"}`), DELETE returns `{}`.
The client thinks the change worked.

Test: `test_write_to_nonexistent_post_returns_404[PATCH]` and `[DELETE]`

## BUG-07: A body without Content-Type is ignored, but the API returns 201

```bash
curl -X POST -H 'Content-Type:' --data-binary '{"title": "t", "body": "b", "userId": 1}' \
  https://jsonplaceholder.typicode.com/posts
```

Expected: 415 Unsupported Media Type (or 400).

Actual: 201 with `{"id": 101}`. The data is ignored and the client gets no error.

Test: `test_body_without_content_type_is_rejected`

## Not bugs, but good to know

- Nothing is saved. POST always returns `id: 101`, and PUT/PATCH/DELETE don't change the data.
  The JSONPlaceholder guide says this, so I don't count it as a bug.
- `GET /posts/9999/comments` returns 200 and `[]`. For a filtered list that's fine, so the test
  `test_comments_for_nonexistent_post_are_empty` checks this behavior.
- 404 responses have an empty body `{}` with no error message.
