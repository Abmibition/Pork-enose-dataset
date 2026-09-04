# Baseline conventions for the derived columns

Three columns in this dataset are not sensor readings. They were computed at
preprocessing time from a reading and a *baseline*:

```
nh3_delta    = nh3_ppm  - baseline_nh3
h2s_delta    = h2s_ppm  - baseline_h2s
gas_drop_pct = (baseline_gas - gas_resistance) / baseline_gas * 100
```

The values are genuine — every term on the right-hand side is a real
measurement. The baseline convention differs between recording sessions, so the
three columns are not on a common scale across the whole dataset. This page
records exactly what was used, so the columns can be interpreted or recomputed.

## Why a baseline at all

The BME680 VOC channel reports an absolute resistance that drifts with
temperature, humidity and sensor history. Two identical meat states measured on
different days can differ by tens of percent in absolute resistance. Referencing
each reading to a clean-air value is what makes the feature comparable across
sessions, provided the reference is consistent — which is what the next section
pins down.

## What was actually used

### `nominal_24-28C` — one constant baseline per file, eight distinct values

The preprocessing script picked, for each file, either a session-paired air
recording or a global fallback:

| Strategy | Files | `baseline_src` in `note` | Implied `baseline_gas` |
|---|---|---|---|
| Global fallback: mean steady value over all air recordings | 28 | `global` | **108 187.95 Ω**, identical in all 28 |
| Session-paired: the air recording of the same session | 9 | `session(<prefix>)` | **7 distinct values**, 65 636 – 145 315 Ω |

The nine session-paired files and their baselines:

| File | `session(...)` | Implied `baseline_gas` |
|---|---|---|
| `dynamic_exp_20260517_a_t1h.csv` | `exp_20260517_a` | 65 635.8 Ω |
| `dynamic_exp_20260517_a_t3h.csv` | `exp_20260517_a` | 65 635.8 Ω |
| `dynamic_exp_20260517_c_t1h.csv` | `exp_20260517_c` | 81 432.2 Ω |
| `dynamic_exp_20260517_c_t3h.csv` | `exp_20260517_c` | 81 432.2 Ω |
| `dynamic_air_0517_t0h.csv` | `air_0517` | 101 397.3 Ω |
| `dynamic_air_0517b_t0h.csv` | `air_0517b` | 109 559.9 Ω |
| `dynamic_air_0517c_t0h.csv` | `air_0517c` | 116 728.8 Ω |
| `dynamic_exp_20260508_b_t1p.csv` | `exp_20260508_b_t1p` | 137 247.1 Ω |
| `dynamic_exp_20260517_air.csv` | `exp_20260517` | 145 314.6 Ω |

The `note` column of every frame records which was used, along with the
steady-state values, e.g.:

```
baseline_src=global b_nh3=0.135 steady_nh3=1.25 steady_dnh3=+1.11
```

The baseline is exactly constant within a file — inverting
`baseline_gas = gas_resistance / (1 - gas_drop_pct/100)` returns the same value
on every row of a file, to the last digit. That inversion is independent of the
`note` column, so the two agree as a cross-check rather than by construction.

**Note the consequence:** the session-paired files span 65 636 – 145 315 Ω, a
factor of 2.2, while the other 28 sit on 108 188 Ω. `gas_drop_pct` is therefore
on eight different scales *inside this one subset*, and reaches negative values
(down to −24.3 %) where measured resistance exceeded the global baseline. The
split is not by date: the 8 May and 17 May sessions each contribute files to both
groups.

## Practical guidance

1. **Recompute before pooling across sessions.** `gas_drop_pct`, `nh3_delta` and
   `h2s_delta` map the same physical state to different numbers under different
   conventions, so bring them onto one convention first.
2. **Inside `nominal_24-28C`, handle the nine session-paired files separately**
   or recompute them, unless the method is invariant to a baseline shift. They
   are listed by name in the table above.
3. **The raw columns need none of this.** `nh3_ppm`, `h2s_ppm`, `gas_resistance`,
   `temperature`, `humidity`, `pressure` are direct readings and comparable
   throughout.
4. **To recompute under another convention**, use the air-labelled recordings as
   the reference pool: `air` frames are ambient-air measurements
   with no meat present. Per-file, per-session or global referencing are all
   reconstructible from what ships here.

## Relevance to model evaluation

`gas_drop_pct` is one of the input features of the classifier developed on this
data rather than a diagnostic column. Comparisons of model behaviour across sessions with different baseline
conventions mix a baseline effect into the result; recomputing the derived
columns per-recording removes it.

See also [labels.md](labels.md) for how the labels themselves are defined.
