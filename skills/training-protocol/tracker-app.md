# Tracker app — single-file, local, daily

A `index.html` you open in the browser (no build, no server) that renders the protocol and **saves progress between sessions**. Optimized to open daily and check off work.

## Storage contract (localStorage shim)

Decouple the UI from storage behind a tiny shim so the same file works whether opened directly or embedded:

```html
<script>
  // Contract: window.storage.get(key) -> { value } | null ;  window.storage.set(key, value)
  window.storage = {
    get(key)        { const v = localStorage.getItem(key); return v === null ? null : { value: v }; },
    set(key, value) { localStorage.setItem(key, String(value)); },
  };
</script>
```

Namespace keys per protocol, e.g. `pq_week`, `pq_completions` (mobility "protocolo de quadril"); `cardio_week`, `cardio_log` for a cardio block. Store completions as a JSON string.

## Structure

- **Weekly plan**: `{ Seg:['A'], Ter:['CARs'], Qua:['B'], ... }` → today's sessions from the current weekday.
- **Today panel**: the day's items with a check/uncheck that persists.
- **Week navigation** (prev/next) + **phase logic** (week N → phase label) + a **reset**.
- **Sessions/reference** rendered from a single JS data object (exercises with dose/equipment/cue/avoid).
- Optional separate **explanations page** for methodology (e.g. what PAILs/RAILs is) so the main view stays clean.

## Hard-won UX lessons (do these by default)

- **Legibility beats beauty for body text.** A display font (e.g. Fraunces) for headers is fine, but exercise **titles and descriptions must be legible** — check size/weight/contrast explicitly across the whole app. A gorgeous low-legibility title is a bug.
- **Cue label wording:** use **"Dica / Foco / Atenção"**, not "Evita".
- **No hover-only content.** Don't make the user hold the mouse to read something important — show it, or put it on the explanations page.
- **YouTube-searchable exercise names** (official or in parentheses).
- **Don't over-clutter.** Replace decorative emoji with restrained icons; align elements; whitespace over density.
- **Single-file export on request:** be able to save a fully self-contained `index.html` to `~/Downloads` (inline all CSS/JS, no external runtime deps; web-font links are fine).
- **Firefox + the user's machine** is the target — verify it actually renders there (the `streamlit-apps` visual-QA idea applies: open it and look).

## Why single-file + localStorage

Local-first, no server, no account, opens instantly in the browser, survives between sessions, and is trivial to back up or hand off. Matches a "open it every day and just do the work" workflow.
