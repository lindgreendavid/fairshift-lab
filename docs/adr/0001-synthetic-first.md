# ADR 0001: Begin with an explicit synthetic process

- Status: Accepted
- Date: 2026-08-12

## Context

The first release needs controlled distribution changes, deterministic tests, transparent provenance, and no personal data. A real dataset would introduce measurement choices and historical context before the experiment infrastructure is validated.

## Decision

Use an explicit structural synthetic generator and publish every equation and intervention. Keep the generator separate from model training and metric computation.

## Consequences

Experiments have clear ground truth about what changed, are cheap to reproduce, and carry no data-license or privacy dependency. External validity is deliberately absent. Later real-data case studies must receive their own Data Cards, licenses, construct-validity analysis, and ethical review; they may not inherit claims from synthetic results.

