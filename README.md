# jsonplaceholder-api-tests

[![API tests](https://github.com/MaksimLiV/jsonplaceholder-api-tests/actions/workflows/tests.yml/badge.svg)](https://github.com/MaksimLiV/jsonplaceholder-api-tests/actions/workflows/tests.yml)

Automated API tests for [JSONPlaceholder](https://jsonplaceholder.typicode.com/guide/).
Written in Python with pytest, requests and pydantic.

## Setup

You need Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

To also get the linter (ruff), install `requirements-dev.txt` instead, then run `ruff check .` and `ruff format --check .`.

The tests call the real JSONPlaceholder API, so you need an internet connection.

## Running the tests

Run everything:

```bash
pytest
```

Some tests show as `xfailed`. These are bugs I found in the API, see "Known bugs" below.
A run is OK if nothing is `failed`.

Run one scope with a marker:

```bash
pytest -m smoke
pytest -m full
pytest -m negative
pytest -m posts
pytest -m "posts and not known_bug"
```

Markers:

- `smoke`: a few critical checks, good for a quick run after a change
- `full`: the whole API regression. `conftest.py` adds it to every test, so nobody has to remember to tag a new test
- `negative`: invalid input and error cases
- `known_bug`: tests for bugs I found in the API, see [FINDINGS.md](FINDINGS.md)
- `users`, `posts`, `comments`: tests for one resource

## Configuration

The default base URL is `https://jsonplaceholder.typicode.com`. To use another one:

```bash
pytest --base-url http://localhost:3000
```

or set the `API_BASE_URL` environment variable. If both are set, `--base-url` wins.
Timeout and retries can be changed with `API_TIMEOUT` (seconds, default 10) and `API_RETRIES` (default 3).

The URL in use is printed at the top of the pytest output.

## Reports and logs

Every run creates two files in `reports/`:

- `report.html`: the pytest-html report. You can open the log of each test there.
- `test-run.log`: debug log with every request, its status and duration, and a curl command for it.
  Each test starts with a `=== <test id>` line, so you can see which test sent which request.
  Requests that fail with a timeout or a connection error are logged as errors.

To open the report, run `open reports/report.html` (macOS) or open the file in a browser.

When a check fails, the message includes a curl command, so the request is easy to repeat by hand:

```
AssertionError: Expected status 400, got 201
  Reproduce: curl -X POST -H 'User-Agent: python-requests/2.34.2' -H 'Accept: application/json' -H 'Connection: keep-alive' -H 'Content-Type: application/json' -d '{}' https://jsonplaceholder.typicode.com/posts
  Response 201: {
  "id": 101
}
```

## Project structure

```
api/          HTTP client, curl builder, one class per resource (users, posts, comments)
assertions/   reusable checks: status, content type, response schema
config/       settings: base URL, timeout, retries
data/         payload builders and dataset constants
models/       pydantic models for API responses
tests/        users/, posts/, comments/, negative/, consistency/ (checks across endpoints)
conftest.py   fixtures, the --base-url option, marker handling
.github/      CI workflow
```

Tests never call `requests` directly and never build URLs. They use the resource classes
(`posts_api.create(payload)`), and the resource classes use `HttpClient`. So if a path or a header
changes, there is only one place to update.

## What is covered

All 10 scenarios from the assignment:

| # | Scenario | Test |
|---|---|---|
| 1 | `GET /users` | `tests/users/test_users.py::test_get_all_users` |
| 2 | `GET /users/{id}` | `tests/users/test_users.py::test_get_user_by_id` |
| 3 | `GET /users/9999` | `tests/users/test_users.py::test_get_nonexistent_user_returns_404` |
| 4 | `GET /posts` | `tests/posts/test_posts.py::test_get_all_posts` |
| 5 | `POST /posts` | `tests/posts/test_posts.py::test_create_post` |
| 6 | `PUT /posts/{id}` | `tests/posts/test_posts.py::test_update_post` |
| 7 | `PATCH /posts/{id}` | `tests/posts/test_posts.py::test_patch_post_changes_only_given_field` |
| 8 | `DELETE /posts/{id}` | `tests/posts/test_posts.py::test_delete_post` |
| 9 | `GET /posts/{id}/comments` | `tests/comments/test_comments.py::test_get_comments_for_post` |
| 10 | Invalid payload | `tests/negative/test_invalid_payloads.py::test_create_post_rejects_invalid_payload` |

For scenario 10 there are cases for missing fields, wrong types and an empty body. They check what the API should
do (400), see "Known bugs" below.

I also added a few more checks: filtering posts by user, invalid JSON, PUT/PATCH/DELETE on a post
that doesn't exist, a body without `Content-Type`, comparing `/posts/1/comments` with
`/comments?postId=1`, and checking that every post belongs to an existing user.

## A few decisions

**Schema validation.** Response models use pydantic with `strict=True` and `extra="forbid"`.
If the API returns `"1"` instead of `1`, or adds or renames a field, the test fails.

**Request bodies are plain dicts.** They are built by `data/payloads.py`, not by models, because the negative
tests need to send missing fields and wrong types, and a model would refuse to build those.

**Retries.** The client retries 429 (rate limit) and 502/503/504, but only for GET, PUT and DELETE.
I don't retry POST and PATCH because that could create duplicates. Failed connections are retried for every
method, because then the request never reached the server. I don't retry a 500 (that's a real bug) or a read
timeout (a slow response is something to report).

**Known bugs.** JSONPlaceholder doesn't validate input, so most negative tests can't pass. I didn't want
tests that just accept the wrong behavior, like expecting 201 for an empty body. So the tests check what
the API should do, and are marked with the bug id:

```python
@pytest.mark.known_bug("BUG-03: malformed JSON returns 500 instead of 400")
```

`conftest.py` turns this marker into a strict xfail. While the bug is there, the test is shown as xfail
and the run is green. If the bug gets fixed, the test passes and the run fails, so I know to remove the
marker.

## Adding a new resource

For example `/albums`:

1. Add `api/resources/albums.py` with `class AlbumsApi(BaseResource): path = "/albums"`.
   The CRUD methods come from `BaseResource`.
2. Add a model in `models/album.py`.
3. Add an `albums_api` fixture to `conftest.py` and an `albums` marker to `pyproject.toml`.
4. Write the tests in `tests/albums/`.

## Notes about JSONPlaceholder

- It doesn't save anything. POST always returns `id: 101`, and PUT/PATCH/DELETE don't change the data.
  That's why the write tests check the response and don't do a GET afterwards.
- The dataset sizes (10 users, 100 posts, 5 comments per post) are in `data/constants.py`.
  If you run the tests against your own json-server, you may need to change them.

## CI

GitHub Actions runs all tests on Python 3.11, the lowest version the project supports.
It runs on every push to `main` and manually from the Actions tab (Run workflow).
The HTML report is saved as a build artifact.
