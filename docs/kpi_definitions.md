# KPI Definitions

## Proportion of days covered (PDC)

```text
PDC = distinct covered medication days / eligible days
```

For this demonstration, the measurement period begins with a member's first eligible paid fill and ends at the reporting cutoff. Covered dates are restricted to the enrollment period and counted once, even when fill coverage overlaps.

## Core KPIs

| KPI | Definition | Portfolio interpretation |
|---|---|---|
| PDC | Covered days divided by eligible days. | Higher is better; 80% or greater is marked adherent in this demo. |
| Adherence rate | Members with PDC >= 80% divided by included members. | Measure performance indicator. |
| Average PDC | Average member level PDC within a measure. | Population adherence trend indicator. |
| Gap days | Eligible days minus covered days. | A larger gap indicates a larger potential adherence opportunity. |
| Included members | Members with an eligible, nonreversed paid fill represented in the measure result. | Denominator used by the demo summary. |
| Reversed fill exclusions | Paid fills matching a reversal in the demo match key. | Data quality control that prevents canceled fills from inflating PDC. |

## Worklist priority rules

| PDC range | Priority |
|---|---|
| Below 50% | High |
| 50% to below 70% | Medium |
| 70% to below 80% | Review |

The worklist is an educational prioritization exercise. It is not clinical decision support and requires human review before any action.

