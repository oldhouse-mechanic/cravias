# How the Brain Works

This is just the ML side of things. If you're here because you said something and CRAVIAS did something completely wrong — yeah, this explains why.

---

## The Short Version

You say something. It gets turned into a pile of numbers. Those numbers get compared against thousands of other numbers. Whichever pile of numbers is closest wins. That's the intent. That's pretty much it.

The slightly longer version is below.

---

## Step 1 — Your Words Become Numbers (TF-IDF)

Before any matching happens, every phrase in the system gets converted into a vector — basically a long list of numbers where each number represents how important a particular word is.

The formula for that importance is called **TF-IDF**:

- **TF** (Term Frequency) — how often a word appears in this phrase
- **IDF** (Inverse Document Frequency) — how rare that word is across *all* phrases

So a word like *"the"* shows up everywhere, gets a low score, barely matters. A word like *"screenshot"* shows up in maybe two or three phrases, gets a high score, matters a lot.

This happens for every example phrase in every intent — there are around 300+ of them across 50+ intents. And it happens for your query too, every single time you speak.

```
you say:  "grab the screen"

becomes:  { "grab": 0.71, "screen": 0.64, "the": 0.02, ... }
```

The vectorizer also looks at pairs and triplets of words (bigrams, trigrams) — so *"scroll down"* is treated as its own thing, not just *"scroll"* and *"down"* separately. This is why saying *"go down the page"* still matches `scroll_down` even though you didn't say scroll.

---

## Step 2 — Finding the Closest Match (Cosine Similarity)

Now it has two vectors — yours, and every example phrase in the system. It needs to find which one is closest.

It does this with **cosine similarity** — which measures the angle between two vectors in high-dimensional space. Angle of 0° means identical. Angle of 90° means completely unrelated.

```
your query vector  →  [0.71, 0.00, 0.64, 0.12, ...]
"grab the screen"  →  [0.68, 0.00, 0.61, 0.09, ...]   similarity: 0.98  ✓
"play some music"  →  [0.00, 0.82, 0.00, 0.44, ...]   similarity: 0.03  ✗
```

It runs this comparison against every single example phrase, then for each intent takes the highest-scoring example as that intent's score. Best intent wins.

---

## Step 3 — Is It Confident Enough?

Winning doesn't mean acting. There's a confidence check first.

```
score ≥ 0.25  →  just do it
score 0.10–0.24  →  ask first ("did you want me to scroll down?")
score < 0.10  →  give up, say something confused
```

The asking-first part is important. Without it, a low-confidence wrong guess would just silently do the wrong thing and you'd have no idea why your browser just closed.

---

## Step 4 — The Learning Loop

This is where it stops being a static model and starts actually adapting to you.

**Correction learning** — say *"no I meant scroll down"* after it does the wrong thing. It re-matches on the corrected phrase, executes the right intent, and then saves the original misunderstood query as a direct mapping to that intent in `data/commands.json`. Next time you say that exact thing, it skips the semantic engine entirely and goes straight to the right answer.

**Phrase teaching** — say *"whenever I say tunes, play music"* and it extracts the alias (*tunes*) and the intent (*play_music*) and saves that mapping directly. No ML involved at that point — it's just a lookup table you've personally written by talking to it.

**Priority order** — every time you say something, it checks in this order:

```
1. learned commands  (your personal lookup table, highest priority)
2. TF-IDF semantic match
3. keyword fallback  (dumb but fast)
4. confused response
```

So over time, the model matters less and less for things you say often. It learns your specific phrasing and stops having to guess.

---

## Why TF-IDF and Not Something Fancier

Sentence transformers and neural embeddings would be more accurate. They'd also pull in PyTorch, 500MB of model weights, and a GPU recommendation. This runs on a potato, fully offline, in about 50MB. The tradeoff is worth it for what this project is.

If the semantic matching ever feels too dumb for something specific, just teach it directly. That'll always beat the model anyway.

---

## Files Involved

`core/brain.py` — the whole thing lives here. `SemanticMatcher` handles the TF-IDF, `KeywordFallback` is the dumb backup, `Brain` is the orchestrator that runs the priority chain and manages the learning loop.

`data/commands.json` — your personal phrase mappings, auto-updated as you correct and teach it.
