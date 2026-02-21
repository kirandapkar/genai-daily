#!/usr/bin/env bash
# Daily build and push: at 00:00 IST run from launchd/cron.
# Usage: ./daily-build-and-push.sh [--dummy] [--delete-dummy]
#   --dummy: create 00-dummy-test, test, push (for testing the pipeline)
#   --delete-dummy: remove 00-dummy-test and push (run after --dummy test)
#   no args: create next project from project_queue.yaml, test, push

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${ENV_FILE:-$REPO_ROOT/../.cursor/rules/.env}"
cd "$REPO_ROOT"

source_env() {
  if [[ -f "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
  fi
}

push_repo() {
  source_env
  if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "GITHUB_TOKEN not set. Set it in $ENV_FILE or ENV_FILE path."
    exit 1
  fi
  git push "https://kirandapkar:${GITHUB_TOKEN}@github.com/kirandapkar/genai-daily.git" main
}

# --- Dummy project (minimal FastAPI + test) for pipeline testing ---
create_dummy_project() {
  local dir="00-dummy-test"
  mkdir -p "$dir/app" "$dir/tests"
  touch "$dir/app/__init__.py"
  cat > "$dir/app/main.py" << 'PY'
from fastapi import FastAPI
app = FastAPI()
@app.get("/health")
def health(): return {"status": "ok"}
PY
  cat > "$dir/tests/test_api.py" << 'PY'
from fastapi.testclient import TestClient
from app.main import app
def test_health():
    r = TestClient(app).get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
PY
  printf "fastapi>=0.115.0\nuvicorn[standard]>=0.32.0\npytest>=8.0.0\nhttpx>=0.27.0\n" > "$dir/requirements.txt"
  echo "# Dummy test project" > "$dir/README.md"
  printf "__pycache__/\n.venv/\n" > "$dir/.gitignore"
}

run_dummy_tests() {
  local dir="00-dummy-test"
  cd "$REPO_ROOT/$dir"
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -q -r requirements.txt
  PYTHONPATH=. pytest -v
  cd "$REPO_ROOT"
}

delete_dummy_project() {
  git rm -rf --cached 00-dummy-test 2>/dev/null || true
  rm -rf 00-dummy-test
  git add -A
  git status
}

# --- Main ---
if [[ "$1" == "--dummy" ]]; then
  echo "[daily-build] Creating dummy project 00-dummy-test..."
  create_dummy_project
  echo "[daily-build] Running tests..."
  run_dummy_tests
  echo "[daily-build] Committing and pushing..."
  git add 00-dummy-test
  git commit -m "chore: add 00-dummy-test (pipeline test)" || true
  push_repo
  echo "[daily-build] Dummy pushed. Run with --delete-dummy to remove it."
  exit 0
fi

if [[ "$1" == "--delete-dummy" ]]; then
  echo "[daily-build] Removing dummy project..."
  delete_dummy_project
  git commit -m "chore: remove 00-dummy-test after pipeline test" || true
  push_repo
  echo "[daily-build] Dummy removed and pushed."
  exit 0
fi

# Normal run: for now just push any uncommitted changes (real project creation done by Cursor agent)
echo "[daily-build] Ensuring repo is pushed..."
git add -A
if git diff --staged --quiet && git diff --quiet; then
  echo "[daily-build] No changes to push."
else
  git commit -m "chore: daily sync $(date +%Y-%m-%d)" || true
  push_repo
  echo "[daily-build] Pushed."
fi
