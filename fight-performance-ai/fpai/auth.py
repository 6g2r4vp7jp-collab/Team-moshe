"""WHOOP OAuth 2.0 (authorization code flow + refresh tokens).

Two ways to complete login:
  * local  - `login`: opens the browser and catches the redirect on localhost.
  * remote - `start` prints the URL; after approving, copy the URL the browser
             was redirected to and pass it to `finish`.
"""
from __future__ import annotations

import http.server
import json
import secrets
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

from . import config

PENDING_FILE = "pending_auth.json"
PENDING_TTL = 15 * 60  # seconds


class AuthError(RuntimeError):
    pass


def _post_form(url: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json",
                 "User-Agent": config.USER_AGENT},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        # Only surface the error code/description, never the request body.
        try:
            err = json.loads(e.read())
            msg = f"{err.get('error')}: {err.get('error_description', '')}"
        except Exception:
            msg = e.reason
        raise AuthError(f"WHOOP token endpoint returned HTTP {e.code} ({msg})") from None


def build_authorize_url() -> str:
    client = config.load_client()
    state = secrets.token_urlsafe(6)  # exactly 8 chars, as WHOOP requires
    config.write_private_json(
        config.home() / PENDING_FILE,
        {"state": state, "redirect_uri": client["redirect_uri"], "created": time.time()},
    )
    params = {
        "response_type": "code",
        "client_id": client["client_id"],
        "redirect_uri": client["redirect_uri"],
        "scope": " ".join(config.SCOPES),
        "state": state,
    }
    return config.AUTH_URL + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)


def _save_tokens(resp: dict) -> dict:
    if "access_token" not in resp:
        raise AuthError("Unexpected token response (no access_token)")
    tokens = {
        "access_token": resp["access_token"],
        "refresh_token": resp.get("refresh_token"),
        "scope": resp.get("scope"),
        "token_type": resp.get("token_type"),
        "expires_at": time.time() + int(resp.get("expires_in", 3600)) - 60,
        "obtained_at": time.time(),
    }
    config.write_private_json(config.token_file(), tokens)
    return tokens


def finish(redirected_url: str) -> dict:
    """Validate state and exchange the authorization code for tokens."""
    pending = config.read_json(config.home() / PENDING_FILE)
    if not pending:
        raise AuthError("No pending login. Run `start` (or `login`) first.")
    if time.time() - pending["created"] > PENDING_TTL:
        raise AuthError("Login attempt expired. Run `start` again.")

    q = urllib.parse.parse_qs(urllib.parse.urlparse(redirected_url.strip()).query)
    if "error" in q:
        raise AuthError(f"WHOOP denied authorization: {q['error'][0]} {q.get('error_description', [''])[0]}")
    state = q.get("state", [None])[0]
    code = q.get("code", [None])[0]
    if not code:
        raise AuthError("No `code` parameter found in the URL.")
    if not state or not secrets.compare_digest(state, pending["state"]):
        raise AuthError("State mismatch - possible CSRF. Start the login again.")

    client = config.load_client()
    resp = _post_form(
        config.TOKEN_URL,
        {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client["client_id"],
            "client_secret": client["client_secret"],
            "redirect_uri": pending["redirect_uri"],
        },
    )
    (config.home() / PENDING_FILE).unlink(missing_ok=True)
    tokens = _save_tokens(resp)
    if not tokens.get("refresh_token"):
        print("אזהרה: לא התקבל refresh token (ה-scope offline לא אושר?). תצטרכו להתחבר מחדש כל שעה.")
    return tokens


def refresh() -> dict:
    tokens = config.read_json(config.token_file())
    if not tokens or not tokens.get("refresh_token"):
        raise AuthError("No refresh token stored. Log in again.")
    client = config.load_client()
    resp = _post_form(
        config.TOKEN_URL,
        {
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
            "client_id": client["client_id"],
            "client_secret": client["client_secret"],
            "scope": "offline",
        },
    )
    # WHOOP rotates refresh tokens: the old one is now invalid.
    return _save_tokens(resp)


def get_access_token() -> str:
    tokens = config.read_json(config.token_file())
    if not tokens:
        raise AuthError("Not connected to WHOOP yet. Run `python3 fpai.py login`.")
    if time.time() >= tokens.get("expires_at", 0):
        tokens = refresh()
    return tokens["access_token"]


def status() -> dict:
    tokens = config.read_json(config.token_file())
    if not tokens:
        return {"connected": False}
    return {
        "connected": True,
        "scope": tokens.get("scope"),
        "has_refresh_token": bool(tokens.get("refresh_token")),
        "access_token_valid_for_sec": max(0, int(tokens.get("expires_at", 0) - time.time())),
    }


def logout(revoke: bool = True) -> None:
    if revoke:
        try:
            token = get_access_token()
            req = urllib.request.Request(
                config.API_BASE + "/v2/user/access",
                headers={"Authorization": f"Bearer {token}", "User-Agent": config.USER_AGENT},
                method="DELETE",
            )
            urllib.request.urlopen(req, timeout=30).close()
        except Exception as e:  # still remove local tokens
            print(f"Revocation failed ({type(e).__name__}); removing local tokens anyway.")
    config.token_file().unlink(missing_ok=True)


def login_local(timeout: int = 300) -> dict:
    """Open the browser and catch the redirect on the configured localhost port."""
    client = config.load_client()
    redirect = urllib.parse.urlparse(client["redirect_uri"])
    if redirect.hostname not in ("localhost", "127.0.0.1"):
        raise AuthError("Local login needs a localhost redirect URI. Use `start` / `finish` instead.")

    captured: dict = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if urllib.parse.urlparse(self.path).path != redirect.path:
                self.send_response(404)
                self.end_headers()
                return
            captured["url"] = f"http://{self.headers.get('Host')}{self.path}"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                "<html dir=rtl><body style='font-family:sans-serif'><h2>החיבור ל-WHOOP התקבל.</h2>"
                "<p>אפשר לסגור את החלון ולחזור ל-Claude Code.</p></body></html>".encode()
            )

        def log_message(self, *a):
            pass

    server = http.server.HTTPServer(("127.0.0.1", redirect.port or 80), Handler)
    url = build_authorize_url()
    print("פותח דפדפן להתחברות ל-WHOOP. אם הוא לא נפתח, היכנסו לכתובת:\n" + url)
    webbrowser.open(url)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    deadline = time.time() + timeout
    while "url" not in captured and time.time() < deadline:
        time.sleep(0.3)
    server.shutdown()
    if "url" not in captured:
        raise AuthError("Timed out waiting for the WHOOP redirect.")
    return finish(captured["url"])
