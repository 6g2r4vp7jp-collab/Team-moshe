"""Paths and secret loading for Fight Performance AI.

Secrets never live in the repository. They are read from, in order:
  1. Environment variables WHOOP_CLIENT_ID / WHOOP_CLIENT_SECRET
  2. $FPAI_HOME/client.json  (created by `fpai.py setup`, file mode 0600)

Tokens and pulled data are stored under $FPAI_HOME
(default: ~/.config/fight-performance-ai), outside the repo, mode 0600.
"""
from __future__ import annotations

import json
import os
import stat
import tempfile
from pathlib import Path

# Official values from https://developer.whoop.com/docs/developing/oauth
AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
API_BASE = "https://api.prod.whoop.com/developer"

# `offline` is required to receive a refresh token.
SCOPES = [
    "offline",
    "read:profile",
    "read:body_measurement",
    "read:cycles",
    "read:recovery",
    "read:sleep",
    "read:workout",
]

DEFAULT_REDIRECT_URI = "http://localhost:8765/callback"

# Cloudflare in front of WHOOP rejects the default Python-urllib User-Agent.
USER_AGENT = "FightPerformanceAI/0.1"


def home() -> Path:
    p = Path(os.environ.get("FPAI_HOME", Path.home() / ".config" / "fight-performance-ai"))
    p.mkdir(parents=True, exist_ok=True)
    try:
        p.chmod(0o700)
    except OSError:
        pass
    return p


def write_private_json(path: Path, data: dict) -> None:
    """Atomically write JSON readable only by the current user."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
    try:
        os.fchmod(fd, stat.S_IRUSR | stat.S_IWUSR)
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def client_file() -> Path:
    return home() / "client.json"


def token_file() -> Path:
    return home() / "tokens.json"


def raw_dir() -> Path:
    d = home() / "raw"
    d.mkdir(exist_ok=True)
    return d


class MissingCredentials(RuntimeError):
    pass


def load_client() -> dict:
    cid = os.environ.get("WHOOP_CLIENT_ID")
    secret = os.environ.get("WHOOP_CLIENT_SECRET")
    redirect = os.environ.get("WHOOP_REDIRECT_URI")
    stored = read_json(client_file()) or {}
    cid = cid or stored.get("client_id")
    secret = secret or stored.get("client_secret")
    redirect = redirect or stored.get("redirect_uri") or DEFAULT_REDIRECT_URI
    if not cid or not secret:
        raise MissingCredentials(
            "חסרים פרטי אפליקציית WHOOP (Client ID / Client Secret). "
            "הריצו `python3 fpai.py setup` או הגדירו WHOOP_CLIENT_ID ו-WHOOP_CLIENT_SECRET."
        )
    return {"client_id": cid, "client_secret": secret, "redirect_uri": redirect}
