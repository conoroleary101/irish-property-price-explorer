import hmac
import os
import subprocess
from pathlib import Path

from flask import Blueprint, abort, request

bp = Blueprint("deploy", __name__)

REPO_DIR = Path(__file__).resolve().parents[1]


@bp.route("/deploy", methods=["POST"])
def deploy():
    secret = os.environ.get("DEPLOY_SECRET")
    sent = request.headers.get("X-Deploy-Token", "")
    if not secret or not hmac.compare_digest(sent, secret):
        abort(403)

    pull = subprocess.run(
        ["git", "pull", "--ff-only", "origin", "main"],
        cwd=REPO_DIR, capture_output=True, text=True, timeout=120,
    )
    if pull.returncode != 0:
        return {"ok": False, "step": "git pull", "output": pull.stderr}, 500

    wsgi_file = os.environ.get("WSGI_FILE")
    if not wsgi_file:
        return {"ok": False, "step": "reload", "output": "WSGI_FILE not set"}, 500
    Path(wsgi_file).touch()

    return {"ok": True, "step": "done", "output": pull.stdout}