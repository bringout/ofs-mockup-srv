# Repository Guidelines

## Project Structure & Module Organization
- `ofs_mockup_srv/`: FastAPI app (`main.py`) and package code.
- `scripts/`: local helper scripts.
- `doc/`: design notes and API docs.
- `patches/`: development env patches (e.g., Nix).
- Tests live in `tests/` mirroring package paths (e.g., `tests/test_status.py`).

## Build, Test, and Development Commands
```bash
# Setup (dev)
pip install -e .[dev]

# Run locally
ofs-mockup-srv
python -m ofs_mockup_srv.main
uvicorn ofs_mockup_srv.main:app --reload --port 8200

# Tests
pytest
pytest --cov=ofs_mockup_srv  # coverage

# Quality
black ofs_mockup_srv/ && isort ofs_mockup_srv/
flake8 ofs_mockup_srv/ && mypy ofs_mockup_srv/
```
Each command maps to tools configured in `pyproject.toml`.

Or via Makefile:
```bash
make install-dev
make run-unavailable PORT=8200
make test
make demo        # runs both PIN and invoice flows
make demo-pin    # PIN-only flow
make demo-invoice
```

## Mock Controls & CLI
- `POST /mock/lock` (Bearer): set service unavailable (HTTP 404 from /api/attention), reset fail counter.
- `POST /api/pin` (text/plain): correct PIN → `0100` and service available (HTTP 200); 3 wrong 4‑digit attempts lock to unavailable (HTTP 404, PIN ignored afterwards).
- `GET /api/attention` (Bearer): returns HTTP 200 (available) or 404 (unavailable).
- Start options: `ofs-mockup-srv --unavailable --port 8200`.

## Monorepo/Subproject Notes
- This package lives under `packages/bringout-ofs-mockup-srv/` in the parent repo.
- Run all commands from this directory; avoid assuming root-level tooling.
- Publishable name is `bringout-ofs-mockup-srv` (see `pyproject.toml`).

## Coding Style & Naming Conventions
- Python ≥ 3.10. Format with Black (line length 88) and isort (Black profile).
- Lint with Flake8; type-check with mypy (no untyped defs).
- Names: `snake_case` for functions/vars, `CamelCase` for classes/Pydantic models, `UPPER_SNAKE_CASE` for constants.
- Modules/files use short, descriptive `snake_case` (e.g., `status_api.py`).

## Testing Guidelines
- Frameworks: `pytest`, `pytest-asyncio`, `httpx` for async client tests.
- Place tests under `tests/`; name files `test_*.py`; use clear, behavior-driven names.
- Aim for meaningful coverage on endpoints, error paths, and auth (API key).
- Example: start app via `from ofs_mockup_srv.main import app` and test with `httpx.AsyncClient`.

## Commit & Pull Request Guidelines
- Prefer Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- Subject in imperative mood, ≤72 chars; include scope when useful.
- PRs: clear description, linked issues, rationale, testing notes, and API changes (with sample requests if applicable).
- Include before/after behavior and screenshots only if UI is involved.

## Security & Configuration Tips
- Default API key and PIN live in `ofs_mockup_srv/main.py` for local use; do not commit real secrets.
- Prefer env vars or config injection for deployments; document changes in `doc/`.
- Default dev port is `8200`. Validate auth on every endpoint in tests.

## Diagrams
- See `doc/SEQUENCES.md` for Mermaid sequence diagrams of PIN, lockout, and init flows.
