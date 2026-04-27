# Challenges

A ladder for the presentation track. Do them in order. Each builds on the last.

---

## 1. Make it yours

Open `index.html` in a browser. Walk through all 8 slides. Now:

- Pick a topic you could talk about briefly (your team's stack, a recent project, a bug you fixed).
- Replace the title slide's `<h1>` with your topic.
- Replace `Your Logo.` with your name or a placeholder text.
- Replace `yourcompany.com` in the footers.
- Reload the browser. Does it feel like yours?

**What you're learning**: the difference between a generic template and one that looks like you.

---

## 2. Write three slides by hand

Without using an AI, write slides 2, 3, and 4 about your topic. Pick any of the existing layouts. Rules:

- One idea per slide.
- No more than three bullets.
- At least one concrete number, name, or date.

**What you're learning**: how hard it is to write tight slides. This is the baseline you're going to improve on.

---

## 3. Let Claude draft five more

In Claude Code, point it at your file and ask something like:

> Read index.html. Extend the deck to 12 slides about <your topic>. Use a mix of section divider, card grid, big statement, and comparison layouts. Match the existing writing style — one idea per slide, concrete examples.

Review each slide it writes. Reject the weak ones. Rewrite the ones you don't like. Don't accept generic filler.

**What you're learning**: Claude is a first-draft engine. Your taste is what ships.

---

## 4. Add a real image

Pick one two-col slide. Put a real image in `assets/`. Replace the placeholder with:

```html
<div class="col-visual animate-in">
    <img src="assets/your-image.jpg" alt="">
</div>
```

Do the image and the words on that slide reinforce each other? If not, change one of them.

**What you're learning**: images earn their slide or they don't belong.

---

## 5. Retheme

Change the CSS palette. Pick a new primary color (your company's, a favorite movie's, whatever). Update the `:root` variables. Reload.

Everything should retheme consistently because every visual element uses a CSS variable. If something looks off, find the hardcoded hex and fix it.

**What you're learning**: design systems that use variables scale; hardcoded styles don't.

---

## 6. Ship it

Deploy to GitHub Pages or Vercel. Share the URL with someone in the room. Have them navigate on their phone.

```bash
# Fastest: GitHub Pages
git init && git add . && git commit -m "my talk"
gh repo create my-talk --public --source=. --push
# Enable Pages in repo settings → Pages → Deploy from main/root
```

**What you're learning**: the difference between a file on your laptop and something you can send to someone.

---

## 7. Stretch: make a new layout

The starter has 7 built-in layouts. Add an 8th (quote card, stats row, two-image mosaic — pick one). Put it in the CSS, use it on a real slide, keep the nav working.

**What you're learning**: the template is a starting point, not a ceiling.
