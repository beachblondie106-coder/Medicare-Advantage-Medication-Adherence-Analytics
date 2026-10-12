-- Medicare Advantage Medication-Adherence Demo: Dashboard Queries
-- Run one query at a time in Databricks SQL. These queries use synthetic data only.

-- 1) Scorecard: adherence by medication-measure family
SELECT
  measure_family,
  members_in_demo,
  adherent_members,
  ROUND(adherence_rate * 100, 1) AS adherence_rate_pct,
  ROUND(average_pdc * 100, 1) AS average_pdc_pct
FROM default.ma_demo_measure_summary
ORDER BY measure_family;

-- Suggested visualization: bar chart
-- X axis = measure_family; Y axis = adherence_rate_pct; show data labels.


-- 2) Intervention queue: cases requiring human review
SELECT
  member_key,
  CASE measure_family
    WHEN 'PDC-DIA' THEN 'Medication Adherence for Diabetes Medications'
    WHEN 'PDC-RASA' THEN 'Medication Adherence for Hypertension (RAS antagonists)'
    WHEN 'PDC-STA' THEN 'Medication Adherence for Cholesterol (Statins)'
    ELSE measure_family
  END AS measure_name,
  ROUND(pdc * 100, 1) AS pdc_pct,
  gap_days,
  priority,
  recommended_action
FROM default.ma_demo_intervention_worklist
ORDER BY
  CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
  pdc_pct;

-- Suggested visualization: table, with conditional color on priority and pdc_pct.


-- 3) Member-level PDC distribution
SELECT
  measure_family,
  CASE
    WHEN pdc < 0.50 THEN 'Below 50%'
    WHEN pdc < 0.80 THEN '50%–79.9%'
    ELSE '80% or higher'
  END AS pdc_band,
  COUNT(*) AS members
FROM default.ma_demo_adherence
GROUP BY measure_family,
  CASE
    WHEN pdc < 0.50 THEN 'Below 50%'
    WHEN pdc < 0.80 THEN '50%–79.9%'
    ELSE '80% or higher'
  END
ORDER BY measure_family, pdc_band;

-- Suggested visualization: stacked bar chart.


-- 4) Data-quality audit: fills removed because they were reversed
SELECT
  member_key,
  CASE measure_family
    WHEN 'PDC-DIA' THEN 'Medication Adherence for Diabetes Medications'
    WHEN 'PDC-RASA' THEN 'Medication Adherence for Hypertension (RAS antagonists)'
    WHEN 'PDC-STA' THEN 'Medication Adherence for Cholesterol (Statins)'
    ELSE measure_family
  END AS measure_name,
  service_date,
  days_supply,
  exclusion_reason
FROM default.ma_demo_reversal_audit
ORDER BY service_date DESC;

-- Suggested visualization: table. Keeping this tile on the dashboard demonstrates
-- traceability rather than hiding a data-quality decision.


-- 5) Monthly PDC trend: population average and percent at/above 80%
SELECT
  month_start,
  measure_family,
  ROUND(AVG(pdc) * 100, 1) AS average_pdc_pct,
  ROUND(AVG(CASE WHEN adherent_flag THEN 1 ELSE 0 END) * 100, 1) AS adherence_rate_pct,
  COUNT(*) AS included_members
FROM default.ma_demo_adherence_monthly
GROUP BY month_start, measure_family
ORDER BY month_start, measure_family;

-- Suggested visualization: line chart.
-- X axis = month_start; Y axis = average_pdc_pct; series = measure_family.

