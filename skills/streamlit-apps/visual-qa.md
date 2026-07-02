# Visual QA recipe — Streamlit + Playwright

Run the app headless, screenshot every tab in light **and** dark, assert no console errors, tear down cleanly. Adapt the tab labels and port to your app.

## Install once

```bash
pip install pytest pytest-playwright
playwright install chromium
```

## Fixture — launch & teardown (`conftest.py`)

```python
import os, signal, subprocess, time
import pytest, requests

PORT = "8502"
BASE_URL = f"http://localhost:{PORT}"

@pytest.fixture(scope="session", autouse=True)
def streamlit_server():
    """Launch Streamlit headless for the test session, then kill it."""
    proc = subprocess.Popen(
        ["streamlit", "run", "app.py",
         "--server.port", PORT,
         "--server.headless", "true",
         "--server.fileWatcherType", "none",      # no inotify in containers/CI
         "--browser.gatherUsageStats", "false"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        env=os.environ.copy(),
    )
    # Poll until the server answers, instead of a blind sleep.
    for _ in range(60):
        try:
            if requests.get(BASE_URL, timeout=1).status_code == 200:
                break
        except requests.RequestException:
            time.sleep(0.5)
    yield
    proc.send_signal(signal.SIGTERM)
    proc.wait(timeout=10)
```

## Test — screenshot every tab in both themes (`test_visual_qa.py`)

```python
from pathlib import Path
from playwright.sync_api import Page

BASE_URL = "http://localhost:8502"
TABS = ["Panorama", "Jogos & Odds", "Grupos", "Chaveamento", "Hoje"]  # ← your tab labels
SHOTS = Path("screenshots"); SHOTS.mkdir(exist_ok=True)

def wait_ready(page: Page):
    """Streamlit-aware readiness: container present AND the script run finished."""
    page.wait_for_selector("[data-testid='stAppViewContainer']", timeout=30_000)
    # Canonical signal (matches Streamlit's own E2E suite): the app flips to
    # data-test-script-state='notRunning' when the run completes — more robust
    # than watching the "Running..." text, which can flash by on fast reruns.
    page.wait_for_selector("[data-testid='stApp'][data-test-script-state='notRunning']",
                           timeout=60_000, state="attached")

def set_theme(page: Page, theme: str):
    """Toggle light/dark through the real settings menu (exercises actual CSS vars)."""
    page.get_by_test_id("stMainMenu").click()
    page.get_by_text("Settings").click()
    page.get_by_text(theme.capitalize(), exact=True).click()
    page.keyboard.press("Escape")
    wait_ready(page)

def shoot_all_tabs(page: Page, suffix: str):
    for label in TABS:
        page.get_by_role("tab", name=label).click()
        wait_ready(page)
        page.mouse.move(0, 0)                      # kill hover artifacts before capture
        page.screenshot(path=str(SHOTS / f"{label}-{suffix}.png".replace(" ", "_")),
                        full_page=True)

def test_light(page: Page):
    page.goto(BASE_URL); wait_ready(page)
    shoot_all_tabs(page, "light")

def test_dark(page: Page):
    page.goto(BASE_URL); wait_ready(page)
    set_theme(page, "dark")
    shoot_all_tabs(page, "dark")

def test_no_console_errors(page: Page):
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto(BASE_URL); wait_ready(page)
    assert errors == [], f"Console errors: {errors}"
```

## Run

```bash
pytest test_visual_qa.py -v --browser chromium
# then open screenshots/ and actually look at the PNGs
```

## Why these specific moves

- **Poll, don't sleep:** a blind `time.sleep(5)` is flaky on cold starts and wasteful when warm. Poll the port.
- **`stApp[data-test-script-state='notRunning']` is the real readiness signal** — `networkidle` fires too early on Streamlit's websocket app, and the `"Running..."` text can flash by on a fast rerun; the script-state attribute is what Streamlit's own E2E suite waits on.
- **Toggle theme via the menu**, not a query-param hack — it exercises the same `[theme.dark]` CSS variables your users see.
- **`page.mouse.move(0,0)`** before each shot removes stray hover/tooltip state that makes diffs noisy.
- **Console-error assertion** catches the silent JS failures (bad chart spec, missing asset) that a screenshot alone can miss.

## Ephemeral test data

When a view needs results that don't exist yet (e.g. a played match), inject a **temporary** fixture, screenshot, then revert with `git checkout`/file delete before committing — never leave fake data in the repo.
