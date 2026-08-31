# RESEARCH — Story A: "A Map of Our Blind Spots"

*A design brief for a single visualization about the exoplanets dataset.*
*Dataset: 1,174 confirmed exoplanets (NASA Exoplanet Archive export, 2002–2025).*

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
