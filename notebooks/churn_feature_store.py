# Databricks notebook source
# MAGIC %md
# MAGIC # Churn Prediction - Feature Store Setup
# MAGIC 
# MAGIC This notebook creates a Feature Store for churn prediction using ticket and customer data.
# MAGIC Features are computed at the company level to predict churn risk.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Setup and Imports

# COMMAND ----------

from databricks import feature_store
from databricks.feature_store import feature_table
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from datetime import datetime, timedelta
import pyspark.sql.types as T

# Initialize Feature Store client
fs = feature_store.FeatureStoreClient()

# Define catalog and schema (adjust to your environment)
CATALOG = "main"
SCHEMA = "ticket_analytics"
FEATURE_TABLE_NAME = f"{CATALOG}.{SCHEMA}.company_churn_features"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Load Data

# COMMAND ----------

# Load tables
companies_df = spark.table(f"{CATALOG}.{SCHEMA}.companies")
customers_df = spark.table(f"{CATALOG}.{SCHEMA}.customers")
tickets_df = spark.table(f"{CATALOG}.{SCHEMA}.tickets")
interactions_df = spark.table(f"{CATALOG}.{SCHEMA}.ticket_interactions")

print(f"Companies: {companies_df.count()}")
print(f"Customers: {customers_df.count()}")
print(f"Tickets: {tickets_df.count()}")
print(f"Interactions: {interactions_df.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Feature Engineering

# COMMAND ----------

# Define reference date for time-based features
reference_date = F.lit(datetime.now())

# Convert date columns to timestamp
tickets_df = tickets_df.withColumn("created_at", F.to_timestamp("created_at"))
tickets_df = tickets_df.withColumn("updated_at", F.to_timestamp("updated_at"))
tickets_df = tickets_df.withColumn("closed_at", F.to_timestamp("closed_at"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.1 Ticket Volume and Status Features

# COMMAND ----------

ticket_features = tickets_df.groupBy("company_id").agg(
    # Total tickets
    F.count("*").alias("total_tickets"),
    
    # Tickets by status
    F.sum(F.when(F.col("status") == "OPEN", 1).otherwise(0)).alias("tickets_open"),
    F.sum(F.when(F.col("status") == "CLOSED", 1).otherwise(0)).alias("tickets_closed"),
    F.sum(F.when(F.col("status") == "PENDING_CUSTOMER", 1).otherwise(0)).alias("tickets_pending_customer"),
    F.sum(F.when(F.col("status") == "RESOLVED", 1).otherwise(0)).alias("tickets_resolved"),
    
    # Tickets by priority
    F.sum(F.when(F.col("priority") == "HIGH", 1).otherwise(0)).alias("tickets_high_priority"),
    F.sum(F.when(F.col("priority") == "MEDIUM", 1).otherwise(0)).alias("tickets_medium_priority"),
    F.sum(F.when(F.col("priority") == "LOW", 1).otherwise(0)).alias("tickets_low_priority"),
    F.sum(F.when(F.col("priority") == "CRITICAL", 1).otherwise(0)).alias("tickets_critical"),
    
    # Tickets by category
    F.sum(F.when(F.col("category") == "COMPLAINT", 1).otherwise(0)).alias("tickets_complaint"),
    F.sum(F.when(F.col("category") == "TECHNICAL", 1).otherwise(0)).alias("tickets_technical"),
    F.sum(F.when(F.col("category") == "FINANCIAL", 1).otherwise(0)).alias("tickets_financial"),
    
    # SLA and escalation metrics
    F.sum(F.when(F.col("sla_breached") == "TRUE", 1).otherwise(0)).alias("tickets_sla_breached"),
    F.sum(F.when(F.col("escalated") == "TRUE", 1).otherwise(0)).alias("tickets_escalated"),
    
    # Reopened tickets
    F.sum(F.col("reopened_count").cast("int")).alias("total_reopened_count"),
    
    # Churn risk indicators
    F.sum(F.when(F.array_contains(F.split(F.col("tags"), "\\|"), "CHURN_RISK"), 1).otherwise(0)).alias("tickets_churn_risk_tag")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.2 Satisfaction and Sentiment Features

# COMMAND ----------

satisfaction_features = tickets_df.groupBy("company_id").agg(
    # NPS metrics
    F.avg(F.col("nps_score").cast("double")).alias("avg_nps_score"),
    F.min(F.col("nps_score").cast("double")).alias("min_nps_score"),
    F.max(F.col("nps_score").cast("double")).alias("max_nps_score"),
    F.count(F.when(F.col("nps_score").isNotNull(), 1)).alias("nps_responses_count"),
    
    # CSAT metrics
    F.avg(F.col("csat_score").cast("double")).alias("avg_csat_score"),
    F.min(F.col("csat_score").cast("double")).alias("min_csat_score"),
    F.max(F.col("csat_score").cast("double")).alias("max_csat_score"),
    F.count(F.when(F.col("csat_score").isNotNull(), 1)).alias("csat_responses_count"),
    
    # Sentiment analysis
    F.sum(F.when(F.col("sentiment") == "VERY_NEGATIVE", 1).otherwise(0)).alias("sentiment_very_negative_count"),
    F.sum(F.when(F.col("sentiment") == "NEGATIVE", 1).otherwise(0)).alias("sentiment_negative_count"),
    F.sum(F.when(F.col("sentiment") == "NEUTRAL", 1).otherwise(0)).alias("sentiment_neutral_count"),
    F.sum(F.when(F.col("sentiment") == "POSITIVE", 1).otherwise(0)).alias("sentiment_positive_count"),
    F.sum(F.when(F.col("sentiment") == "VERY_POSITIVE", 1).otherwise(0)).alias("sentiment_very_positive_count")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.3 Time-Based Features

# COMMAND ----------

time_features = tickets_df.groupBy("company_id").agg(
    # Resolution time metrics
    F.avg(F.col("resolution_time_hours").cast("double")).alias("avg_resolution_time_hours"),
    F.max(F.col("resolution_time_hours").cast("double")).alias("max_resolution_time_hours"),
    F.min(F.col("resolution_time_hours").cast("double")).alias("min_resolution_time_hours"),
    F.stddev(F.col("resolution_time_hours").cast("double")).alias("std_resolution_time_hours"),
    
    # First response time metrics
    F.avg(F.col("first_response_time_minutes").cast("double")).alias("avg_first_response_time_minutes"),
    F.max(F.col("first_response_time_minutes").cast("double")).alias("max_first_response_time_minutes"),
    
    # Recency metrics
    F.datediff(reference_date, F.max("created_at")).alias("days_since_last_ticket"),
    F.datediff(reference_date, F.min("created_at")).alias("days_since_first_ticket")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.4 Recent Activity Features (Last 30/60/90 days)

# COMMAND ----------

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
    
    if days == 30:
        time_window_features = recent_features
    else:
        time_window_features = time_window_features.join(recent_features, "company_id", "left")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.5 Trend Features

# COMMAND ----------

# Calculate ticket volume trend (comparing last 30 vs previous 30 days)
last_30_days = F.date_sub(reference_date, 30)
last_60_days = F.date_sub(reference_date, 60)

recent_30 = tickets_df.filter(F.col("created_at") >= last_30_days).groupBy("company_id").agg(
    F.count("*").alias("tickets_recent_30")
)

previous_30 = tickets_df.filter(
    (F.col("created_at") >= last_60_days) & (F.col("created_at") < last_30_days)
).groupBy("company_id").agg(
    F.count("*").alias("tickets_previous_30")
)

trend_features = recent_30.join(previous_30, "company_id", "left").select(
    "company_id",
    F.when(
        F.col("tickets_previous_30").isNull() | (F.col("tickets_previous_30") == 0),
        F.lit(0)
    ).otherwise(
        (F.col("tickets_recent_30") - F.col("tickets_previous_30")) / F.col("tickets_previous_30")
    ).alias("ticket_volume_trend_pct")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.6 Interaction Features

# COMMAND ----------

interaction_features = interactions_df.groupBy(
    F.col("ticket_id")
).agg(
    F.count("*").alias("interaction_count"),
    F.avg(F.col("duration_minutes").cast("double")).alias("avg_interaction_duration")
)

ticket_interaction_features = tickets_df.join(
    interaction_features, "ticket_id", "left"
).groupBy("company_id").agg(
    F.avg("interaction_count").alias("avg_interactions_per_ticket"),
    F.max("interaction_count").alias("max_interactions_per_ticket"),
    F.avg("avg_interaction_duration").alias("avg_interaction_duration_minutes")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.7 Customer Features

# COMMAND ----------

customer_features = customers_df.groupBy("company_id").agg(
    F.count("*").alias("total_customers"),
    F.countDistinct("role").alias("distinct_customer_roles")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Combine All Features

# COMMAND ----------

# Start with companies base table
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

# Join all feature groups
feature_df = feature_df \
    .join(ticket_features, "company_id", "left") \
    .join(satisfaction_features, "company_id", "left") \
    .join(time_features, "company_id", "left") \
    .join(time_window_features, "company_id", "left") \
    .join(trend_features, "company_id", "left") \
    .join(ticket_interaction_features, "company_id", "left") \
    .join(customer_features, "company_id", "left")

# Fill nulls with 0 for count features
count_columns = [c for c in feature_df.columns if any(x in c for x in [
    "tickets_", "total_", "sentiment_", "days_", "interaction", "customer"
])]

for col in count_columns:
    if col not in ["company_id", "company_name", "segment", "company_size", "status"]:
        feature_df = feature_df.withColumn(col, F.coalesce(F.col(col), F.lit(0)))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Add Derived Features

# COMMAND ----------

feature_df = feature_df.withColumn(
    "ticket_resolution_rate",
    F.when(F.col("total_tickets") > 0, 
           F.col("tickets_closed") / F.col("total_tickets")
    ).otherwise(0)
).withColumn(
    "sla_breach_rate",
    F.when(F.col("total_tickets") > 0,
           F.col("tickets_sla_breached") / F.col("total_tickets")
    ).otherwise(0)
).withColumn(
    "complaint_rate",
    F.when(F.col("total_tickets") > 0,
           F.col("tickets_complaint") / F.col("total_tickets")
    ).otherwise(0)
).withColumn(
    "critical_high_priority_rate",
    F.when(F.col("total_tickets") > 0,
           (F.col("tickets_critical") + F.col("tickets_high_priority")) / F.col("total_tickets")
    ).otherwise(0)
).withColumn(
    "negative_sentiment_rate",
    F.when(F.col("total_tickets") > 0,
           (F.col("sentiment_very_negative_count") + F.col("sentiment_negative_count")) / F.col("total_tickets")
    ).otherwise(0)
).withColumn(
    "tickets_per_day",
    F.when(F.col("days_as_customer") > 0,
           F.col("total_tickets") / F.col("days_as_customer")
    ).otherwise(0)
).withColumn(
    "tickets_per_customer",
    F.when(F.col("total_customers") > 0,
           F.col("total_tickets") / F.col("total_customers")
    ).otherwise(0)
)

# Add feature computation timestamp
feature_df = feature_df.withColumn("feature_timestamp", F.current_timestamp())

# COMMAND ----------

# Display sample of features
display(feature_df.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Create Feature Store Table

# COMMAND ----------

# Create the feature table
try:
    fs.create_table(
        name=FEATURE_TABLE_NAME,
        primary_keys=["company_id"],
        timestamp_keys=["feature_timestamp"],
        df=feature_df,
        description="Company-level features for churn prediction based on ticket analytics and customer behavior"
    )
    print(f"✓ Feature table created: {FEATURE_TABLE_NAME}")
except Exception as e:
    if "already exists" in str(e).lower():
        print(f"Feature table already exists. Updating with new data...")
        fs.write_table(
            name=FEATURE_TABLE_NAME,
            df=feature_df,
            mode="merge"
        )
        print(f"✓ Feature table updated: {FEATURE_TABLE_NAME}")
    else:
        raise e

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Prepare Training Dataset for AutoML

# COMMAND ----------

# Create training dataset with target variable
# Binary classification: churn_risk_score > 0.7 = high risk of churn
training_df = feature_df.withColumn(
    "is_churn_risk",
    F.when(F.col("churn_risk_score") > 0.7, 1).otherwise(0)
)

# Select features for training (exclude identifiers and target)
exclude_cols = [
    "company_id", "company_name", "feature_timestamp", 
    "churn_risk_score", "status"  # Don't use status as it might leak information
]

feature_columns = [c for c in training_df.columns if c not in exclude_cols]

print(f"Total features for AutoML: {len(feature_columns)}")
print(f"\nTarget variable distribution:")
training_df.groupBy("is_churn_risk").count().show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Save Training Dataset

# COMMAND ----------

# Save to Delta table for AutoML
TRAINING_TABLE_NAME = f"{CATALOG}.{SCHEMA}.company_churn_training_data"

training_df.write.format("delta").mode("overwrite").saveAsTable(TRAINING_TABLE_NAME)

print(f"✓ Training dataset saved: {TRAINING_TABLE_NAME}")
print(f"\nTo use with AutoML:")
print(f"1. Go to Machine Learning > AutoML")
print(f"2. Select table: {TRAINING_TABLE_NAME}")
print(f"3. Set target column: is_churn_risk")
print(f"4. Select problem type: Classification")
print(f"5. Start AutoML training")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Feature Importance Analysis

# COMMAND ----------

# Display key statistics about features
print("Feature Summary Statistics:")
print("-" * 80)

numeric_features = [
    "total_tickets", "tickets_open", "tickets_complaint", 
    "tickets_sla_breached", "avg_nps_score", "avg_csat_score",
    "avg_resolution_time_hours", "tickets_last_30_days",
    "ticket_resolution_rate", "sla_breach_rate", "complaint_rate",
    "negative_sentiment_rate"
]

summary_df = feature_df.select(numeric_features).summary()
display(summary_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Export Feature Metadata

# COMMAND ----------

# Create feature metadata for documentation
feature_metadata = spark.createDataFrame([
    ("company_id", "string", "primary_key", "Unique company identifier"),
    ("total_tickets", "integer", "volume", "Total number of tickets created by company"),
    ("tickets_open", "integer", "volume", "Number of tickets currently open"),
    ("tickets_closed", "integer", "volume", "Number of tickets that are closed"),
    ("tickets_complaint", "integer", "category", "Number of complaint tickets"),
    ("tickets_technical", "integer", "category", "Number of technical tickets"),
    ("tickets_financial", "integer", "category", "Number of financial tickets"),
    ("tickets_sla_breached", "integer", "quality", "Number of tickets with SLA breach"),
    ("tickets_escalated", "integer", "quality", "Number of escalated tickets"),
    ("tickets_churn_risk_tag", "integer", "risk", "Number of tickets tagged as churn risk"),
    ("avg_nps_score", "double", "satisfaction", "Average Net Promoter Score"),
    ("avg_csat_score", "double", "satisfaction", "Average Customer Satisfaction Score"),
    ("sentiment_very_negative_count", "integer", "sentiment", "Count of very negative sentiment"),
    ("sentiment_negative_count", "integer", "sentiment", "Count of negative sentiment"),
    ("avg_resolution_time_hours", "double", "time", "Average time to resolve tickets in hours"),
    ("avg_first_response_time_minutes", "double", "time", "Average first response time in minutes"),
    ("days_since_last_ticket", "integer", "time", "Days since last ticket was created"),
    ("tickets_last_30_days", "integer", "trend", "Number of tickets in last 30 days"),
    ("tickets_last_60_days", "integer", "trend", "Number of tickets in last 60 days"),
    ("tickets_last_90_days", "integer", "trend", "Number of tickets in last 90 days"),
    ("ticket_volume_trend_pct", "double", "trend", "Percentage change in ticket volume"),
    ("ticket_resolution_rate", "double", "derived", "Ratio of closed to total tickets"),
    ("sla_breach_rate", "double", "derived", "Ratio of SLA breached tickets"),
    ("complaint_rate", "double", "derived", "Ratio of complaint tickets"),
    ("negative_sentiment_rate", "double", "derived", "Ratio of negative sentiment tickets"),
    ("tickets_per_customer", "double", "derived", "Average tickets per customer in company"),
    ("is_churn_risk", "integer", "target", "Binary target: 1 if churn risk score > 0.7")
], ["feature_name", "data_type", "feature_group", "description"])

METADATA_TABLE = f"{CATALOG}.{SCHEMA}.churn_feature_metadata"
feature_metadata.write.format("delta").mode("overwrite").saveAsTable(METADATA_TABLE)

print(f"✓ Feature metadata saved: {METADATA_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC 
# MAGIC ### Feature Store Created Successfully! ✓
# MAGIC 
# MAGIC **What was created:**
# MAGIC - Feature Store Table: `{FEATURE_TABLE_NAME}`
# MAGIC - Training Dataset: `{TRAINING_TABLE_NAME}`
# MAGIC - Feature Metadata: `{METADATA_TABLE}`
# MAGIC 
# MAGIC **Key Features Generated:**
# MAGIC - 60+ features across multiple dimensions
# MAGIC - Ticket volume and status metrics
# MAGIC - Customer satisfaction scores (NPS, CSAT)
# MAGIC - Sentiment analysis
# MAGIC - Time-based trends (30/60/90 days)
# MAGIC - Resolution and response times
# MAGIC - Derived rates and ratios
# MAGIC 
# MAGIC **Next Steps:**
# MAGIC 1. Use the training dataset with Databricks AutoML
# MAGIC 2. Monitor feature drift over time
# MAGIC 3. Schedule periodic feature updates
# MAGIC 4. Deploy the model for real-time predictions
