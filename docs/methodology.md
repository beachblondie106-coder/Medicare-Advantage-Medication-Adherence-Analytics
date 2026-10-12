# Methodology

## Objective

Demonstrate how a Medicare Advantage quality operations team could identify medication adherence opportunities using a transparent, auditable lakehouse workflow.

## Workflow

1. Generate fictional member, enrollment, medication reference, and prescription fill data in PySpark.
2. Write the source data to Databricks Delta tables in the `default` schema.
3. Identify paid fills that match a reversal using the demo key: member, medication, service date, and days supply.
4. Exclude matched paid fills from PDC coverage and write the decision to `ma_demo_reversal_audit`.
5. Expand remaining paid fills into daily medication coverage dates.
6. Limit covered dates to enrollment and the reporting cutoff and deduplicate overlapping dates.
7. Calculate member level PDC and the 80% adherence flag.
8. Create cumulative month end PDC snapshots for trend analysis.
9. Publish measure summaries and a human review intervention worklist.

## Design choices

- The project uses a simplified, transparent PDC calculation so each result can be traced to source fills and days of coverage.
- Three measure families are represented: diabetes medications, RAS antagonists, and statins.
- Fifty additional fictional members create varied high, moderate, and low refill patterns for more realistic visual distributions.
- The dashboard uses abbreviations in charts for readability and full measure names in tables for clarity.

## Limitations

This project is not a production quality measure engine. It does not implement the complete current CMS technical specifications, official eligibility rules, multi drug class logic, production transaction linkage, or clinical review process. It must not be used for real member level decisions.

