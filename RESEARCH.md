# RESEARCH — Story A: "A Map of Our Blind Spots"

*A design brief for a single visualization about the exoplanets dataset.*
*Dataset: 1,174 confirmed exoplanets (NASA Exoplanet Archive export, 2002–2025).*

---

# ⚑ ACTIVE REFRAME — "The Trisolaran Cut"

*The audience is no longer human. This section overrides Goal, Audience, Hypothesis,
Tone, and Risks below. The visualization mechanics and Key Columns (further down) are
inherited unchanged except where noted. The original human framing is retained beneath
for provenance — see "Why Story A".*

**One image. Cold tone. Maximum honesty. Built for instant decisions.**

## Audience — the Trisolaran fleet

A hive-mind civilization fleeing a chaotic three-body star system. Design implications,
in order of consequence:

- **Collective survival rule: one surviving member = the civilization survives.** This
  is the master constraint. It makes the fleet **risk-seeking and portfolio-driven** —
  the goal is to maximize the *number of independent survivable bets*, not the safety of
  any single one. Even a marginal, low-odds world is worth a seed when you need only one
  to land.
- **Hive cognition:** perceives the whole decision surface in parallel. Wants **density
  and completeness, not narrative pacing or simplification.** No hand-holding.
- **Native masters of orbital mechanics; chaos is their ancestral trauma.** Do not
  explain the physics. Their hierarchy of desire: *stability → survivable conditions →
  reachability.*
- **Cold, unsentimental, deterministic.** This is a targeting solution, not a brochure.

## Goal (reframed)

Give the collective, in one cold glance, the **complete field of seed targets** — every
world with any survivable-and-reachable value — so it can disperse across as many
independent bets as possible. *Not "find the one home." Map all the shots.*

**Success looks like:** the hive can, at a glance, count and locate every viable target
and rank each by cost (distance) and certainty (confidence flags) — then seed them all.

## Hypothesis (same data shape, opposite valence, hardened)

> The catalog is overwhelmingly furnaces — gas giants and heat. Genuinely survivable
> worlds are few (~10 small + temperate) and cluster in the faint, hard-to-confirm
> corner. For a portfolio-survival strategist this means viable targets are scarce and
> mostly marginal — so **every reachable candidate matters, and the fleet must bet
> wide.** The empty corner is not humility (the human reading); it is the arithmetic of
> desperation.

## Tone

Cold, operational, deterministic. The takeaway lives in the words, e.g.:
> *"1,174 worlds. Ten within survivable bounds. None confirmed stable. Seed all
> reachable. One survivor is enough."*

## Design changes vs. the human cut (still Concept 1, one scatter)

| Element | Change |
|---|---|
| **Reference anchor** | *Home* (the dying three-body world) replaces Earth & Jupiter. |
| **Survivable Zone** | Drawn target box (small radius + temperate-enough `pl_eqt`). Labeled explicitly as **our inference**, not Trisolaran biology. |
| **Distance → opacity** | Solid = near = cheap bet; faint = far = costly bet. A *cost cue, not a filter* — the hive seeds faint targets too. |
| **Confidence flag `△`** | Marks worlds where `pl_eqt_computed = True` — temperature inferred, not measured = lower-confidence bet. (Re-introduces a column cut for humans.) |
| **Reachability flag `⚑`** | Marks worlds with missing `sy_dist` — **cannot be navigated to.** Flagged, never silently dropped. |
| **Every dot near the zone** | Is a candidate seed target, not just the "best" few — portfolio logic. |

## Risks (honesty for lethal-stakes, hive-mind bets)

| Risk | Why it matters here | Mitigation |
|---|---|---|
| **Stability is not in the data** | It's the aliens' #1 criterion — three-body chaos is their trauma — and the chart cannot certify a stable orbit. | State on the image: *"Stability is unknown for every target. This map finds warmth and size — not peace."* Single-star host is at best a weak proxy; do not imply more. |
| **"Survivable" uses human water-life bounds** | Trisolaran tolerance differs and is unknown; the box may mis-serve them. | Label the zone as *our* temperature guess, not their limit. Widen/annotate as uncertain. |
| **Missing `sy_dist` = unnavigable** | A target you can't reach is no target; TRAPPIST-1 (a prime candidate) has no distance in this file. | `⚑` flag on-chart; never drop silently. |
| **Computed temps are inferred** | Portfolio bets must be weighted by certainty. | `△` flag on `pl_eqt_computed = True`. |
| **Portfolio logic tempts "seed everything"** | The chart must not imply reachability the data can't support (no fuel/time model). | Opacity shows cost honestly; the directive says *reachable*, not *all*. |
| **Home cannot be plotted truthfully** | Home might sit inside the size/temp box yet be uninhabitable — its curse is chaos the chart can't render. | Anchor Home with an explicit note that its problem is stability, invisible here. |

## Text diagram — Trisolaran cut (layout intent)

```
  RADIUS
  (log)              ← FURNACES: DO NOT SEED →
   ▲
34 │          · ·▓▓▓▓▓▓▓▓▓▓▓· ·           1,164 worlds:
   │       · ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ·          gas · heat · death
11 ┤· · · · ·▓▓▓▓▓▓▓▓▓▓▓▓▓▓· · · · · · · · · · · · ·
   │        ▓▓▓▓▓▓▓▓▓▓▓▓▓
   │         ▓▓▓▓▓▓▓
   │          ▓▓▓
   │     ┌────────────────────────────┐
 2 ┤     │  SURVIVABLE ZONE (inferred) │  seed targets, n≈10
   │     │   ○  ●   ○      ●   ○       │  ● near = cheap bet
   │     │        ●          ○         │  ○ far  = costly bet
 1 ┤· · ·│· ●· · · · · · · · · · ·     │  ⚑ no distance = UNREACHABLE
   │     │  ⚑           △              │  △ temp computed = low confidence
0.3│     └────────────────────────────┘
   └──────────────────────────────────────────▶
      0.3d     1d     10d    100d   1000d+     ORBITAL PERIOD (log)
      ← closer / cheaper to reach        farther →

  ✚ HOME (three-body): would plot inside the zone — but its curse is CHAOS,
    which this chart cannot show. STABILITY IS UNKNOWN FOR EVERY TARGET.
    This map finds warmth and size — not peace.

  DIRECTIVE: Seed every reachable target. One survivor = the civilization survives.
```

---

## ⚑⚑ ACTIVE REFRAME v2 — "The Attrition Run" (interactive)

*Supersedes the delivery **medium** of the Trisolaran Cut, not its logic. The static
scatter above is retained as the **mission-select map** (Layer 0); this section adds the
interactive drill-down. Audience-as-alien, portfolio-survival logic, and every honesty
rule are inherited unchanged and made **stricter** — an interactive sim can imply far more
than a static chart, so the guardrails tighten.*

**One line:** turn the target map into a played decision — you are the alien
representative spending a finite crew to find seed worlds; each planet you test returns a
verdict computed from real data, and a volunteer lives or dies on that verdict.

### The two readings (toggle) — same numbers, opposite valence
- **Alien (built first):** the attrition run — spend volunteers, watch the feed, log the
  field of survivable bets. The emotional + data core.
- **Human (deferred):** the NASA voyage — liftoff, astronaut-scientist narration, framed
  as helping the fleet find home. Warmer, more invented content; specced later.

### Core loop (alien, per planet)
1. **Select** a target from the mission-select map. Missing-`sy_dist` worlds are `⚑` — you
   cannot travel there; they can't be selected, only mourned.
2. **Arrive** — a volunteer steps out to test conditions; you watch a video feed.
3. **Verdict** — computed live from the data: survivable → the volunteer lives and the
   world is logged as a seed target; lethal → the feed cuts out, the volunteer dies, cause
   logged.
4. **Log** — record the finding and its confidence (`△` computed temp = low confidence).
   The accumulating log *is* the "complete field of seed targets" the static chart showed
   at a glance — now earned one death at a time.
5. **Resource** — crew is finite. Win = seed ≥1 survivable world before the crew runs out.
   *One survivor is enough.* Portfolio logic: bet wide, spend to learn.

### What is real vs. what is impression (STRICT — the ground-rule spine)
- **Real, drives verdicts:** survivability (size+temp candidate logic), surface gravity
  (`pl_bmasse ÷ pl_rade²`), freeze/boil (`pl_eqt`), reachability + confidence flags.
- **Impression, drives nothing:** surface visuals, sky, terrain, atmosphere, "elements,"
  crew faces — all watermarked *"ARTIST'S IMPRESSION — not from data."*
- **Modeling assumption, labelled as such:** the lethal-gravity band (data gives gravity;
  the human survivability threshold is our guess, like the temperature zone).
- **Always on screen:** every verdict cites the column + value that produced it; the
  stability caveat persists on *every* survivable verdict (*"tests warmth, size, gravity —
  not orbital peace; stability is unknown."*). Blanks are unknown, never zero.

### Why this is honest storytelling, not a game with a data skin
Each death is a real verdict from the catalog's own columns; the sim dramatizes the
*consequence* of the numbers, never the numbers themselves. The player does what the
dataset's authors did — observe, record, mark confidence.

---

## Why Story A

Of the candidate stories, "A Map of Our Blind Spots" wins on the three things that
matter most for a single-image piece:

1. **It's surprising but true.** The counterintuitive claim — *the typical known
   planet tells you about our telescopes, not the galaxy* — lands immediately and
   reframes what the viewer thought they were looking at. Surprise is what earns a
   second look.
2. **It's defensible.** The pattern rests on the dataset's own strongest, least-gappy
   columns (radius, orbital period, discovery method — all <1.1% missing) and on an
   effect so large it needs no statistics to see: the median planet is Jupiter-sized
   with a 5-day year. There is no overclaim risk the way there is with "habitability"
   (Story D) or the bias-sensitive radius valley (Story C).
3. **It resolves to one clean image.** Two axes carry the entire argument, and the
   *empty* region does the persuading. You don't need annotations to feel it.

Just as important, A is the **foundation for the others**. Once a viewer accepts that
this is a map of detectability, the rare temperate worlds (D) become the emotional
payoff and the discovery timeline (B) becomes the backstory. A earns the right to tell
the rest.

---

## Goal

Make a general audience *feel*, in one image, that this catalog is a **portrait of our
detection method — not a census of planets**. The viewer should leave understanding
that big, hot, close-in planets dominate the data because they are the *easiest to
find*, and that the near-empty "Earth-like" corner reflects a blind spot, not an
absence of such worlds.

**Success looks like:** a viewer who, unprompted, says some version of *"oh — we're
only seeing the easy ones."*

---

## Audience

**Primary:** curious, educated general public — science-explainer, museum-panel, or
newsroom-graphic readers. No astrophysics assumed.

**Needs:**
- Reference anchors they already know (Earth, Jupiter) to make sense of the axes.
- The takeaway stated in plain language, not left implicit.
- A short, honest note that we can't chart what we've never found.

**Not for:** domain astronomers (they know this and would want detection-efficiency
corrections we can't provide) — see Risks.

---

## Hypothesis

> Known exoplanets cluster overwhelmingly into **large radius + short orbital period**
> — the regime the transit method detects most easily — leaving a conspicuous void
> where small, Earth-like, wider-orbit planets would sit. The shape of the data is the
> shape of our detection bias.

**Evidence already in hand (from profiling):**
- Median radius **9.9 Earth-radii** (near Jupiter); only **62 of 1,174** planets are
  truly terrestrial (<1.25 R⊕).
- Median orbital period **4.6 days** — a "year" shorter than a work week.
- **96%** of planets found by **Transit**, the method most biased toward big, close-in
  worlds.

---

## Visualization choice

**A single scatter plot** — one dot per planet.

| Encoding | Field | Why |
|---|---|---|
| **X axis** | `pl_orbper` (orbital period), **log scale** | "Closeness" — spans 0.24 to 8M days; log is mandatory |
| **Y axis** | `pl_rade` (planet radius), **log scale** | "Size" — spans 0.3 to 34 Earth-radii; log is mandatory |
| **Color** | `discoverymethod` | Reveals that the dense cluster is one method (Transit) |
| **Reference marks** | Earth & Jupiter as labeled points/lines | Turns abstract axes into intuition |
| **Annotation** | Callout on the empty lower-right | Names the blind spot explicitly |

**Why a scatter, and why these axes:** the two bias directions — *big* and *close* —
are the two axes, so the clustering and the void appear together in one glance. The
persuasive element is the **absence** in the corner where small, wide-orbit planets
belong; a scatter is the only form that makes an empty region legible as meaning. Log
scales aren't a stylistic choice — the quantities span 4–7 orders of magnitude and
would collapse to an unreadable smear on linear axes.

**Rejected alternatives:** a histogram (shows one variable, loses the joint pattern);
a bar chart of methods (states the bias as a number instead of letting the viewer
*see* it); a time series (that's Story B).

---

## Key columns

**Used:**
- `pl_rade` — planet radius, Earth-radii (0% missing) — Y axis
- `pl_orbper` — orbital period, days (1.1% missing) — X axis
- `discoverymethod` — detection method (0% missing) — color

**Deliberately left out:**
- `pl_bmasse` (mass) — ~0.86 correlated with radius here; redundant, adds no new axis.
- `pl_eqt` (temperature) — tempting for color, but doubles the message; keep it to
  method. Could be a *secondary* version.
- `ra` / `dec` (sky position) — irrelevant to a size-vs-orbit story.
- `st_met` (metallicity) — the gappiest column (7.4%) and off-topic.
- Everything host-star (`st_teff`, `st_rad`, `st_mass`) — about stars, not the bias.

**What the chart itself cannot show (state this):** the planets we've *never detected*.
The empty corner is inferred from absence — it is the point, but it must be named as
inference, not measurement.

---

## Text diagram (layout intent)

```
  RADIUS
 (Earth = 1, log scale)
   ▲
34 │                    ● ● ●●
   │            ● ●●● ●●●●●●●●●● ●        ← JOVIAN WORLDS pile up:
   │        ●●●●●●●●●●●●●●●●●●●●●● ●         big + close = easy transits
11 ┤· · · · ·●·●●●●●●●●●●●●●●●·●· · · · · · ·  Jupiter
   │       ●● ●●●●●●●●●●●●●● ●●●
   │      ●  ●●●●●●●●●●●● ●●
   │        ● ●●●●●●●● ●
   │          ●●●●● ●                        (dense cluster,
   │         ● ●● ●                           mostly ONE color
   │        ● ● ●                             = Transit)
 1 ┤· · · ·●·●· · · · · · · · · · · · · · · ·  Earth
   │      ·                    ┌───────────────────────┐
   │                          │   THE BLIND SPOT        │
   │       (nearly empty)     │  small + wide orbit =   │
   │                          │  where "Earth-like"     │
0.3│                          │  worlds would be —      │
   │                          │  but we can't see them  │
   └──────────────────────────└───────────────────────┘──▶
     0.3d      1d      10d      100d     1000d    10000d+
                     ORBITAL PERIOD (log scale)
                     ←— closer to star        farther —→

  Legend:  ● Transit (96%)   ○ Radial Velocity   ◆ Imaging   ▪ other

  Reading guide (on-chart text):
   • Top-left blob  = "the easy ones" — big planets whipping around fast
   • Earth & Jupiter dotted lines = your intuition anchors
   • Empty lower-right = the blind spot; absence is the message
```

---

## Risks & mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| **Overreading absence** — viewer thinks Earth-likes are *rare*, not *hard to see* | Inverts the whole point | Explicit caption: "empty ≠ rare; empty = hard to detect." Frame the corner as *our* limit. |
| **Survivorship framing missing** — chart shows only detections | A pro would ask for detection-efficiency correction | State plainly this is a *raw catalog*, a portrait of the method, not a debiased census. Don't imply otherwise. |
| **Log-scale confusion** — general audience misreads spacing | Distorts perceived distances | Label a few gridlines in plain units ("1 day", "10 years"); add the ←closer / farther→ guide. |
| **Color near-meaningless** — 96% one method | A single-color blob undercuts the color encoding | Lean into it: the monochrome cluster *is* evidence ("almost all one method"). Keep the few non-Transit points visible as contrast. |
| **Outlier compression** — an 8M-day period stretches the axis | Wastes canvas, flattens the cluster | Consider clipping/annotating extreme outliers rather than letting them set the range. |
| **"So what" for lay viewer** — pattern seen but meaning missed | Chart fails its goal | Hard-code the takeaway in a title/subtitle, not just a legend: *"We've mostly found the easy ones."* |

---

## What's next

1. **Rough the scatter** (grayscale, no polish) — the one question to answer first:
   *does the empty corner actually read as empty to someone who doesn't know what
   belongs there?* If absence isn't legible, the whole story fails and we pivot.
2. **Pressure-test axis handling** — decide how to treat the 8M-day outlier (clip vs.
   annotate) and which gridlines get plain-language labels.
3. **Draft the title/subtitle** — the takeaway must live in the words, not the legend.
   Candidate: *"We've mostly found the easy ones."*
4. **Decide on the color payoff** — confirm the near-monochrome cluster is framed as
   evidence, not a bug.
5. *Then, and only then,* move to build. Everything above is still design.

Deferred (possible follow-on pieces, not this image): Story D as the emotional payoff,
Story B as the backstory — see the trade-off table in prior analysis.

---

## One-line summary

**A single log-log scatter of size vs. orbit, colored by method, that turns an empty
corner into the whole argument: this is a map of what we can find, not what's out
there.**
