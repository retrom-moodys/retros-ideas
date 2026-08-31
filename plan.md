# PLAN — Building "The Trisolaran Cut"

*How & when. The contract a fresh session executes to build the single image specified
in [RESEARCH.md](RESEARCH.md) → "⚑ ACTIVE REFRAME — The Trisolaran Cut."*
*Design (what & why) lives in research.md; this doc is only the build sequence and the
locked parameters. Read research.md first, then follow this.*

---

## Goal (one line, inherited)

One cold log-log scatter that hands the Trisolaran hive the complete field of
**survivable-and-reachable seed targets** at a glance — portfolio logic, one survivor =
survival. *Map all the shots, not the one home.*

---

## Chosen approach

- **Stack:** Python + pandas + **matplotlib**, exporting a static **SVG (+ PNG)**.
- **Why:** deliverable is one precise, reproducible static image with a custom cold dark
  theme and hand-drawn annotations (zone box, Home anchor, on-image copy). matplotlib
  gives pixel control and re-runs from the CSV. pandas already profiles this data.
- **Rejected:** D3/Observable web build (interactivity we don't need; heavier; the hive
  reads a static field fine); the `visualize`/widget tools (great for live HTML, but the
  artifact is a static targeting chart, not an interactive page).
- **At build time:** invoke the **`dataviz` skill first** (before any chart code) for
  palette/mark/legend discipline; adapt its guidance to the cold, near-monochrome tone.

---

## Inputs (locked)

- Data: `C:\Users\manishir\Downloads\exoplanets.csv` (1,174 rows, verified clean).
- Dictionary: `exoplanets_data_dictionary.csv` (units confirmed).
- Columns used: `pl_rade` (Y), `pl_orbper` (X), `pl_eqt` (zone test), `sy_dist`
  (opacity/reachability), `pl_eqt_computed` (confidence flag). All others ignored.

---

## Locked parameters (so a fresh session does not guess)

**Survivable Zone** (drawn box; a world is a *candidate* if both hold):
- `pl_rade` ≤ **1.8** Earth-radii  AND  **200** ≤ `pl_eqt` ≤ **320** K
- (This is the ~10-world set found in profiling; label it explicitly as *our inference*.)

**Reachability → opacity** (by `sy_dist`, parsecs), candidates only:
- ≤ 25 pc → alpha **1.0** (solid, cheap bet)
- 25–100 pc → alpha **0.6** (medium)
- > 100 pc → alpha **0.3** (faint, costly bet)
- **missing `sy_dist`** → `⚑` glyph, distinct, reduced alpha = **UNREACHABLE / unnavigable**

**Confidence flag:** `pl_eqt_computed == True` → `△` overlay (hollow) = temperature
inferred, lower-confidence bet.

**Furnace field** (everything not a candidate): single muted mark, alpha ~0.15, **no
flags** — backdrop only.

**Axes:** both log10. X = `pl_orbper` (days). Y = `pl_rade` (Earth-radii). Plain-unit
gridlines labelled (1d, 10d, 100d, 1000d; 1, 11 R⊕ ref lines).

**Anchors & copy (on-image, cold register):**
- `✚ HOME` marker inside the zone region, with note: *its curse is chaos this chart
  cannot show.*
- Mandatory honesty line: *"Stability is unknown for every target. This map finds warmth
  and size — not peace."*
- Title/subtitle carries the takeaway: *"1,174 worlds. Ten within survivable bounds.
  None confirmed stable. Seed all reachable. One survivor is enough."*

**Palette intent:** near-black background; furnaces muted slate; candidates cold
cyan/white; `⚑`/Home in a single warning hue. Finalize against the dataviz skill.

---

## Build sequence (with gates)

1. **Data-prep script** — load CSV; derive `is_candidate`, `reach_bucket`,
   `flag_unreachable`, `flag_computed`; emit a tidy plotting frame. *No plotting yet.*

2. **GATE 1 — grayscale rough.** Plot the scatter with zero styling: furnace field +
   zone box + candidate dots. **Question to answer:** does the empty corner read as
   meaningful, and do the ~10 candidates + flags stay legible (not cluttered)?
   - Pass → step 3. Fail → revisit zone bounds / flag hierarchy in research.md *before*
     styling. This is the first code and the first real risk checkpoint.

3. **Styled image** — apply cold dark theme, opacity encoding, `⚑`/`△` glyphs (candidates
   only), Home anchor, gridline labels, title/subtitle + honesty line.

4. **GATE 2 — honesty review.** Verify on the rendered image: stability caveat present;
   zone labelled as *inference*; missing-distance worlds *flagged, not dropped*;
   computed temps marked. If any proxy reads as a promise, fix copy.

5. **Export & commit** — SVG + PNG to the project; commit with a message noting gates
   passed. Send the image to the user for review.

---

## Definition of Done (the artifact)

- [ ] Single static image, cold tone, both axes log.
- [ ] Furnace field muted; ~10 candidates emphasized and countable at a glance.
- [ ] Reachability shown as opacity; `⚑` unreachable and `△` computed both visible.
- [ ] Home anchored; stability-unknown honesty line on the image.
- [ ] Takeaway in the title, not the legend.
- [ ] Both gates passed and noted; SVG+PNG exported; committed.

---

## Risks carried from design (see research.md for full table)

- Stability — the hive's #1 need — is **not in the data**; chart must not imply it.
- "Survivable" bounds are **human** temperature guesses, not Trisolaran biology.
- Missing `sy_dist` = unnavigable; must be flagged, never silently dropped.
- Clutter vs. quick-decision: mitigated by flags-on-candidates-only (locked above);
  re-check at Gate 1.

---

## What's next after this artifact (out of scope here)

Deferred sibling pieces only if asked: Story D (the rare temperate worlds as payoff),
Story B (discovery-boom backstory). Not part of this build.
