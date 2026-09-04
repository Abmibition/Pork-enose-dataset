# Column dictionary

Every file has 21 columns.

## Identity and timing

| Column | Unit | Notes |
|---|---|---|
| `timestamp` | — | Host wall-clock at frame capture, millisecond resolution (`2026-05-08 11:15:39.968`). |
| `sample_id` | — | Recording identifier, e.g. `pork_002`, `exp_20260517_a`. Frames sharing a `sample_id` belong to one recording. |
| `elapsed_s` | s | Seconds since the start of the logged detection window. Runs 0 → ≈60 s. |

## Labels

| Column | Unit | Notes |
|---|---|---|
| `time_label` | — | Class: `air`, `fresh`, `early_spoilage`, `spoiled`. Defined by a steady-state `nh3_ppm` threshold — see [labels.md](labels.md). |
| `sensory_label` | — | Slot for human sensory annotation, reserved in the schema; the value is `none` in every frame. |

## Direct sensor readings

These are raw measurements, comparable across the entire dataset.

| Column | Unit | Source | Observed range |
|---|---|---|---|
| `nh3_ppm` | ppm | ZE03-NH₃ electrochemical module | 0 – ~13 |
| `h2s_ppm` | ppm | ZE03-H₂S electrochemical module | integer-valued, frequently 0 |
| `temperature` | °C | BME680 | 23.3 – 27.8 |
| `humidity` | %RH | BME680 | ~45 – 56 |
| `pressure` | hPa | BME680 | ~991 – 994 |
| `gas_resistance` | Ω | BME680 VOC channel | ~1 000 – 112 800 |

`h2s_ppm` is reported at 1 ppm resolution by the module, so it is zero for most
fresh and early-spoilage frames and only becomes nonzero in strongly spoiled
samples. It is a low-resolution channel, not a dead one.

`gas_resistance` falls as VOC concentration rises — low resistance means a dirtier
headspace.

## On-device spike encoding

The firmware contains a rate-based spike encoder and a lateral-inhibition stage.
Both write their per-channel spike counts into every frame. Channel order is
NH₃, H₂S, BME680.

| Column | Unit | Notes |
|---|---|---|
| `s_nh3`, `s_h2s`, `s_bme` | count | Raw spike count per channel, **before** lateral inhibition. |
| `i_nh3`, `i_h2s`, `i_bme` | count | Spike count per channel **after** lateral inhibition (cross-channel background subtraction, gain 0.35). |

These columns are logged for transparency and are not consumed by the classifier
developed on this data — that model takes continuous features. They are included
so that the encoder's behaviour can be inspected rather than taken on trust.

## Provenance string

| Column | Unit | Notes |
|---|---|---|
| `note` | — | Populated throughout. |

Format, when present:

```
baseline_src=global b_nh3=0.135 steady_nh3=1.25 steady_dnh3=+1.11 old_label=fresh auto_label=fresh
```

| Field | Meaning |
|---|---|
| `baseline_src` | `global` (mean over all air recordings) or `session(<prefix>)` (paired air recording of that session) |
| `b_nh3` | baseline ammonia used for `nh3_delta`, ppm |
| `steady_nh3` | steady-state ammonia of the recording (mean of final 10 s), ppm — this is the value the label rule thresholds |
| `steady_dnh3` | steady-state ammonia minus baseline, ppm |
| `old_label` | original annotation, from room-temperature ageing duration |
| `auto_label` | label produced by the ammonia threshold rule; **this is what `time_label` holds** |

Only the first frame of each recording carries the full string in most files;
subsequent frames may have an empty `note`.

## Derived columns

**See [baselines.md](baselines.md) for these three.** They are referenced to a
baseline that differs between
sessions.

| Column | Unit | Formula |
|---|---|---|
| `nh3_delta` | ppm | `nh3_ppm - baseline_nh3` |
| `h2s_delta` | ppm | `h2s_ppm - baseline_h2s` |
| `gas_drop_pct` | % | `(baseline_gas - gas_resistance) / baseline_gas * 100` |

`gas_drop_pct` reaches negative values (minimum −24.3 %) because measured
resistance can exceed the global air baseline.
