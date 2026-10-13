"""L'en-tête `X-Revision` : le commit de l'image, sur chaque réponse.

Le déploiement attend qu'une page réponde 200 avec le commit qu'il vient de
déployer : il lit cet en-tête pour savoir quelle image répond. Une redirection
de `redirect_errors` le porte aussi.
"""

import asyncio

from oceens import main


def get(path):
    """Statut et en-têtes de la réponse à `GET path`, sans serveur."""
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": [(b"host", b"oceens.example")],
        "client": ("testclient", 50000),
        "server": ("oceens.example", 80),
    }
    sent = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    asyncio.run(main.app(scope, receive, send))
    headers = {k.decode().lower(): v.decode() for k, v in sent[0]["headers"]}
    return sent[0]["status"], headers


def test_a_page_names_the_revision(monkeypatch):
    monkeypatch.setattr(main, "REVISION", "abc123")
    status, headers = get("/")
    assert status == 200
    assert headers["x-revision"] == "abc123"


def test_a_redirect_names_the_revision_too(monkeypatch):
    monkeypatch.setattr(main, "REVISION", "abc123")
    status, headers = get("/nope")
    assert status == 303
    assert headers["x-revision"] == "abc123"


def test_outside_an_image_the_revision_is_unknown():
    status, headers = get("/")
    assert status == 200
    assert headers["x-revision"] == "unknown"
