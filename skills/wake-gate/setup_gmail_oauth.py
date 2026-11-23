#!/usr/bin/env python3
"""One-time, interactive setup for wake_gate.py's Gmail watcher.

This cannot be run by an agent on your behalf: step 3 opens a real browser
tied to your Google login and you click Allow yourself. Everything before
and after that click is scripted here so the manual part is only that one
click, not the whole OAuth dance.

Prerequisites (you do this once, in Google Cloud Console):
  1. console.cloud.google.com -> select or create a project.
  2. APIs & Services > Library > enable the "Gmail API".
  3. APIs & Services > OAuth consent screen > External (or Internal if the
     account is Workspace) > add scope
     https://www.googleapis.com/auth/gmail.readonly (this is enough to list
     mail; no send/modify scope is requested anywhere in this gate).
  4. APIs & Services > Credentials > Create Credentials > OAuth client ID >
     Application type "Desktop app". Copy the Client ID and Client secret.

Then run, from this folder:
    python setup_gmail_oauth.py --creds-file <path to client_secret_*.json>

It opens your default browser to Google's consent screen, listens on
127.0.0.1 for the redirect, exchanges the code for tokens, and writes
%USERPROFILE%\\.wake-gate-gmail.json in the exact shape
wake_gate.py's Gmail watcher expects. Nothing is written anywhere else.
"""

from __future__ import annotations

import argparse
import http.server
import json
import os
from pathlib import Path
import secrets
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser

AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
DEFAULT_OUT = Path.home() / ".wake-gate-gmail.json"
REDIRECT_PORT = 8765


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    result: dict = {}

    def do_GET(self) -> None:  # noqa: N802 (http.server API)
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        _CallbackHandler.result["code"] = params.get("code", [None])[0]
        _CallbackHandler.result["state"] = params.get("state", [None])[0]
        _CallbackHandler.result["error"] = params.get("error", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        if _CallbackHandler.result.get("code"):
            self.wfile.write(b"Authorized. You can close this tab and return to the terminal.")
        else:
            self.wfile.write(b"No authorization code received. Check the terminal.")

    def log_message(self, *_args: object) -> None:  # silence default stderr logging
        return


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--client-id", default=None)
    parser.add_argument("--client-secret", default=None)
    parser.add_argument(
        "--creds-file",
        default=None,
        help="Path to the client_secret_*.json Google Cloud hands you on download, OR a plain "
             "two-line file: client id on line 1, client secret on line 2. Preferred over the "
             "--client-secret flag, which leaks the secret into shell history.",
    )
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    # Resolve credentials without ever requiring them on the command line.
    # Order: --creds-file, then env vars, then the flags (discouraged).
    client_id, client_secret = args.client_id, args.client_secret
    if args.creds_file:
        raw = open(args.creds_file, encoding="utf-8").read().strip()
        if raw.lstrip().startswith("{"):
            blob = json.loads(raw)
            node = blob.get("installed") or blob.get("web") or blob
            client_id = node.get("client_id")
            client_secret = node.get("client_secret")
        else:
            parts = [ln.strip() for ln in raw.splitlines() if ln.strip()]
            if len(parts) < 2:
                print("ERROR: %s needs the client id on line 1 and the secret on line 2."
                      % args.creds_file)
                return 2
            client_id, client_secret = parts[0], parts[1]
    client_id = client_id or os.environ.get("WAKE_GATE_CLIENT_ID")
    client_secret = client_secret or os.environ.get("WAKE_GATE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("ERROR: no client credentials. Give --creds-file pointing at the JSON Google Cloud")
        print("downloaded for you, or set WAKE_GATE_CLIENT_ID / _CLIENT_SECRET.")
        return 2

    args.client_id, args.client_secret = client_id, client_secret

    redirect_uri = "http://127.0.0.1:%d/" % REDIRECT_PORT
    state = secrets.token_urlsafe(16)
    auth_url = AUTH_ENDPOINT + "?" + urllib.parse.urlencode(
        {
            "client_id": args.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
    )

    server = http.server.HTTPServer(("127.0.0.1", REDIRECT_PORT), _CallbackHandler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    print("Opening your browser for Google's consent screen.")
    print("If it does not open, paste this URL into a browser yourself:")
    print(auth_url)
    webbrowser.open(auth_url)

    thread.join(timeout=900)
    server.server_close()

    result = _CallbackHandler.result
    if result.get("error"):
        print("Google returned an error: %s" % result["error"], file=sys.stderr)
        return 1
    code = result.get("code")
    if not code:
        print("Timed out waiting for the browser redirect. Nothing was written.", file=sys.stderr)
        return 1
    if result.get("state") != state:
        print("State mismatch on the redirect; refusing to proceed.", file=sys.stderr)
        return 1

    body = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": args.client_id,
            "client_secret": args.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode("ascii")
    request = urllib.request.Request(TOKEN_ENDPOINT, data=body, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        print(
            "Google did not return a refresh_token. This usually means the account already "
            "granted this client consent before. Revoke access at "
            "https://myaccount.google.com/permissions and re-run this script.",
            file=sys.stderr,
        )
        return 1

    out_path = Path(args.out)
    out_path.write_text(
        json.dumps(
            {
                "client_id": args.client_id,
                "client_secret": args.client_secret,
                "refresh_token": refresh_token,
                "token_uri": TOKEN_ENDPOINT,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    try:
        os.chmod(out_path, 0o600)  # owner-only on Mac/Linux; harmless on Windows
    except OSError:
        pass
    print("Wrote %s" % out_path)
    print("Verify with: python wake_gate.py --config watchers.json --dry-run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
