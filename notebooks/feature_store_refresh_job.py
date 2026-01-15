# Databricks notebook source
# MAGIC %md
# MAGIC # Feature Store Refresh Job
# MAGIC 
# MAGIC This notebook can be scheduled to run periodically (e.g., daily) to update
# MAGIC the feature store with the latest data.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

from databricks.feature_store import FeatureStoreClient
from pyspark.sql import functions as F
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CATALOG = "main"
SCHEMA = "ticket_analytics"
FEATURE_TABLE_NAME = f"{CATALOG}.{SCHEMA}.company_churn_features"

fs = FeatureStoreClient()

# Parameters (can be passed via job parameters)
dbutils.widgets.text("refresh_mode", "incremental", "Refresh Mode (full/incremental)")
dbutils.widgets.text("lookback_days", "7", "Lookback Days for Incremental")

refresh_mode = dbutils.widgets.get("refresh_mode")
lookback_days = int(dbutils.widgets.get("lookback_days"))

logger.info(f"Starting feature store refresh - Mode: {refresh_mode}, Lookback: {lookback_days} days")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Data

# COMMAND ----------

reference_date = F.lit(datetime.now())

# Load base tables
companies_df = spark.table(f"{CATALOG}.{SCHEMA}.companies")
customers_df = spark.table(f"{CATALOG}.{SCHEMA}.customers")
tickets_df = spark.table(f"{CATALOG}.{SCHEMA}.tickets")
interactions_df = spark.table(f"{CATALOG}.{SCHEMA}.ticket_interactions")

# Convert timestamps
tickets_df = tickets_df.withColumn("created_at", F.to_timestamp("created_at"))
tickets_df = tickets_df.withColumn("updated_at", F.to_timestamp("updated_at"))
tickets_df = tickets_df.withColumn("closed_at", F.to_timestamp("closed_at"))

logger.info(f"Loaded {tickets_df.count()} tickets")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Feature Computation Functions

# COMMAND ----------

def compute_ticket_features(tickets_df):
    """Compute ticket volume and status features"""
    return tickets_df.groupBy("company_id").agg(
        F.count("*").alias("total_tickets"),
        F.sum(F.when(F.col("status") == "OPEN", 1).otherwise(0)).alias("tickets_open"),
        F.sum(F.when(F.col("status") == "CLOSED", 1).otherwise(0)).alias("tickets_closed"),
        F.sum(F.when(F.col("status") == "PENDING_CUSTOMER", 1).otherwise(0)).alias("tickets_pending_customer"),
        F.sum(F.when(F.col("status") == "RESOLVED", 1).otherwise(0)).alias("tickets_resolved"),
        F.sum(F.when(F.col("priority") == "HIGH", 1).otherwise(0)).alias("tickets_high_priority"),
        F.sum(F.when(F.col("priority") == "MEDIUM", 1).otherwise(0)).alias("tickets_medium_priority"),
        F.sum(F.when(F.col("priority") == "LOW", 1).otherwise(0)).alias("tickets_low_priority"),
        F.sum(F.when(F.col("priority") == "CRITICAL", 1).otherwise(0)).alias("tickets_critical"),
        F.sum(F.when(F.col("category") == "COMPLAINT", 1).otherwise(0)).alias("tickets_complaint"),
        F.sum(F.when(F.col("category") == "TECHNICAL", 1).otherwise(0)).alias("tickets_technical"),
        F.sum(F.when(F.col("category") == "FINANCIAL", 1).otherwise(0)).alias("tickets_financial"),
        F.sum(F.when(F.col("sla_breached") == "TRUE", 1).otherwise(0)).alias("tickets_sla_breached"),
        F.sum(F.when(F.col("escalated") == "TRUE", 1).otherwise(0)).alias("tickets_escalated"),
        F.sum(F.col("reopened_count").cast("int")).alias("total_reopened_count"),
        F.sum(F.when(F.array_contains(F.split(F.col("tags"), "\\|"), "CHURN_RISK"), 1).otherwise(0)).alias("tickets_churn_risk_tag")
    )

def compute_satisfaction_features(tickets_df):
    """Compute satisfaction and sentiment features"""
    return tickets_df.groupBy("company_id").agg(
        F.avg(F.col("nps_score").cast("double")).alias("avg_nps_score"),
        F.min(F.col("nps_score").cast("double")).alias("min_nps_score"),
        F.max(F.col("nps_score").cast("double")).alias("max_nps_score"),
        F.count(F.when(F.col("nps_score").isNotNull(), 1)).alias("nps_responses_count"),
        F.avg(F.col("csat_score").cast("double")).alias("avg_csat_score"),
        F.min(F.col("csat_score").cast("double")).alias("min_csat_score"),
        F.max(F.col("csat_score").cast("double")).alias("max_csat_score"),
        F.count(F.when(F.col("csat_score").isNotNull(), 1)).alias("csat_responses_count"),
        F.sum(F.when(F.col("sentiment") == "VERY_NEGATIVE", 1).otherwise(0)).alias("sentiment_very_negative_count"),
        F.sum(F.when(F.col("sentiment") == "NEGATIVE", 1).otherwise(0)).alias("sentiment_negative_count"),
        F.sum(F.when(F.col("sentiment") == "NEUTRAL", 1).otherwise(0)).alias("sentiment_neutral_count"),
        F.sum(F.when(F.col("sentiment") == "POSITIVE", 1).otherwise(0)).alias("sentiment_positive_count"),
        F.sum(F.when(F.col("sentiment") == "VERY_POSITIVE", 1).otherwise(0)).alias("sentiment_very_positive_count")
    )

def compute_time_features(tickets_df):
    """Compute time-based features"""
    return tickets_df.groupBy("company_id").agg(
        F.avg(F.col("resolution_time_hours").cast("double")).alias("avg_resolution_time_hours"),
        F.max(F.col("resolution_time_hours").cast("double")).alias("max_resolution_time_hours"),
        F.min(F.col("resolution_time_hours").cast("double")).alias("min_resolution_time_hours"),
        F.stddev(F.col("resolution_time_hours").cast("double")).alias("std_resolution_time_hours"),
        F.avg(F.col("first_response_time_minutes").cast("double")).alias("avg_first_response_time_minutes"),
        F.max(F.col("first_response_time_minutes").cast("double")).alias("max_first_response_time_minutes"),
        F.datediff(reference_date, F.max("created_at")).alias("days_since_last_ticket"),
        F.datediff(reference_date, F.min("created_at")).alias("days_since_first_ticket")
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Compute Features

# COMMAND ----------

logger.info("Computing features...")

# Compute all feature groups
ticket_features = compute_ticket_features(tickets_df)
satisfaction_features = compute_satisfaction_features(tickets_df)
time_features = compute_time_features(tickets_df)

# Time window features
time_window_features = None
for days in [30, 60, 90]:
    cutoff_date = F.date_sub(reference_date, days)
    recent_tickets = tickets_df.filter(F.col("created_at") >= cutoff_date)
    
    recent_features = recent_tickets.groupBy("company_id").agg(
        F.count("*").alias(f"tickets_last_{days}_days"),
        F.sum(F.when(F.col("status") == "OPEN", 1).otherwise(0)).alias(f"tickets_open_last_{days}_days"),
        F.sum(F.when(F.col("sla_breached") == "TRUE", 1).otherwise(0)).alias(f"tickets_sla_breached_last_{days}_days"),
        F.sum(F.when(F.col("category") == "COMPLAINT", 1).otherwise(0)).alias(f"tickets_complaint_last_{days}_days"),
        F.avg(F.col("nps_score").cast("double")).alias(f"avg_nps_last_{days}_days"),
        F.avg(F.col("csat_score").cast("double")).alias(f"avg_csat_last_{days}_days")
    )
    
    if time_window_features is None:
        time_window_features = recent_features
    else:
        time_window_features = time_window_features.join(recent_features, "company_id", "left")

# Customer features
customer_features = customers_df.groupBy("company_id").agg(
    F.count("*").alias("total_customers"),
    F.countDistinct("role").alias("distinct_customer_roles")
)

logger.info("Features computed successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Combine and Enrich Features

# COMMAND ----------

# Base features from companies
feature_df = companies_df.select(
    "company_id",
    "company_name",
    "segment",
    "company_size",
    "monthly_transaction_volume",
    "status",
    "churn_risk_score",
    F.datediff(reference_date, F.to_timestamp("contract_start_date")).alias("days_as_customer")
)

# Join all features
feature_df = feature_df \
    .join(ticket_features, "company_id", "left") \
    .join(satisfaction_features, "company_id", "left") \
    .join(time_features, "company_id", "left") \
    .join(time_window_features, "company_id", "left") \
    .join(customer_features, "company_id", "left")

# Fill nulls
count_columns = [c for c in feature_df.columns if any(x in c for x in [
    "tickets_", "total_", "sentiment_", "days_", "customer"
])]

for col in count_columns:
    if col not in ["company_id", "company_name", "segment", "company_size", "status"]:
        feature_df = feature_df.withColumn(col, F.coalesce(F.col(col), F.lit(0)))

# Add derived features
feature_df = feature_df \
    .withColumn("ticket_resolution_rate", 
                F.when(F.col("total_tickets") > 0, F.col("tickets_closed") / F.col("total_tickets")).otherwise(0)) \
    .withColumn("sla_breach_rate",
                F.when(F.col("total_tickets") > 0, F.col("tickets_sla_breached") / F.col("total_tickets")).otherwise(0)) \
    .withColumn("complaint_rate",
                F.when(F.col("total_tickets") > 0, F.col("tickets_complaint") / F.col("total_tickets")).otherwise(0)) \
    .withColumn("negative_sentiment_rate",
                F.when(F.col("total_tickets") > 0, 
                       (F.col("sentiment_very_negative_count") + F.col("sentiment_negative_count")) / F.col("total_tickets")).otherwise(0)) \
    .withColumn("tickets_per_customer",
                F.when(F.col("total_customers") > 0, F.col("total_tickets") / F.col("total_customers")).otherwise(0)) \
    .withColumn("feature_timestamp", F.current_timestamp())

logger.info(f"Final feature set: {feature_df.count()} companies, {len(feature_df.columns)} features")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Feature Store

# COMMAND ----------

try:
    if refresh_mode == "full":
        logger.info("Performing full refresh...")
        fs.write_table(
            name=FEATURE_TABLE_NAME,
            df=feature_df,
            mode="overwrite"
        )
    else:
        logger.info("Performing incremental refresh...")
        fs.write_table(
            name=FEATURE_TABLE_NAME,
            df=feature_df,
            mode="merge"
        )
    
    logger.info(f"✓ Feature store updated successfully: {FEATURE_TABLE_NAME}")
    
    # Update training dataset as well
    TRAINING_TABLE_NAME = f"{CATALOG}.{SCHEMA}.company_churn_training_data"
    training_df = feature_df.withColumn(
        "is_churn_risk",
        F.when(F.col("churn_risk_score") > 0.7, 1).otherwise(0)
    )
    
    training_df.write.format("delta").mode("overwrite").saveAsTable(TRAINING_TABLE_NAME)
    logger.info(f"✓ Training dataset updated: {TRAINING_TABLE_NAME}")
    
except Exception as e:
    logger.error(f"Error updating feature store: {str(e)}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validation and Monitoring

# COMMAND ----------

# Feature quality checks
print("\n=== Feature Quality Report ===")
print(f"Refresh timestamp: {datetime.now()}")
print(f"Total companies with features: {feature_df.count()}")
print(f"\nFeature completeness:")

# Check for null values
null_counts = feature_df.select([
    F.sum(F.col(c).isNull().cast("int")).alias(c) 
    for c in feature_df.columns if c not in ["company_id", "company_name"]
])

null_df = null_counts.toPandas().T
null_df.columns = ["null_count"]
null_df = null_df[null_df["null_count"] > 0].sort_values("null_count", ascending=False)

if len(null_df) > 0:
    print("Features with null values:")
    print(null_df.head(10))
else:
    print("✓ No null values found")

# Target distribution
print(f"\nChurn risk distribution:")
training_df.groupBy("is_churn_risk").count().show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Job Complete

# COMMAND ----------

dbutils.notebook.exit({
    "status": "success",
    "timestamp": datetime.now().isoformat(),
    "mode": refresh_mode,
    "companies_updated": feature_df.count()
})
