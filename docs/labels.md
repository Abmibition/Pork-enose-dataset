# Labels: definition, calibration, provenance

## The rule

The `time_label` column holds one of four classes. It was assigned by a
preprocessing script that thresholds the **steady-state ammonia concentration**
of each recording, defined as the mean of `nh3_ppm` over the final 10 s of the
recording:

| Steady-state NH₃ | Label | Intended meaning |
|---|---|---|
| < 1.0 ppm | `air` | ambient air, no meat present (device zero reference) |
| 1.0 – 4.0 ppm | `fresh` | acceptable, intended to correspond to TVB-N ≤ 15 mg/100 g |
| 4.0 – 5.5 ppm | `early_spoilage` | intended to correspond to TVB-N 15–25 mg/100 g |
| ≥ 5.5 ppm | `spoiled` | intended to correspond to TVB-N > 25 mg/100 g |

The label may vary within a file.

## Relationship between labels and features

Applying one deterministic rule to every recording makes the labelling
reproducible and removes annotator subjectivity. It also means the label shares a
source with `nh3_ppm` and its derivative `nh3_delta`, both of which are model
input features.

Evaluation designs on this dataset are best chosen with that in mind. A
classifier that re-thresholds ammonia will approach full agreement with the
labels, so plain accuracy and macro-F1 mainly measure agreement with the rule.
Protocols that stay informative include: leave-one-recording-out, evaluation on
feature subsets that exclude ammonia, reporting the direction of
misclassifications alongside the rate, and validation against an external
reference method.

## Threshold calibration

The ppm thresholds are empirical values for this project's ZE03 readings,
anchored to colourimetric TVB-N measurements made on 17 May 2026:

| Measured NH₃ | Measured TVB-N | Class implication |
|---|---|---|
| 3.9 ppm | ≈ 12 mg/100 g | within `fresh` |
| 5.0 – 5.7 ppm | ≈ 25 mg/100 g | `early_spoilage` / `spoiled` boundary |

NH₃ in ppm and TVB-N in mg/100 g are not related by a strict conversion, so the
thresholds are stated in ppm as applied.

The dataset does not include a paired laboratory TVB-N determination for each
individual recording; work requiring per-sample reference chemistry should treat
these labels as rule-derived proxies.

## Relation to GB 2707-2016

GB 2707-2016 (fresh and frozen livestock and poultry meat) specifies a **two-way**
criterion on TVB-N: ≤ 15 mg/100 g acceptable, > 15 mg/100 g not acceptable. It
does not define a three-tier freshness scale.

The three meat tiers used here (`fresh` / `early_spoilage` / `spoiled`) come from
food-science literature ranges, not from the standard. The accurate description of
this label scheme is therefore: *a three-tier grading based on GB 2707-2016
together with food-science literature ranges, plus an air baseline class.*
NH₃ in ppm and TVB-N in mg/100 g are not related by a strict conversion; the ppm
thresholds are empirical values back-derived from this project's ZE03 readings.

Note in particular that anything labelled `early_spoilage` here is already **above
the regulatory limit of 15 mg/100 g** under the intended correspondence. The
`early_spoilage` name refers to the analytical tier, not to regulatory
acceptability.

## Label revision history

The `note` column preserves the labelling history of every
frame as `old_label=... auto_label=...`, where `old_label` is the original
annotation (assigned from room-temperature ageing duration) and `auto_label` is
the value produced by the ammonia rule. **The `time_label` column holds
`auto_label`** — the rule overwrote the original annotation.

Four of the 37 files have `old_label` ≠ `auto_label`:

| File | Original | Final label in `time_label` |
|---|---|---|
| `dynamic_exp_20260517b_t8h5.csv` | `early_spoilage` | **`fresh`** |
| `dynamic_exp_20260519a_t11h.csv` | `unlabeled` | `spoiled` |
| `dynamic_exp_20260519b_t11h.csv` | `unlabeled` | `spoiled` |
| `dynamic_exp_20260519c_t11h.csv` | `unlabeled` | `spoiled` |

Three had not been annotated and were filled in by the rule. One —
`20260517b_t8h5` — moved from `early_spoilage` to `fresh`: its steady-state
ammonia of 3.79 ppm sits just below the 4.0 ppm boundary after 8.5 h of ageing at
about 25–26 °C, i.e. close to the interpolated boundary described above, and the
change is in the conservative direction. Both annotations are kept in the data so
that the decision is auditable; the duration-based annotation can be recovered
from the `note` column at any time.

