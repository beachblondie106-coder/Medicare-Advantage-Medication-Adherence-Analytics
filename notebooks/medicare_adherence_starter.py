# Databricks notebook source
# MAGIC %md
# MAGIC # Medicare Advantage Medication Adherence Analytics
# MAGIC This educational notebook uses entirely synthetic data. Do not replace it
# MAGIC with real patient information in a personal Databricks workspace.

# COMMAND ----------

from datetime import date, timedelta
from pyspark.sql import functions as F

RUN_DATE = date(2026, 9, 30)
TARGET_SCHEMA = "default"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Create synthetic source tables
# MAGIC `member_key` is a fictional token and all names, dates, and events below are fabricated.

# COMMAND ----------

members = [
    ("M001", "Northstar Health", "H001", "001", "1954-07-11"),
    ("M002", "Northstar Health", "H001", "001", "1948-02-03"),
    ("M003", "Northstar Health", "H001", "001", "1959-10-26"),
    ("M004", "Northstar Health", "H001", "001", "1951-04-18"),
    ("M005", "Northstar Health", "H001", "001", "1946-12-09"),
]

# Add 50 fictional members with deterministic refill patterns. No real people or
# patient data are represented. Patterns cycle through high, borderline, and low
# adherence so the dashboard has a more useful distribution.
for member_number in range(6, 56):
    member_key = f"M{member_number:03d}"
    birth_year = 1942 + (member_number % 22)
    birth_month = (member_number % 12) + 1
    birth_day = (member_number % 27) + 1
    members.append((
        member_key, "Northstar Health", "H001", "001",
        f"{birth_year:04d}-{birth_month:02d}-{birth_day:02d}"
    ))
member_df = spark.createDataFrame(
    members, ["member_key", "plan_name", "contract_id", "pbp_id", "birth_date"]
).withColumn("birth_date", F.to_date("birth_date"))

enrollment_df = spark.createDataFrame(
    [(m[0], "2026-01-01", "2026-12-31") for m in members],
    ["member_key", "enrollment_start", "enrollment_end"],
).select(
    "member_key", F.to_date("enrollment_start").alias("enrollment_start"),
    F.to_date("enrollment_end").alias("enrollment_end")
)

# A simplified reference mapping. Validate any real measure mapping against the
# applicable measure specification before treating output as an official result.
medication_df = spark.createDataFrame([
    ("RX001", "00093-1047-56", "atorvastatin", "PDC-STA"),
    ("RX002", "00093-1047-98", "lisinopril", "PDC-RASA"),
    ("RX003", "00093-1047-02", "metformin", "PDC-DIA"),
], ["medication_key", "ndc", "generic_name", "measure_family"])

# Fill events are synthetic. M004's paid event is intentionally reversed; M005 has no fills.
fills = [
    ("F001", "M001", "RX001", "2026-01-05", 90, "PAID"),
    ("F002", "M001", "RX001", "2026-04-05", 90, "PAID"),
    ("F003", "M001", "RX001", "2026-07-04", 90, "PAID"),
    ("F004", "M002", "RX001", "2026-01-15", 30, "PAID"),
    ("F005", "M002", "RX001", "2026-03-20", 30, "PAID"),
    ("F006", "M003", "RX002", "2026-02-01", 90, "PAID"),
    ("F007", "M003", "RX002", "2026-05-02", 90, "PAID"),
    ("F008", "M004", "RX003", "2026-01-10", 30, "PAID"),
    ("F009", "M004", "RX003", "2026-01-10", 30, "REVERSAL"),
]

medication_cycle = ["RX001", "RX002", "RX003"]
fill_number = 10
for member_number in range(6, 56):
    member_key = f"M{member_number:03d}"
    medication_key = medication_cycle[(member_number - 6) % len(medication_cycle)]
    pattern = (member_number - 6) % 3
    first_fill_date = date(2026, 1, 1) + timedelta(days=(member_number * 3) % 45)

    # Pattern 0: near-continuous coverage; Pattern 1: moderate refill gaps;
    # Pattern 2: long refill gaps. All dates and fills are fabricated.
    days_supply, refill_gap = [(90, 0), (30, 12), (30, 48)][pattern]
    service_date = first_fill_date
    while service_date <= RUN_DATE:
        fills.append((
            f"F{fill_number:03d}", member_key, medication_key,
            service_date.isoformat(), days_supply, "PAID"
        ))
        fill_number += 1
        service_date += timedelta(days=days_supply + refill_gap)
fill_df = spark.createDataFrame(
    fills, ["fill_key", "member_key", "medication_key", "service_date", "days_supply", "event_status"]
).withColumn("service_date", F.to_date("service_date"))

for name, df in {
    "ma_demo_member": member_df,
    "ma_demo_enrollment": enrollment_df,
    "ma_demo_medication": medication_df,
    "ma_demo_prescription_fill": fill_df,
}.items():
    df.write.mode("overwrite").saveAsTable(f"{TARGET_SCHEMA}.{name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Calculate a transparent, simplified PDC
# MAGIC
# MAGIC Paid fills matched to a reversal are excluded. Each remaining paid fill expands into
# MAGIC covered days. Duplicate covered days are counted only once, and days are limited to
# MAGIC the member's enrollment and the reporting cutoff.

# COMMAND ----------

all_fill_events = spark.table(f"{TARGET_SCHEMA}.ma_demo_prescription_fill")

# Demo reversal-matching key: member + drug + date + days supplied. Production claims/PDE
# data should use the source system's transaction and reversal linkage identifiers instead.
reversal_events = (
    all_fill_events.filter(F.col("event_status") == "REVERSAL")
    .select("member_key", "medication_key", "service_date", "days_supply")
    .dropDuplicates()
)

paid_fills = (
    all_fill_events.filter(F.col("event_status") == "PAID")
    .join(reversal_events, ["member_key", "medication_key", "service_date", "days_supply"], "left_anti")
    .join(spark.table(f"{TARGET_SCHEMA}.ma_demo_medication"), "medication_key")
)

reversal_audit = (
    all_fill_events.filter(F.col("event_status") == "PAID")
    .join(reversal_events, ["member_key", "medication_key", "service_date", "days_supply"], "inner")
    .join(spark.table(f"{TARGET_SCHEMA}.ma_demo_medication"), "medication_key")
    .select("member_key", "measure_family", "service_date", "days_supply")
    .withColumn("exclusion_reason", F.lit("Paid fill matched to reversal"))
)
reversal_audit.write.mode("overwrite").saveAsTable(f"{TARGET_SCHEMA}.ma_demo_reversal_audit")
display(reversal_audit)

first_fill = paid_fills.groupBy("member_key", "measure_family").agg(
    F.min("service_date").alias("measurement_start")
)

covered_days = (
    paid_fills
    .withColumn(
        "covered_date",
        F.explode(F.sequence("service_date", F.date_add("service_date", (F.col("days_supply") - 1).cast("int"))))
    )
    .join(spark.table(f"{TARGET_SCHEMA}.ma_demo_enrollment"), "member_key")
    .filter((F.col("covered_date") >= F.col("enrollment_start")) &
            (F.col("covered_date") <= F.col("enrollment_end")) &
            (F.col("covered_date") <= F.lit(RUN_DATE)))
    .select("member_key", "measure_family", "covered_date")
    .dropDuplicates()
)

denominator = (
    first_fill
    .join(spark.table(f"{TARGET_SCHEMA}.ma_demo_enrollment"), "member_key")
    .withColumn("period_start", F.greatest("measurement_start", "enrollment_start"))
    .withColumn("period_end", F.least(F.lit(RUN_DATE), "enrollment_end"))
    .withColumn("eligible_days", F.datediff("period_end", "period_start") + F.lit(1))
)

adherence = (
    denominator
    .join(covered_days.groupBy("member_key", "measure_family").agg(F.count("*").alias("covered_days")),
          ["member_key", "measure_family"], "left")
    .fillna({"covered_days": 0})
    .withColumn("pdc", F.round(F.col("covered_days") / F.col("eligible_days"), 4))
    .withColumn("adherent_flag", F.col("pdc") >= F.lit(0.80))
    .withColumn("calculation_version", F.lit("demo-v1-simplified"))
    .withColumn("reporting_cutoff", F.lit(RUN_DATE).cast("date"))
    .select("member_key", "measure_family", "period_start", "period_end", "eligible_days",
            "covered_days", "pdc", "adherent_flag", "calculation_version", "reporting_cutoff")
)

adherence.write.mode("overwrite").saveAsTable(f"{TARGET_SCHEMA}.ma_demo_adherence")
display(adherence.orderBy("pdc", "member_key"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Create monthly PDC snapshots
# MAGIC
# MAGIC These are cumulative snapshots from the first fill through each month-end. They let
# MAGIC the dashboard show whether the demo population's PDC is trending up or down.

# COMMAND ----------

monthly_snapshots = (
    denominator
    .select("member_key", "measure_family", "period_start", "period_end")
    .withColumn(
        "month_start",
        F.explode(F.expr("sequence(trunc(period_start, 'month'), trunc(period_end, 'month'), interval 1 month)"))
    )
    .withColumn("snapshot_end", F.least(F.last_day("month_start"), F.col("period_end")))
)

adherence_monthly = (
    monthly_snapshots.alias("snapshot")
    .join(
        covered_days.alias("coverage"),
        (F.col("snapshot.member_key") == F.col("coverage.member_key")) &
        (F.col("snapshot.measure_family") == F.col("coverage.measure_family")) &
        (F.col("coverage.covered_date") >= F.col("snapshot.period_start")) &
        (F.col("coverage.covered_date") <= F.col("snapshot.snapshot_end")),
        "left"
    )
    .groupBy(
        F.col("snapshot.member_key").alias("member_key"),
        F.col("snapshot.measure_family").alias("measure_family"),
        F.col("snapshot.month_start").alias("month_start"),
        F.col("snapshot.period_start").alias("period_start"),
        F.col("snapshot.snapshot_end").alias("snapshot_end")
    )
    .agg(F.countDistinct(F.col("coverage.covered_date")).alias("covered_days"))
    .withColumn("eligible_days", F.datediff("snapshot_end", "period_start") + F.lit(1))
    .withColumn("pdc", F.round(F.col("covered_days") / F.col("eligible_days"), 4))
    .withColumn("adherent_flag", F.col("pdc") >= F.lit(0.80))
    .withColumn("calculation_version", F.lit("demo-v1-simplified"))
)

adherence_monthly.write.mode("overwrite").saveAsTable(f"{TARGET_SCHEMA}.ma_demo_adherence_monthly")
display(adherence_monthly.orderBy("month_start", "member_key"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Publish an educational intervention worklist
# MAGIC This is a prioritization exercise, not clinical decision support. A human reviewer
# MAGIC must validate any outreach decision.

# COMMAND ----------

worklist = (
    adherence
    .filter(~F.col("adherent_flag"))
    .withColumn("gap_days", F.col("eligible_days") - F.col("covered_days"))
    .withColumn(
        "priority",
        F.when(F.col("pdc") < 0.50, F.lit("High"))
         .when(F.col("pdc") < 0.70, F.lit("Medium"))
         .otherwise(F.lit("Review"))
    )
    .withColumn("recommended_action", F.lit("Verify access and outreach eligibility"))
    .withColumn("requires_human_review", F.lit(True))
    .select("member_key", "measure_family", "pdc", "gap_days", "priority",
            "recommended_action", "requires_human_review", "calculation_version")
)

worklist.write.mode("overwrite").saveAsTable(f"{TARGET_SCHEMA}.ma_demo_intervention_worklist")
display(worklist.orderBy(F.expr("CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END"), "pdc"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Summary table

# COMMAND ----------

summary = adherence.groupBy("measure_family").agg(
    F.count("*").alias("members_in_demo"),
    F.sum(F.when("adherent_flag", 1).otherwise(0)).alias("adherent_members"),
    F.round(F.avg("pdc"), 4).alias("average_pdc"),
    F.round(F.avg(F.when("adherent_flag", 1).otherwise(0)), 4).alias("adherence_rate")
)
summary.write.mode("overwrite").saveAsTable(f"{TARGET_SCHEMA}.ma_demo_measure_summary")
display(summary.orderBy("measure_family"))

