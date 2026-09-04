# Acquisition protocol

## Sample handling

Pork samples were held at room temperature and measured repeatedly as they aged.
The hour tag in each filename (`t4p5h`, `t12p58h`, …) is the elapsed
room-temperature ageing time of that sample, in hours, at the moment of
measurement. Recordings tagged `t0p00h` and the `air`-labelled recordings are
ambient-air references taken with no meat in the chamber.

Sample headspace is drawn into the measurement chamber and diluted with ambient
air by a small diaphragm pump. Dilution keeps the electrochemical modules inside
their linear range once ammonia rises in heavily spoiled samples.

## Device state machine

The instrument cycles through an idle phase, a baseline phase and a detection
phase. At the time this dataset was recorded the phases were 20 s idle, 20 s
baseline and **60 s detection**. Only the detection phase is logged to CSV, which
is why `elapsed_s` runs from 0 to about 60 s in every file:

| Subset | Detection window observed | Sampling rate |
|---|---|---|
| `nominal_24-28C` | 60.0 – 60.9 s | ≈ 1.34 Hz |

That yields 69–92 frames per recording. Frames are emitted over UART and captured
by a host-side logger.

The firmware's detection window was lengthened in later development. The files in
this repository are all 60 s and should be treated as a 60 s protocol regardless
of what any later firmware revision does.

## What is not preserved in these files

- **Pump phase.** The acquisition firmware emits a pump-phase flag indicating
  whether the pump was drawing or resting; frames taken while the pump runs are
  affected by forced convection over the sensing elements. That flag is **not**
  present in these CSVs, so pump-on and pump-off frames cannot be separated post
  hoc. Pump drive settings also changed across development.
- **Idle and baseline phases.** Only the detection window was logged.
- **Reference chemistry per recording.** TVB-N was determined colourimetrically
  at two calibration points on 17 May 2026, not once per recording. See
  [labels.md](labels.md).

## Ambient conditions

Ambient temperature and humidity are recorded per frame by the BME680 and vary
across the dataset:

| Subset | Temperature | Nominal intent |
|---|---|---|
| `nominal_24-28C` | 23.3 – 27.8 °C | uncontrolled indoor ambient |

Because baseline conventions for the derived columns vary by session, see
[baselines.md](baselines.md) before comparing derived columns across sessions.
