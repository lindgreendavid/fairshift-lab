# Fairshift Lab interactive site

This directory contains the accessible browser laboratory for Fairshift Lab v0.2.0. It mirrors the documented synthetic process so visitors can explore shift mechanisms, decision thresholds, group measurements, and sampling uncertainty without installing Python.

The browser simulation favors immediate explanation and uses 80 stratified bootstrap resamples. The Python package in the repository root remains the authoritative implementation for reproducible research output.

## Local development

```bash
pnpm install
pnpm run dev
pnpm run lint
pnpm run test
```

No personal data, tracking, authentication, database, cookies, or external runtime API is used.
