# Start here: personal Databricks project

## What you need

- A personal Databricks **Free Edition** account (no cloud-provider account required).
- This project file: `medicare_adherence_starter.py`.

## Five-minute setup

1. Go to the [Databricks Free Edition sign-up page](https://www.databricks.com/learn/free-edition).
2. Create a Free Edition workspace using your personal email.
3. In the left sidebar, choose **Workspace**, then **New**, then **Import**.
4. Upload `medicare_adherence_starter.py` and open it as a notebook.
5. Use Python as the notebook language, then run all cells.

The notebook creates four synthetic source tables and three result tables in the `default` schema:

- `ma_demo_member`, `ma_demo_enrollment`, `ma_demo_medication`, `ma_demo_prescription_fill`
- `ma_demo_adherence`, `ma_demo_adherence_monthly`, `ma_demo_intervention_worklist`, `ma_demo_measure_summary`, `ma_demo_reversal_audit`

## What the results mean

`ma_demo_adherence` shows simplified proportion of days covered (PDC): the number of distinct medication-covered days divided by the eligible days from the first fill through September 30, 2026. The worklist surfaces non-adherent demo members and marks every row for human review.

This is an educational prototype only. It uses fabricated records and simplified measure logic; it is not an official CMS Stars measure calculation, clinical advice, or a system for handling real patient information.

The notebook now removes a paid fill when a matching synthetic reversal is present and records that decision in `ma_demo_reversal_audit`. In production, use the source system's transaction identifiers rather than matching on member, drug, date, and days supplied.

## Next enhancement

Use `medicare_adherence_dashboard_queries.sql` to create a simple dashboard. In Databricks, open **SQL Editor**, paste and run each query individually, save it, then choose **Add visualization** using the suggested chart type in the comments. Create a dashboard and add the five saved visualizations, including the monthly PDC trend line.

After the dashboard, useful next steps are more realistic refill behavior and a plain-English explanation of each notebook section.

