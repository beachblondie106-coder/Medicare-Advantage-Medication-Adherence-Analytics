# Data Dictionary

## Source and reference tables

| Table | Field | Description |
|---|---|---|
| `ma_demo_member` | `member_key` | Fictional, tokenized member identifier. |
| `ma_demo_member` | `plan_name`, `contract_id`, `pbp_id` | Fictional plan attributes used for a Medicare Advantage-style context. |
| `ma_demo_member` | `birth_date` | Fabricated date used only for demonstration. |
| `ma_demo_enrollment` | `enrollment_start`, `enrollment_end` | Demo enrollment window used to limit PDC-covered days. |
| `ma_demo_medication` | `medication_key`, `ndc`, `generic_name` | Simplified medication reference values. |
| `ma_demo_medication` | `measure_family` | PDC-DIA, PDC-RASA, or PDC-STA measure-family code. |
| `ma_demo_prescription_fill` | `fill_key` | Fictional prescription-fill event identifier. |
| `ma_demo_prescription_fill` | `service_date`, `days_supply` | Fill date and intended days of medication coverage. |
| `ma_demo_prescription_fill` | `event_status` | `PAID` or `REVERSAL`; matched reversals remove a paid fill from PDC calculation. |

## Analytical tables

| Table | Grain | Key fields | Purpose |
|---|---|---|---|
| `ma_demo_adherence` | Member x measure family | `member_key`, `measure_family` | Current reporting-cutoff PDC result. |
| `ma_demo_adherence_monthly` | Member x measure family x month | `member_key`, `measure_family`, `month_start` | Cumulative month-end PDC snapshots. |
| `ma_demo_intervention_worklist` | Member x measure family | `member_key`, `measure_family` | Non-adherent members prioritized for human review. |
| `ma_demo_measure_summary` | Measure family | `measure_family` | Measure-level counts, average PDC, and adherence rate. |
| `ma_demo_reversal_audit` | Matched paid-fill/reversal event | `member_key`, `service_date` | Transparent audit trail of excluded fill events. |

## Measure-family labels

| Code | Dashboard label | Demo medication |
|---|---|---|
| `PDC-DIA` | Medication Adherence for Diabetes Medications | metformin |
| `PDC-RASA` | Medication Adherence for Hypertension (RAS antagonists) | lisinopril |
| `PDC-STA` | Medication Adherence for Cholesterol (Statins) | atorvastatin |

