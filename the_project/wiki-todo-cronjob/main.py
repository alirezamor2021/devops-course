import json
import os
import sys
import urllib.error
import urllib.request


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


WIKI_RANDOM_URL = require_env("WIKI_RANDOM_URL")
TODO_BACKEND_URL = require_env("TODO_BACKEND_URL")
MAX_TODO_LENGTH = int(require_env("MAX_TODO_LENGTH"))
MAX_ATTEMPTS = int(require_env("MAX_ATTEMPTS"))
REQUEST_TIMEOUT_SECONDS = float(require_env("REQUEST_TIMEOUT_SECONDS"))
USER_AGENT = require_env("USER_AGENT")

REDIRECT_CODES = (301, 302, 303, 307, 308)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Stop urllib from following redirects so we can read the Location header."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


opener = urllib.request.build_opener(NoRedirect)


def get_random_article_url() -> str:
    req = urllib.request.Request(WIKI_RANDOM_URL, headers={"User-Agent": USER_AGENT})
    try:
        opener.open(req, timeout=REQUEST_TIMEOUT_SECONDS)
    except urllib.error.HTTPError as e:
        if e.code in REDIRECT_CODES:
            location = e.headers.get("Location")
            if location:
                return location
        raise
    raise RuntimeError("Expected a redirect from the random article URL")


def create_todo(text: str) -> int:
    body = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        TODO_BACKEND_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
        return resp.status


def main() -> None:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        url = get_random_article_url()
        text = f"Read {url}"
        if len(text) > MAX_TODO_LENGTH:
            print(f"Attempt {attempt}: too long ({len(text)} chars), picking another", flush=True)
            continue
        status = create_todo(text)
        print(f"Created todo '{text}' (HTTP {status})", flush=True)
        return

    print("Could not find an article short enough for a todo", flush=True)
    sys.exit(1)


if __name__ == "__main__":
    main()