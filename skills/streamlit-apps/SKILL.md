---
name: streamlit-apps
description: Use when building, debugging, or polishing a Streamlit data app — multipage/tabs, st.session_state, caching, st.fragment, light/dark theming, layout, st.dialog or forms — or when you need to visually verify a rendered Streamlit/web UI with headless-browser screenshots and console-error checks before claiming it works. Covers the Streamlit 1.4x+ API (2025–2026).
---

# Streamlit Apps — production patterns + visual QA

## Overview

Build Streamlit apps that stay fast under heavy compute, and verify them by **looking** at the rendered result instead of guessing. Core principle: **cache the expensive thing once, rerun only what changed, and screenshot every tab/theme before saying it works.**

## When to use

- Building or refactoring a Streamlit app (tabs, pages, sidebar, dashboard "cockpit").
- Performance: the app recomputes a heavy sim/model on every click or widget change.
- Theming: light + dark, tab styling, Material icons.
- The "looks done" trap — you changed UI and need proof it actually renders correctly.

**Not for:** non-Streamlit frontends → use `frontend-design`. Pure modeling/eval → use `senior-data-scientist` or `forecasting-calibration`. Chart design choices → use `dataviz-storytelling`.

## Quick reference (current API)

| Need | Use | Note |
|---|---|---|
| Cache data (DataFrame, API JSON) | `@st.cache_data(ttl=...)` | returns a copy; slice/filter downstream |
| Cache singleton (model, DB, client) | `@st.cache_resource` | **never mutate** the returned object |
| Heavy compute (e.g. 50k Monte Carlo) | cache the function, filter outside it | don't key the cache on user filters → cache explosion |
| Rerun only one block | `@st.fragment` (+ `run_every="10s"`) | escalate with `st.rerun()`; local `st.rerun(scope="fragment")` |
| Conditionally heavy "tab" | `st.segmented_control` + `if` guard | `st.tabs`/`expander`/`popover` run **all** children every time |
| Batch many inputs | `with st.form("x"):` | reruns only on submit, not per keystroke |
| Modal | `@st.dialog("Title", icon=":material/edit:")` | `icon` needs Streamlit ≥1.53; close via `st.rerun()` inside |
| Light + dark (≥1.51) | `[theme.light]` / `[theme.dark]` in `config.toml` | runtime detect: `st.context.theme.type` |
| Icons | `:material/name:` | works in `st.Page`, `st.dialog`, markdown |
| Init state | `st.session_state.setdefault(k, v)` | never assign unconditionally at top of script |
| Multipage | `st.navigation([st.Page(...)])` | don't name a dir `pages/` (collides with old API) |

## Dual light/dark theme

```toml
# .streamlit/config.toml  — BOTH sections unlock the in-app toggle (Streamlit ≥1.51).
[theme]                       # shared defaults
base = "light"
primaryColor = "#2E7D32"

[theme.light]
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F4F6F5"
textColor = "#15140F"

[theme.dark]
backgroundColor = "#15140F"
secondaryBackgroundColor = "#1E1C16"
textColor = "#EDE7D8"
```

```python
mode = st.context.theme.type          # "light" | "dark" (Streamlit ≥1.46) — swap chart palettes/logos
```

Avoid theming via `st.markdown(..., unsafe_allow_html=True)` `<style>` blocks: it fights Streamlit's own styles and breaks silently on upgrades. Use `config.toml`.

## Visual QA — don't trust "it renders"

After any UI change, run the app headless, screenshot **every tab/page in both themes**, and assert **zero console errors**. This is the difference between "compiled" and "works."

**REQUIRED:** follow the pytest + Playwright recipe in `visual-qa.md` — it uses the Streamlit-aware readiness wait (`"Running..."` detaches), a real theme toggle, screenshot-all-tabs, console-error assertion, and clean teardown. **Multipage `st.navigation` apps:** navigate by `url_path` (not tab clicks) and filter the benign `_stcore/*` 404s — both covered in `visual-qa.md`.

## Common mistakes

- **`st.tabs` runs all children** even when hidden → a 50k-sim chart in a tab always runs. Use `st.segmented_control` + `if`.
- **Mutating a `@st.cache_resource` return** (drop a column, append) corrupts it for *all* sessions. Copy first, or use `@st.cache_data`.
- **Unbounded cache:** passing a user filter as the cache key makes one entry per value. Cache the raw data; filter outside.
- **`st.session_state.x = default` unconditionally** resets state every rerun. Guard with `setdefault` / `if k not in st.session_state`.
- **`@st.experimental_fragment`** was removed 2025-01-01 → use `@st.fragment`.
- **Forgetting `--server.fileWatcherType none`** in containers/CI → inotify exhaustion crashes the headless run.
- **Console-error QA false-fails on multipage deep-links:** navigating to a page `url_path` makes Streamlit's `_stcore/health`/`host-config` probes 404 (they resolve only at root). Benign — filter them (see `visual-qa.md`).
