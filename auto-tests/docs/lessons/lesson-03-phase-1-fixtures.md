# Lesson 3 — Phase 1 fixtures (you build this)

**Goal:** pytest can load `ct_qa` + role `dxtf_bot` and open dxTrade5 **without** asserting the CRTQA-1692 login oracle.

**Exit criteria** (from `schema.json` teach_track phase 1): *pytest can load env_profile without product oracle.*

**Blocked until done:** `tests/smoke/test_crtqa_1692.py` (lesson 4).

---

## Why this layer exists

Lesson 1 gave you **who** (`dxtf_bot`). Lesson 2 gave you **what to prove later** (hamburger username). Lesson 3 is **how every future test gets URL + creds + browser** the same way.

Without it, each smoke test would copy-paste:

- `https://ctqa.prosp.devexperts.com/`
- read JSON credentials by hand
- invent its own browser lifecycle

That is what causes “chaos” at test 5+.

---

## Target tree (you create these files)

```
auto-tests/
  requirements.txt          ← step A
  pytest.ini                ← step B
  tests/
    conftest.py             ← step E (fixtures)
    _framework/
      __init__.py           ← step C1
      paths.py              ← step C2
      env.py                ← step C3
      credentials.py        ← step C4
    wiring/
      test_fixtures_load.py ← step F (wiring only)
```

`tests/smoke/` stays empty until lesson 4.

---

## Instrumentation map (what each piece does)

| Piece | Why it exists | What it must NOT do |
|-------|---------------|---------------------|
| `paths.py` | Single source for “where is repo / specs / credentials / tmp” | No test logic |
| `env.py` | Join `schema.json` profile id with `corner-platform-map.json` URLs | No passwords |
| `credentials.py` | Load gitignored overlay; resolve role by id | No URLs |
| `conftest.py` | pytest fixtures = wiring between framework and tests | No CRTQA oracle |
| `wiring/test_*.py` | Prove fixtures work | No login success assertion |
| `requirements.txt` | Pin pytest + Playwright | — |
| `pytest.ini` | `testpaths`, `pythonpath` so imports work | — |

**Fixture chain:**

```
--env-profile ct_qa  →  env_profile  →  application_urls["dxtrade5"]
--smoke-role dxtf_bot →  smoke_role   →  username / password
browser (plugin)     →  context (yours) →  isolated + trace on failure
                      →  page / isolated_page
```

---

## Step A — Dependencies

**Create:** `auto-tests/requirements.txt`

```text
pytest>=8.0
pytest-playwright>=0.5
playwright>=1.40
```

**Install:**

```powershell
cd auto-tests
pip install -r requirements.txt
playwright install chromium
```

**Exercise A1:** Run `pytest --version` and `playwright --version`. Paste both version lines in chat.

---

## Step B — pytest config

**Create:** `auto-tests/pytest.ini`

```ini
[pytest]
testpaths = tests
pythonpath = .
addopts = -ra
```

**Why:** Tests live under `tests/`; imports like `from tests._framework.env import ...` resolve from `auto-tests/` as root.

**Exercise B1:** Run `pytest --collect-only` (expect “no tests collected” or empty — no failures).

---

## Step C — `_framework/` helpers

### C2 — `tests/_framework/paths.py`

**Why:** Avoid `../../../../` in every file; one place to update if layout changes.

```python
from pathlib import Path

AUTO_TESTS_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = AUTO_TESTS_ROOT.parent
SPECS_DIR = AUTO_TESTS_ROOT / "specs"
SCHEMA_PATH = SPECS_DIR / "schema.json"
PLATFORM_MAP_PATH = REPO_ROOT / "docs" / "corner-platform-map.json"
DEFAULT_CREDENTIALS_PATH = AUTO_TESTS_ROOT / "dependencies" / "credentials.local.json"
TMP_DIR = AUTO_TESTS_ROOT / "tmp"
```

**Exercise C2:** In a Python REPL from `auto-tests/`, import `SCHEMA_PATH` and confirm `.is_file()` is True.

### C3 — `tests/_framework/env.py`

**Why:** `schema.json` has profile **ids** and `base_host`; full app URLs live in `docs/corner-platform-map.json`.

Implement:

1. `load_json(path)` — stdlib `json`
2. `resolve_env_profile(profile_id)` — find profile in schema; find matching `environments[]` in platform map; return dict with `id`, `label`, `base_host`, `application_urls`

**Exercise C3:** Call `resolve_env_profile("ct_qa")` in REPL; assert `application_urls["dxtrade5"]` starts with `https://`.

### C4 — `tests/_framework/credentials.py`

**Why:** Centralize “overlay missing” and “unknown role” errors.

Implement:

1. `load_credentials_overlay(path=None)` — default `DEFAULT_CREDENTIALS_PATH`; raise clear `FileNotFoundError` if missing
2. `resolve_role(overlay, role_id)` — return `{"id": role_id, **role_fields}`

**Exercise C4:** Call `resolve_role(overlay, "dxtf_bot")`; confirm `surface == "dxtrade5"` and username is non-empty. **Do not print password to chat.**

### C1 — `tests/_framework/__init__.py`

Empty file or one-line docstring — marks package for imports.

---

## Step E — `tests/conftest.py`

**Why:** Every test gets the same env + role + failure artifacts without copy-paste.

**You need:**

1. **`pytest_addoption`** — `--env-profile` (default `ct_qa`), `--smoke-role` (default `dxtf_bot`)
2. **Session fixtures** — `env_profile`, `credentials_overlay`, `smoke_role`
3. **`artifact_dir`** — `tmp/pytest/` for screenshots/traces
4. **`pytest_runtest_makereport` hook** — so fixtures know if test failed
5. **Wrap `context` fixture** — start Playwright tracing per test; on failure `tracing.stop(path=...zip)`
6. **`isolated_page` fixture** — wrap `page`; on failure save screenshot PNG

**Reference pattern (study, do not paste blindly):**

```python
@pytest.fixture
def context(context, request, artifact_dir):
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield context
    failed = getattr(request.node, "rep_call", None)
    if failed and failed.failed:
        trace_path = artifact_dir / f"{request.node.name}.zip"
        context.tracing.stop(path=str(trace_path))
    else:
        context.tracing.stop()
```

**Exercise E1:** Create only fixtures `env_profile` and `smoke_role` first (no browser). Write a one-line test in `wiring/` that asserts `env_profile["id"] == "ct_qa"`. Run `pytest tests/wiring -v` — 1 passed.

**Exercise E2:** Add `context` + `isolated_page` fixtures. Intentionally fail a dummy test; confirm `tmp/pytest/` gets `.png` and `.zip`.

---

## Step F — Wiring tests (`tests/wiring/test_fixtures_load.py`)

**Why:** Prove phase 1 exit **without** implementing CRTQA-1692.

Write **three** tests:

| Test | Asserts | Must NOT assert |
|------|---------|-----------------|
| `test_env_profile_resolves_ct_qa` | id, base_host, dxtrade5 URL shape | Logged-in UI |
| `test_smoke_role_resolves_dxtf_bot` | role id, surface, username present | Password value |
| `test_dxtrade5_login_surface_reachable` | `page.goto` returns OK; page text hints login (username/password/login) | Hamburger username oracle |

**Exercise F (lesson exit):** Run:

```powershell
pytest tests/wiring -v
```

Paste the summary line (`3 passed` or errors). **Do not** create `tests/smoke/` yet.

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Hardcode `https://ctqa...` in tests | Use `env_profile["application_urls"]["dxtrade5"]` |
| Put password in test file | Only `smoke_role["password"]` at runtime from overlay |
| Wiring test checks hamburger menu | That is lesson 4 oracle — belongs in `tests/smoke/` |
| `ModuleNotFoundError: tests` | Run from `auto-tests/`; check `pytest.ini` `pythonpath = .` |
| Credentials file committed | `git status` — only `example.json` staged |

---

## How to get help in Teach mode

1. Implement one **step** (A–F).
2. Paste **your** file or error output (no secrets).
3. Ask for review — agent reviews, does **not** replace your files unless you say “write the full solution”.

---

## After lesson 3

Update session mentally: phase 1 exit = wiring green. Then lesson 4 — one module `tests/smoke/test_crtqa_1692.py` for the manifest oracle.
