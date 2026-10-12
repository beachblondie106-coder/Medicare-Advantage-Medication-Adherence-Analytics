# Quality Assurance Checklist

## Notebook run

- [ ] Notebook runs end to end in Databricks without errors.
- [ ] Source tables are created: member, enrollment, medication, and prescription fill.
- [ ] Analytical tables are created: adherence, monthly adherence, worklist, summary, and reversal audit.

## PDC logic

- [ ] Every PDC value is between 0 and 1.
- [ ] Eligible days are positive for every included result.
- [ ] Covered days do not exceed eligible days.
- [ ] Overlapping fill coverage is counted once per covered date.
- [ ] Coverage outside the enrollment interval or reporting cutoff is excluded.

## Reversal logic

- [ ] A matched paid fill and reversal appear in `ma_demo_reversal_audit`.
- [ ] The matched paid fill does not contribute covered days to PDC.
- [ ] The reversal audit table is visible on the dashboard.

## Dashboard validation

- [ ] Adherence summary totals reconcile to member level results.
- [ ] Worklist includes only members below 80% PDC.
- [ ] Worklist priorities follow the documented PDC bands.
- [ ] Monthly trend contains one record per included member, measure family, and month.
- [ ] Charts use short measure codes and tables use full measure labels.
- [ ] Dashboard and exported PDF display the synthetic data disclaimer.

## Portfolio safety

- [ ] No real patient, pharmacy, organization, or credential data is included.
- [ ] `DATA_NOTICE.md` is present at the repository root.
- [ ] The README states that the project is educational and not an official CMS Stars calculation.

