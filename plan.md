# PLAN — Building "The Trisolaran Cut"

*How & when. The contract a fresh session executes. **Active build target: the
interactive "Attrition Run" (v2 below)** — see [RESEARCH.md](RESEARCH.md) → "⚑⚑ ACTIVE
REFRAME v2." The static-image build (further down) is retained as the mission-select map's
design reference and a standalone fallback; its **Locked parameters** are reused verbatim
as the verdict-engine inputs.*
*Design (what & why) lives in research.md; this doc is only the build sequence and the
locked parameters. Read research.md first, then follow this.*

---

## Goal (one line, inherited)

One cold log-log scatter that hands the Trisolaran hive the complete field of
**survivable-and-reachable seed targets** at a glance — portfolio logic, one survivor =
survival. *Map all the shots, not the one home.*

---

## ⚑ BUILD DIRECTION v2 — Interactive Attrition Run (active; supersedes static delivery)

*The static-SVG build sequence below is retained as (a) the design reference for the
mission-select map and (b) a valid standalone fallback/export. The **Locked parameters**
below are reused verbatim as the verdict-engine inputs — do not re-derive them.*

### Stack (v2)
- Web app, **stylized 2D** (HTML/CSS/JS; Canvas or SVG/DOM; light or no framework).
- Data **pre-baked to JSON** from `exoplanets.csv` (plotting frame + verdict fields).
- Runs in the browser preview; **no game engine, no 3D.**

### Architecture (layers)
- **Layer 0 — Mission-select map:** the scatter, interactive; click a planet to select.
  Encodings + zone + flags exactly as the Locked parameters below. `⚑` worlds are
  untravelable → not selectable.
- **Layer 1 — Verdict engine (data → outcome), LOCKED:**
  - *Survivable seed?* candidate logic: `pl_rade ≤ 1.8` AND `200 ≤ pl_eqt ≤ 320 K`.
  - *Surface gravity* g = `pl_bmasse ÷ pl_rade²` (Earth units); missing mass → gravity
    unknown = partial verdict, labelled. **Lethal band is a stated modeling assumption,
    not data.**
  - *Thermal* from `pl_eqt` (freeze/boil), with the equilibrium-temp caveat (no atmosphere
    modeled).
  - *Reachable?* missing `sy_dist` → `⚑`, untravelable.
  - *Confidence:* `pl_eqt_computed` → `△` low-confidence verdict; missing temp → `?`.
- **Layer 2 — Attrition loop + log:** select → arrive → volunteer tests → verdict →
  live/die → log entry (verdict, cause, confidence). Finite crew; win = seed ≥1.
- **Layer 3 — Honesty UI (LOCKED, strict):** every verdict cites its column + value; all
  surface visuals watermarked *"artist's impression"*; stability caveat on every
  survivable verdict; blanks shown as unknown, never zero.

### Vertical slice (build FIRST — thinnest honest thing)
Alien mode, **one** selectable planet, the full loop arrive→test→verdict→live/die→log,
with the honesty UI. No human toggle, no full catalog, no polished art. Proves the spine.

### Build sequence — v2 (with gates)
1. **Data → JSON** — bake plotting frame + verdict fields (candidate, size-qualified,
   reach bucket, gravity where mass exists, computed/temp-missing flags). *No UI yet.*
2. **Layer 0 map** — interactive scatter; a planet is selectable.
   - **GATE 0:** map reads (empty corner meaningful) and selection works.
3. **Verdict engine + one-planet loop** — arrive→test→verdict→live/die→log for the slice.
   - **GATE 1 (honesty):** every verdict cites its column+value; visuals labelled;
     stability caveat present; missing data = unknown. Fail → fix *before* adding content.
4. **Slice review** — play one planet end to end: does the death land *and* stay honest?
   Send to user.
5. **Expand (out of slice):** more planets, gravity/journey interactions, then the human
   toggle + NASA voyage.

### Definition of Done — v2 slice
- [ ] Alien mode, one planet, full loop playable in the browser.
- [ ] Verdict computed from real columns; each cites its source value.
- [ ] Survive/die + logging works; log records confidence (`△`/`?`).
- [ ] All surface visuals watermarked impression; stability caveat on survivable verdicts.
- [ ] Both v2 gates passed and noted.

---

## Chosen approach *(static image — now the mission-select map's reference / fallback)*

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
  (opacity/reachability), `pl_eqt_computed` (confidence flag), **`pl_bmasse` (v2:
  surface-gravity interaction)**. All others ignored.

## Verified data profile (2026-09-01, run against `exoplanets.csv`)

*Traceable, not remembered. A fresh session inherits these; do not re-guess.*

- **1,174** worlds. Candidates (seed targets): **exactly 10** — the "Ten" claim is now
  verified. Furnace backdrop: **1,164**. Median world **9.9 R⊕**, **4.6-day** orbit;
  **96.2%** Transit.
- Missingness: `pl_rade` 0%, `pl_eqt` **0%**, `pl_bmasse` **0%**, `pl_orbper` 1.1% (13),
  `sy_dist` 1.5% (18).
- **`?` (size-qualified, temp-unknown) class = 0 members** — because `pl_eqt` is 0% missing
  in this file. Keep the rule as a principled guard; give it legend/UI space *only if* a
  future data cut has members. (The silent-drop gap was real in principle, empty here.)
- Reachability of the 10 candidates: **2 near (≤25 pc), 3 med, 2 far, 3 unreachable (`⚑`)**.
  The 3 unreachable are TRAPPIST-1 c/d/e — and they are *also* the only 3 with computed
  temps (`△`). The least-certain targets are the ones you can't reach.
- Surface gravity (all 10 have mass): **0.62 g … 17.60 g**, median 3.03 g. Kepler-62 f =
  **17.6 g** would crush a volunteer even though the planet is a valid seed on size+temp →
  the honest **seed-viable ≠ personally-survivable** nuance is real in the data.

**Candidate roster (the playable seed targets):**

| Planet | R⊕ | eqt (K) | temp | dist (pc) | gravity | reach |
|---|---|---|---|---|---|---|
| Gliese 12 b | 0.96 | 314.6 | measured | 12.2 | 4.22 g | near |
| LHS 1140 b | 1.73 | 226.0 | measured | 15.0 | 1.87 g | near |
| LP 890-9 c | 1.37 | 272.0 | measured | 32.4 | 13.54 g | med |
| TOI-2095 c | 1.33 | 297.0 | measured | 41.9 | 4.18 g | med |
| K2-3 d | 1.46 | 305.2 | measured | 44.1 | 1.03 g | med |
| Kepler-62 e | 1.61 | 270.0 | measured | 300.9 | 13.89 g | far |
| Kepler-62 f | 1.41 | 208.0 | measured | 300.9 | 17.60 g | far |
| TRAPPIST-1 c | 1.10 | 310.9 | `△` computed | — | 1.09 g | `⚑` unreachable |
| TRAPPIST-1 d | 0.79 | 261.8 | `△` computed | — | 0.62 g | `⚑` unreachable |
| TRAPPIST-1 e | 0.92 | 228.5 | `△` computed | — | 0.82 g | `⚑` unreachable |

---

## Locked parameters (so a fresh session does not guess)

**Survivable Zone** (drawn box; a world is a *candidate* if both hold):
- `pl_rade` ≤ **1.8** Earth-radii  AND  **200** ≤ `pl_eqt` ≤ **320** K
- (This is the ~10-world set found in profiling; label it explicitly as *our inference*.)

**Size-qualified, temperature-unknown** (new class — do *not* bin as furnace):
- `pl_rade` ≤ **1.8** AND `pl_eqt` **missing** → `?` glyph = *size fits, temperature
  never measured.* A live bet the data can't rank on warmth. Shown with the same
  reachability opacity as candidates; never silently dropped (Ground Rule 6: blanks are
  unknown, not zero). This is the honesty fix — a small world with no temp is a bet the
  hive would want *flagged*, not buried in the furnace backdrop.
- **Note (verified 2026-09-01):** this class has **0 members** in the current file
  (`pl_eqt` is 0% missing). Keep the rule as a principled guard; surface it in the
  legend/UI only if a future data cut populates it.

**Reachability → opacity** (by `sy_dist`, parsecs), for candidates **and** size-qualified
worlds:
- ≤ 25 pc → alpha **1.0** (solid, cheap bet)
- > 25 to ≤ 100 pc → alpha **0.6** (medium)
- > 100 pc → alpha **0.3** (faint, costly bet)
- **missing `sy_dist`** → `⚑` glyph, distinct, reduced alpha = **UNREACHABLE / unnavigable**
- (Boundaries are strict at 25 and 100 pc so a world lands in exactly one bucket.)

**Confidence flag:** `pl_eqt_computed == True` → `△` overlay (hollow) = temperature
inferred, lower-confidence bet.

**Glyphs co-render.** `⚑` (unreachable), `△` (computed temp), and `?` (temp-unknown) can
stack on one mark — e.g. a size-qualified world that is also unnavigable renders `? ⚑`.
Glyphs are overlays on the base mark; none suppresses another.

**Furnace field** (everything not a candidate and not size-qualified): single muted mark,
alpha ~0.15, **no flags** — backdrop only.

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

## Workflow patterns in play (the plan-mode toolkit)

This build is deliberately structured around four patterns so a fresh session stays on
the rails:
- **Context Reset** — this doc is the single source; a reset session executes it without
  re-deriving. Locked params exist to survive the reset.
- **CICS** — Clarity (one unambiguous spec per parameter) + Intent (goal + reason stated
  up top, traced to research.md).
- **Happy to Delete** — the Gate-1 rough is *designed to be thrown away*; no sunk cost.
- **Parallel Implementations** — the one non-deterministic step (styling) is harnessed,
  not fought: build **three** variants, then select at Gate 2. Don't chase one "right"
  render; generate variation and pick.

## Build sequence (with gates)

1. **Data-prep script** — load CSV; derive `is_candidate`, `is_size_qualified`
   (size ok + temp missing), `reach_bucket` (strict 25/100 boundaries), `flag_unreachable`,
   `flag_computed`; emit a tidy plotting frame. *No plotting yet.*

2. **GATE 1 — grayscale rough (disposable).** Plot the scatter with zero styling: furnace
   field + zone box + candidate/size-qualified dots. **Question to answer:** does the
   empty corner read as meaningful, and do the ~10 candidates + the four flag types stay
   legible (not cluttered)?
   - Pass → step 3. Fail → revisit zone bounds / flag hierarchy in research.md *before*
     styling. This is the first code and the first real risk checkpoint.
   - *This rough is a probe, not a draft — delete it once the question is answered.*

3. **Parallel styled variants — build THREE from the same frame.** Same locked data and
   encoding rules; each varies only the *aesthetic* choices research left open. Give each
   a distinct thesis so they diverge meaningfully, not randomly:
   - **Variant A — "empty field":** full axis range (no outlier clip), subtle zone box,
     minimal annotation. Lets the void do the persuading.
   - **Variant B — "targeting HUD":** clip extreme-period outliers, bold zone box, dense
     flags + on-image labels. Operational, high-density (leans into hive cognition).
   - **Variant C — "balanced cut":** middle ground — moderate clipping, medium box weight,
     honesty copy foregrounded.
   - All three carry the mandatory honesty line, the `?`/`⚑`/`△` glyphs, and Home anchor.

4. **GATE 2 — select + honesty review.**
   - **Select:** compare the three; pick the winner *or graft* the best elements into a
     final render (this is where the non-determinism pays off).
   - **Honesty checklist** on the winner: stability caveat present; zone labelled as
     *inference*; missing-distance worlds `⚑`-flagged, not dropped; temp-unknown worlds
     `?`-flagged, not buried; computed temps `△`-marked. If any proxy reads as a promise,
     fix copy.

5. **Export & commit** — SVG + PNG to the project; commit with a message noting which
   variant won (or how they were grafted) and both gates passed. Send the image to the
   user for review.

---

## Definition of Done (the artifact)

- [ ] Single static image, cold tone, both axes log.
- [ ] Furnace field muted; ~10 candidates emphasized and countable at a glance.
- [ ] Reachability shown as opacity; `⚑` unreachable, `△` computed, and `?` temp-unknown
      all visible (and legibly stackable).
- [ ] Home anchored; stability-unknown honesty line on the image.
- [ ] Takeaway in the title, not the legend.
- [ ] Three variants built; winner selected/grafted and noted.
- [ ] Both gates passed and noted; SVG+PNG exported; committed.

---

## Risks carried from design (see research.md for full table)

- Stability — the hive's #1 need — is **not in the data**; chart must not imply it.
- "Survivable" bounds are **human** temperature guesses, not Trisolaran biology.
- Missing `sy_dist` = unnavigable; must be flagged, never silently dropped.
- Missing `pl_eqt` on a small world = **silent furnace drop** if untreated; mitigated by
  the `?` size-qualified class (locked above). Blanks are unknown, not disqualifying.
- Clutter vs. quick-decision: mitigated by flags on candidates + size-qualified only
  (furnace stays bare); re-check at Gate 1 now that there are four flag types.

---

## What's next after this artifact (out of scope here)

Deferred sibling pieces only if asked: Story D (the rare temperate worlds as payoff),
Story B (discovery-boom backstory). Not part of this build.
