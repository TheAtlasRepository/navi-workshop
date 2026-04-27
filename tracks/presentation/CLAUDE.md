# Presentation starter — Claude instructions

When asked to work on this presentation, follow this file.

## File layout

- `index.html` — the entire presentation. CSS, slide content, and nav script are all inline. One file, no build step.
- `assets/` — images go here. Reference as `assets/<name>`.
- `assets/fonts/` — ProgitSans (SIL OFL 1.1, © 2020 Tobias Wulvik). Keep `OFL.txt` if you ship the font. Don't rename the font files — @font-face references them by name.
- `assets/images/` — Progit marketing photos (workplace, portraits, iPad/keyboard animations). Use as `assets/images/<name>`.
- `README.md` — human-facing setup and deploy instructions.
- `CHALLENGES.md` — the workshop practical track.

## How to add a slide

1. Copy one of the 8 existing slides as a template (they're fenced with `<!-- ==========` comments).
2. Paste it in order inside `<div class="slides-container">`.
3. Increment `data-slide="N"` so numbers are sequential.
4. Write the content. Keep text tight — one idea per slide.
5. Don't touch the nav script. It counts slides automatically.

## Available layouts

| Layout | Class | Use for |
|---|---|---|
| Title (hero) | `layout-title` | Opening slide |
| Section divider (dark) | `layout-divider` | Transitions between parts |
| Two-column | *(none — uses `.two-col`)* | Text + image |
| Big statement | `layout-statement` | One powerful claim |
| Card grid (3x) | *(uses `.card-grid`)* | 3 concepts side by side |
| Comparison | *(uses `.compare`)* | Before/after, old/new |
| Code block | *(uses `pre.code`)* | Technical content |
| Summary/CTA | `layout-summary` | Closing with action items |

## Color palette (Progit-inspired)

Use CSS variables. Don't hardcode hex.

```
--color-primary-100: #f7fceb   pale mint (subtle bg)
--color-primary-200: #ddecd3   light mint (card bg)
--color-primary-300: #afc3ae   sage (borders)
--color-primary-500: #2f4949   mid teal (subheading text)
--color-primary-600: #1b3436   deep teal (primary)
--color-primary-700: #103031   near-black teal (dividers)
--color-primary-800: #0d2026   very dark (code bg)

--accent-warm: #dd7655         salmon — use sparingly
--accent-hot:  #f99c00         orange — use more sparingly
```

**Rule**: dark teals for structure, pale mint for soft backgrounds, one warm accent max per slide. Progit's feel is minimalist Scandinavian — lots of whitespace, restrained accents.

## Writing style

- One idea per slide.
- Tight headlines (3–8 words).
- Replace abstract bullets with concrete numbers or examples.
- Speaker notes go in HTML comments above each slide, not on the slide.

## Typography hybrid — Mixed + Regular

Body text is **ProgitSans Regular**. For titles, emphasize a single word or phrase with **`<span class="mixed">…</span>`** — this swaps to ProgitSans Mixed (a visually distinctive variant). Examples already in the deck:

```html
<h1>Your <span class="mixed">topic</span><br>goes here.</h1>
<h1>Part 1 · <span class="mixed">The problem</span></h1>
<h1>The <span class="mixed">single most important</span> claim of your whole talk.</h1>
```

Rule: one emphasized span per title. Two starts to feel noisy. Don't wrap whole headlines in Mixed — that's what progit.no does, but for a slide at this size it's too much.

**Don't use `ProgitSans Plants` for titles.** It's a decorative alphabet meant for single-letter accents (e.g., fancy bullets), not reading. No punctuation glyphs either.

## What not to change

- The `<script>` at the bottom — the nav logic reads `data-slide` and counts.
- The `.progress` bar.
- The keyboard handler (arrow keys + space).

## Preview

```bash
# Simplest way:
open index.html

# If you want a proper server (for relative assets):
python3 -m http.server 8000
# then http://localhost:8000
```

## Before shipping

- Replace `Your Logo.` everywhere (search for "Your Logo").
- Replace `yourcompany.com` in every slide footer.
- Update the `<title>` tag at the top of the file.
- Put real images in `assets/` and replace the placeholder `.col-visual` divs.
