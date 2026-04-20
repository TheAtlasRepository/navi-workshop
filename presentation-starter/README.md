# Presentation starter

A single-file HTML presentation you can clone, theme, and ship. No build step. Works in any browser.

Colors and feel are borrowed from [progit.no](https://progit.no) — change them to match your brand.

## Quick start

```bash
# Preview
open index.html

# Or serve locally (needed for relative image paths)
python3 -m http.server 8000
```

Then **arrow keys** or **space** to navigate. Click the circle buttons bottom-right. Progress bar on top.

## Customize

1. **Your logo** — search the file for `Your Logo.` and replace. Three occurrences.
2. **Your footer** — search for `yourcompany.com`. Eight occurrences (one per slide).
3. **Your brand colors** — edit the CSS variables under `:root`. The starter uses Progit's forest-green scale.
4. **Your font** — replace the `@font-face` blocks in `<head>` and the `font-family` in `html, body`. The starter ships with **ProgitSans** (SIL Open Font License 1.1, © 2020 Tobias Wulvik) in `assets/fonts/`. Keep `assets/fonts/OFL.txt` if you keep the font.
5. **Your content** — each slide is between `<!-- ==========` comments. Write, copy, paste, delete as needed.

## Add a slide

Copy any existing slide block, paste in order, bump the `data-slide="N"` to be sequential. The nav counter updates automatically from the count of `.slide` elements.

See `CLAUDE.md` for the full layout catalog and rules an AI should follow when helping you edit.

## Deploy

**Simplest**: zip the folder, send it. Opens in any browser.

**A bit fancier**: drop into a GitHub Pages repo or Vercel static project — no configuration needed.

```bash
# GitHub Pages
git init && git add . && git commit -m "init"
gh repo create my-talk --public --source=. --push
# Enable Pages on main branch, root directory, in repo settings

# Vercel
vercel deploy --prod
```

## Print to PDF

Chrome → Print → "Save as PDF" → Layout: Landscape. The CSS has a `@media print` block that stacks slides one per page.

## Files

- `index.html` — everything (CSS, slides, JS)
- `CLAUDE.md` — instructions for AI agents working on this file
- `CHALLENGES.md` — workshop practical track
- `assets/` — your images go here
