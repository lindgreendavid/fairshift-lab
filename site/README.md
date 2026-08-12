# Fairshift Lab interactive site

This directory contains the accessible browser laboratory for Fairshift Lab v1.1.0. It mirrors the documented synthetic process so visitors can explore shift mechanisms, source-only temperature scaling, reliability, complete decision-threshold curves, group measurements, sampling uncertainty, the frozen 300-experiment report, and the 20-seed Policy Studio benchmark without installing Python.

The browser simulation favors immediate explanation and uses 80 stratified bootstrap resamples. Training, calibration, source evaluation, and target evaluation use independent samples. The Python package in the repository root remains the authoritative implementation for reproducible research output.

## Local development

```bash
pnpm install
pnpm run dev
pnpm run lint
pnpm run test
```

No personal data, tracking, authentication, database, cookies, or external runtime API is used.
