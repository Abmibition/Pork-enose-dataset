# Pork Freshness Electronic-Nose Dataset (RISC-V, 4-class)

Raw time-series recordings from a custom RISC-V electronic nose measuring pork
headspace. 37 recordings, 2 894 frames, four freshness classes.

Every number in these files is a real measurement or a value computed from real
measurements at acquisition time. Nothing is simulated or augmented.

Section 3 documents the label definition and the baseline conventions — worth
reading before the derived columns are used in an evaluation.

---

## 1. Hardware

| Part                           | Role                                                   | Columns produced                                        |
| ------------------------------ | ------------------------------------------------------ | ------------------------------------------------------- |
| CH32V307VCT6 (RISC-V, 144 MHz) | MCU, on-device acquisition and inference               | —                                                       |
| ZE03-NH₃                       | electrochemical ammonia module                         | `nh3_ppm`                                               |
| ZE03-H₂S                       | electrochemical hydrogen-sulfide module                | `h2s_ppm`                                               |
| Bosch BME680                   | temperature / humidity / pressure / VOC gas resistance | `temperature`, `humidity`, `pressure`, `gas_resistance` |

A small diaphragm pump dilutes the sample headspace with ambient air. Frames are
logged over UART at roughly 1.3 Hz during a 60 s detection window, giving 69–92
frames per recording.

## 2. Contents

```
data/
└── nominal_24-28C/   37 recordings, 2 894 frames, 23.3–27.8 °C
```

### Class distribution (frames)

| Class            | Frames |
| ---------------- | ------ |
| `air`            | 506    |
| `fresh`          | 824    |
| `early_spoilage` | 893    |
| `spoiled`        | 671    |

`air` frames are ambient-air recordings with no meat present — device zero
reference, not a freshness grade.

### File naming

- `dynamic_exp_<YYYYMMDD>_<replicate>_t<hours>h.csv` — meat exposure.
  `t1p` / `t6p` / `t15p` in the 8 May files are elapsed-time tags in the original
  notation, not percentages.
- `dynamic_air_*.csv`, `dynamic_exp_*_air.csv` — dedicated ambient-air baselines.

The filename hour tag is the *ageing time of the meat*, not the class. Several
recordings taken at a nonzero ageing time carry the `air` label because their
steady-state ammonia stayed at ambient level (see section 3).

## 3. Notes for reuse

### (1) `time_label` is defined by a steady-state ammonia threshold

The class label is a deterministic function of the recording's steady-state
ammonia reading, applied uniformly by the preprocessing script:

| Steady-state NH₃ | Label            |
| ---------------- | ---------------- |
| < 1.0 ppm        | `air`            |
| 1.0 – 4.0 ppm    | `fresh`          |
| 4.0 – 5.5 ppm    | `early_spoilage` |
| ≥ 5.5 ppm        | `spoiled`        |

Applying one rule to every recording keeps the labelling reproducible and removes
annotator subjectivity, and it means `nh3_ppm` and its derivative `nh3_delta`
share a source with the label. Evaluations on this dataset are therefore best
designed around that: hold out whole recordings (leave-one-recording-out),
report results on ammonia-free feature subsets alongside the full set, and
characterise the *direction* of errors — in this application, confusing `spoiled`
for `fresh` and the reverse are not equivalent. The thresholds are anchored to
colourimetric TVB-N measurements.

### (2) The derived columns use more than one baseline convention

Both are relative-to-baseline quantities:

```
nh3_delta    = nh3_ppm - baseline_nh3
gas_drop_pct = (baseline_gas - gas_resistance) / baseline_gas * 100
```

The baseline convention differs within the dataset:

| Files    | Baseline source                          | Implied `baseline_gas`                |
| -------- | ---------------------------------------- | ------------------------------------- |
| 28 files | global mean over all air recordings      | 108 188 Ω, one shared value           |
| 9 files  | paired air recording of the same session | 7 distinct values, 65 636 – 145 315 Ω |

The dataset therefore carries eight baselines. `gas_drop_pct` spans −24.3 % to
99.3 % (it turns negative where gas resistance exceeds the global air baseline).
Pooling the derived columns across sessions calls for recomputing them under a
single convention first. The raw columns — `nh3_ppm`, `h2s_ppm`, `gas_resistance`,
`temperature`, `humidity`, `pressure` — are direct readings and are comparable
throughout.

Which baseline each file used is recorded in its own `note` column, and
`scripts/summarize.py` recovers every baseline independently by inversion, so the
two can be checked against each other. `gas_drop_pct` is one of the model input
features used in our own work rather than a diagnostic column, which is why the
convention is documented in this much detail. 

## 4. Columns

Each CSV has 21 columns.

| Column                    | Unit  | Source                                                  |
| ------------------------- | ----- | ------------------------------------------------------- |
| `timestamp`               | —     | host clock                                              |
| `sample_id`               | —     | recording identifier                                    |
| `elapsed_s`               | s     | time since recording start                              |
| `time_label`              | —     | class label, **derived from NH₃** (see above)           |
| `sensory_label`           | —     | sensory annotation slot; `none` throughout |
| `nh3_ppm`                 | ppm   | ZE03-NH₃, direct reading                                |
| `h2s_ppm`                 | ppm   | ZE03-H₂S, direct reading                                |
| `temperature`             | °C    | BME680                                                  |
| `humidity`                | %RH   | BME680                                                  |
| `pressure`                | hPa   | BME680                                                  |
| `gas_resistance`          | Ω     | BME680 VOC channel                                      |
| `s_nh3`, `s_h2s`, `s_bme` | count | on-device spike counts, **before** lateral inhibition   |
| `i_nh3`, `i_h2s`, `i_bme` | count | on-device spike counts, **after** lateral inhibition    |
| `note`                    | —     | provenance string                                       |
| `nh3_delta`, `h2s_delta`  | ppm   | derived, baseline-subtracted                            |
| `gas_drop_pct`            | %     | derived, baseline-relative                              |

The `s_*` / `i_*` columns are logged by the firmware's rate-based spike encoder
and its lateral-inhibition stage. They are retained for transparency; our own
deployed model does not consume them.

## 5. Reproducing the summary tables

```bash
python scripts/summarize.py          # stdlib only, no dependencies
```

Every count, range and baseline quoted above is printed by this script, so the
tables can be checked against the files rather than trusted.

## 6. License and citation

Data released under **CC BY 4.0** — see [LICENSE](LICENSE). You may share and
adapt with attribution.

A manuscript describing the measurement system and its evaluation is in
preparation; this section will be updated with the citation when it appears.

Corrections and questions: please open an issue.
