# Databricks notebook source
# MAGIC %md
# MAGIC # Customer Support Tickets Agent - Complete Setup and Analysis
# MAGIC
# MAGIC ## 🎯 Objective
# MAGIC This notebook provides a complete end-to-end solution for analyzing customer support tickets using Databricks and GenAI.
# MAGIC
# MAGIC ## 📋 What this notebook does:
# MAGIC 1. Creates Delta tables for tickets data
# MAGIC 2. Loads data from CSV files
# MAGIC 3. Validates data quality
# MAGIC 4. Performs executive analysis
# MAGIC 5. Identifies churn risks
# MAGIC 6. Generates AI-powered insights
# MAGIC
# MAGIC ## ⚙️ Prerequisites:
# MAGIC - CSV files uploaded to DBFS at `/FileStore/tickets/`
# MAGIC - Databricks Runtime with ML or above
# MAGIC
# MAGIC ---

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📦 Step 1: Configuration

# COMMAND ----------

# DBTITLE 1,Cell 3
# Configuration parameters
CSV_BASE_PATH = "file:/Workspace/Users/fabio.goncalves@databricks.com/databricks-tickets-agent/data/pt-br"  # Update this path if your CSVs are in a different location
CATALOG_NAME = "fabio_goncalves"  # Change to your Unity Catalog name if using UC
SCHEMA_NAME = "tickets_agent"  # Change to your schema name
TABLE_PREFIX = ""  # Optional prefix for table names
VOLUME = "tickets_csv_data" 
VOLUME_PATH = f"/Volumes/{CATALOG_NAME}/{SCHEMA_NAME}/{TABLE_PREFIX}{VOLUME}" 
VOLUME_NAME = f"{CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_PREFIX}{VOLUME}"

# Full table names
COMPANIES_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_PREFIX}companies"
CUSTOMERS_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_PREFIX}customers"
AGENTS_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_PREFIX}agents"
TICKETS_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_PREFIX}tickets"
INTERACTIONS_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_PREFIX}ticket_interactions"

print(f"✓ Configuration loaded")
print(f"  CSV Path: {CSV_BASE_PATH}")
print(f"  Catalog: {CATALOG_NAME}")
print(f"  Schema: {SCHEMA_NAME}")
print(f"  Volume: {VOLUME_NAME}")
print(f"  Volume_path: {VOLUME_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🗂️ Step 2: Create Database Schema

# COMMAND ----------

# Create schema if it doesn't exist
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG_NAME}.{SCHEMA_NAME}")
spark.sql(f"USE {CATALOG_NAME}.{SCHEMA_NAME}")

print(f"✓ Schema {SCHEMA_NAME} is ready")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🏗️ Step 3: Create Delta Tables and Volume
# MAGIC
# MAGIC Creating Volume:
# MAGIC - **tickets_csv_data**: csv data files
# MAGIC Creating 5 related tables:
# MAGIC - **companies**: Customer companies using payment processing services
# MAGIC - **customers**: Individual users who open support tickets
# MAGIC - **agents**: Support agents handling tickets
# MAGIC - **tickets**: Main tickets table with all ticket information
# MAGIC - **ticket_interactions**: Interaction history/dialogue for each ticket

# COMMAND ----------

# Drop existing tables (optional - comment out if you want to preserve existing data)
spark.sql(f"DROP VOLUME {VOLUME_NAME}")
spark.sql(f"DROP TABLE IF EXISTS {INTERACTIONS_TABLE}")
spark.sql(f"DROP TABLE IF EXISTS {TICKETS_TABLE}")
spark.sql(f"DROP TABLE IF EXISTS {CUSTOMERS_TABLE}")
spark.sql(f"DROP TABLE IF EXISTS {AGENTS_TABLE}")
spark.sql(f"DROP TABLE IF EXISTS {COMPANIES_TABLE}")

print("✓ Existing tables dropped (if any)")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Create Data Volume 

# COMMAND ----------

spark.sql(f"""
CREATE VOLUME {VOLUME_NAME}""")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Create COMPANIES table

# COMMAND ----------

spark.sql(f"""
CREATE TABLE {COMPANIES_TABLE} (
  company_id STRING NOT NULL COMMENT 'Unique identifier for the company',
  company_name STRING NOT NULL COMMENT 'Company legal name',
  cnpj STRING NOT NULL COMMENT 'Brazilian company tax ID - PII',
  segment STRING COMMENT 'Business segment (retail, restaurant, services, etc)',
  company_size STRING COMMENT 'Company size: SMALL, MEDIUM, LARGE, ENTERPRISE',
  contract_start_date DATE COMMENT 'Date when company started using the service',
  monthly_transaction_volume DECIMAL(15,2) COMMENT 'Average monthly transaction volume in BRL',
  status STRING COMMENT 'Account status: ACTIVE, SUSPENDED, CANCELLED',
  churn_risk_score DECIMAL(3,2) COMMENT 'Churn risk score from 0.00 to 1.00',
  created_at TIMESTAMP COMMENT 'Record creation timestamp'
)
USING DELTA
COMMENT 'Customer companies using payment processing services'
TBLPROPERTIES (
  'delta.minReaderVersion' = '1',
  'delta.minWriterVersion' = '2',
  'pii.columns' = 'cnpj'
)
""")

print(f"✓ Table created: {COMPANIES_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Create CUSTOMERS table

# COMMAND ----------

spark.sql(f"""
CREATE TABLE {CUSTOMERS_TABLE} (
  customer_id STRING NOT NULL COMMENT 'Unique identifier for the customer',
  company_id STRING NOT NULL COMMENT 'Foreign key to companies table',
  customer_name STRING NOT NULL COMMENT 'Customer full name - PII',
  email STRING NOT NULL COMMENT 'Customer email address - PII',
  cpf STRING COMMENT 'Brazilian individual tax ID - PII',
  birth_date DATE COMMENT 'Date of birth - PII',
  phone STRING COMMENT 'Phone number - PII',
  role STRING COMMENT 'Role in company: OWNER, MANAGER, OPERATOR, FINANCIAL',
  created_at TIMESTAMP COMMENT 'Record creation timestamp'
)
USING DELTA
COMMENT 'Individual customers who interact with support'
TBLPROPERTIES (
  'delta.minReaderVersion' = '1',
  'delta.minWriterVersion' = '2',
  'pii.columns' = 'customer_name,email,cpf,birth_date,phone'
)
""")

print(f"✓ Table created: {CUSTOMERS_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Create AGENTS table

# COMMAND ----------

spark.sql(f"""
CREATE TABLE {AGENTS_TABLE} (
  agent_id STRING NOT NULL COMMENT 'Unique identifier for the agent',
  agent_name STRING NOT NULL COMMENT 'Agent full name',
  email STRING NOT NULL COMMENT 'Agent email address',
  team STRING COMMENT 'Support team: L1_SUPPORT, L2_TECHNICAL, L3_SPECIALIST, FINANCIAL',
  specialization STRING COMMENT 'Agent specialization area',
  hire_date DATE COMMENT 'Agent hire date',
  avg_csat DECIMAL(3,2) COMMENT 'Average CSAT score (0-5)',
  tickets_resolved INT COMMENT 'Total tickets resolved',
  status STRING COMMENT 'Agent status: ACTIVE, INACTIVE, ON_LEAVE',
  created_at TIMESTAMP COMMENT 'Record creation timestamp'
)
USING DELTA
COMMENT 'Support agents handling customer tickets'
""")

print(f"✓ Table created: {AGENTS_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Create TICKETS table

# COMMAND ----------

spark.sql(f"""
CREATE TABLE {TICKETS_TABLE} (
  ticket_id STRING NOT NULL COMMENT 'Unique ticket identifier',
  company_id STRING NOT NULL COMMENT 'Foreign key to companies table',
  customer_id STRING NOT NULL COMMENT 'Foreign key to customers table',
  agent_id STRING COMMENT 'Foreign key to agents table - assigned agent',
  created_at TIMESTAMP NOT NULL COMMENT 'Ticket creation timestamp',
  updated_at TIMESTAMP COMMENT 'Last update timestamp',
  closed_at TIMESTAMP COMMENT 'Ticket closure timestamp',
  status STRING NOT NULL COMMENT 'Ticket status: OPEN, IN_PROGRESS, PENDING_CUSTOMER, RESOLVED, CLOSED, CANCELLED',
  priority STRING NOT NULL COMMENT 'Priority level: LOW, MEDIUM, HIGH, CRITICAL',
  category STRING NOT NULL COMMENT 'Ticket category: TECHNICAL, FINANCIAL, COMMERCIAL, COMPLAINT, INFORMATION',
  subcategory STRING COMMENT 'Ticket subcategory for detailed classification',
  channel STRING NOT NULL COMMENT 'Contact channel: EMAIL, PHONE, CHAT, WHATSAPP, PORTAL',
  subject STRING NOT NULL COMMENT 'Ticket subject/title',
  description STRING NOT NULL COMMENT 'Detailed ticket description',
  tags ARRAY<STRING> COMMENT 'Tags for categorization and search',
  resolution_time_hours DECIMAL(10,2) COMMENT 'Time to resolve in hours',
  first_response_time_minutes INT COMMENT 'Time to first response in minutes',
  sla_breached BOOLEAN COMMENT 'Indicates if SLA was breached',
  nps_score INT COMMENT 'Net Promoter Score: 0-10 scale',
  csat_score DECIMAL(3,2) COMMENT 'Customer Satisfaction Score: 1.00 to 5.00',
  sentiment STRING COMMENT 'Sentiment analysis: POSITIVE, NEUTRAL, NEGATIVE, VERY_NEGATIVE',
  escalated BOOLEAN COMMENT 'Indicates if ticket was escalated',
  reopened_count INT COMMENT 'Number of times ticket was reopened',
  related_ticket_ids ARRAY<STRING> COMMENT 'Related ticket IDs'
)
USING DELTA
COMMENT 'Main customer support tickets table'
TBLPROPERTIES (
  'delta.minReaderVersion' = '1',
  'delta.minWriterVersion' = '2'
)
""")

print(f"✓ Table created: {TICKETS_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Create TICKET_INTERACTIONS table

# COMMAND ----------

spark.sql(f"""
CREATE TABLE {INTERACTIONS_TABLE} (
  interaction_id STRING NOT NULL COMMENT 'Unique interaction identifier',
  ticket_id STRING NOT NULL COMMENT 'Foreign key to tickets table',
  interaction_timestamp TIMESTAMP NOT NULL COMMENT 'When the interaction occurred',
  author_type STRING NOT NULL COMMENT 'Who wrote: CUSTOMER, AGENT, SYSTEM',
  author_id STRING COMMENT 'ID of the author (customer_id or agent_id)',
  author_name STRING COMMENT 'Name of the author',
  message STRING NOT NULL COMMENT 'Interaction message content',
  interaction_type STRING COMMENT 'Type: COMMENT, STATUS_CHANGE, ESCALATION, INTERNAL_NOTE',
  channel STRING COMMENT 'Channel used for this interaction',
  attachments ARRAY<STRING> COMMENT 'List of attachment file names'
)
USING DELTA
COMMENT 'Ticket interaction history and dialogue'
TBLPROPERTIES (
  'delta.minReaderVersion' = '1',
  'delta.minWriterVersion' = '2'
)
""")

print(f"✓ Table created: {INTERACTIONS_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📥 Step 4: Load Data from CSV Files
# MAGIC
# MAGIC Loading data in the correct order to respect foreign key relationships:
# MAGIC 1. Companies (parent)
# MAGIC 2. Agents (parent)
# MAGIC 3. Customers (references companies)
# MAGIC 4. Tickets (references companies, customers, agents)
# MAGIC 5. Ticket Interactions (references tickets)

# COMMAND ----------

# DBTITLE 1,Cell 21
# Copia todos os arquivos da pasta do workspace "data/pt-br" para o volume VOLUME_NAME
src_path = "file:/Workspace/Users/fabio.goncalves@databricks.com/databricks-tickets-agent/data/pt-br/"
dst_path = f"/Volumes/{VOLUME_NAME.replace('.', '/')}/"

files = dbutils.fs.ls(src_path)
for file in files:
    dbutils.fs.cp(file.path, dst_path + file.name)
print(f"✓ Arquivos copiados de {src_path} para {dst_path}")

# COMMAND ----------

files = dbutils.fs.ls(f"{VOLUME_PATH}")
display(files)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Load COMPANIES

# COMMAND ----------

# DBTITLE 1,Cell 20
from pyspark.sql.types import *

# Define schema for companies
companies_schema = StructType([
    StructField("company_id", StringType(), False),
    StructField("company_name", StringType(), False),
    StructField("cnpj", StringType(), False),
    StructField("segment", StringType(), True),
    StructField("company_size", StringType(), True),
    StructField("contract_start_date", DateType(), True),
    StructField("monthly_transaction_volume", DecimalType(15,2), True),
    StructField("status", StringType(), True),
    StructField("churn_risk_score", DecimalType(3,2), True),
    StructField("created_at", TimestampType(), True)
])

df_companies = (spark.read
    .option("header", "true")
    .option("multiLine", "true")
    .option("escape", '"')
    .schema(companies_schema)
    .csv(f"{CSV_BASE_PATH}/companies.csv"))

df_companies.write.mode("overwrite").saveAsTable(f"{COMPANIES_TABLE}")
display(df_companies)

display(df_companies)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Load AGENTS

# COMMAND ----------

# Define schema for agents
agents_schema = StructType([
    StructField("agent_id", StringType(), False),
    StructField("agent_name", StringType(), False),
    StructField("email", StringType(), False),
    StructField("team", StringType(), True),
    StructField("specialization", StringType(), True),
    StructField("hire_date", DateType(), True),
    StructField("avg_csat", DecimalType(3,2), True),
    StructField("tickets_resolved", IntegerType(), True),
    StructField("status", StringType(), True),
    StructField("created_at", TimestampType(), True)
])

df_agents = (spark.read
    .option("header", "true")
    .option("multiLine", "true")
    .option("escape", '"')
    .schema(agents_schema)
    .csv(f"{CSV_BASE_PATH}/agents.csv")
)

df_agents.write.mode("overwrite").saveAsTable(f"{AGENTS_TABLE}")
display(df_agents)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Load CUSTOMERS

# COMMAND ----------

# Define schema for customers
customers_schema = StructType([
    StructField("customer_id", StringType(), False),
    StructField("company_id", StringType(), False),
    StructField("customer_name", StringType(), False),
    StructField("email", StringType(), False),
    StructField("cpf", StringType(), True),
    StructField("birth_date", DateType(), True),
    StructField("phone", StringType(), True),
    StructField("role", StringType(), True),
    StructField("created_at", TimestampType(), True)
])

df_customers = (spark.read
    .option("header", "true")
    .option("multiLine", "true")
    .option("escape", '"')
    .schema(customers_schema)
    .csv(f"{CSV_BASE_PATH}/customers.csv")
)

df_customers.write.mode("overwrite").saveAsTable(f"{CUSTOMERS_TABLE}")

display(df_customers)


# COMMAND ----------

# MAGIC %md
# MAGIC ### Load TICKETS

# COMMAND ----------

# Define schema for tickets
tickets_schema = StructType([
    StructField("ticket_id", StringType(), False),
    StructField("company_id", StringType(), False),
    StructField("customer_id", StringType(), False),
    StructField("agent_id", StringType(), True),
    StructField("created_at", TimestampType(), False),
    StructField("updated_at", TimestampType(), True),
    StructField("closed_at", TimestampType(), True),
    StructField("status", StringType(), False),
    StructField("priority", StringType(), False),
    StructField("category", StringType(), False),
    StructField("subcategory", StringType(), True),
    StructField("channel", StringType(), False),
    StructField("subject", StringType(), False),
    StructField("description", StringType(), False),
    StructField("tags", StringType(), True),  # Will convert to array
    StructField("resolution_time_hours", DecimalType(10,2), True),
    StructField("first_response_time_minutes", IntegerType(), True),
    StructField("sla_breached", StringType(), True),  # Will convert to boolean
    StructField("nps_score", IntegerType(), True),
    StructField("csat_score", DecimalType(3,2), True),
    StructField("sentiment", StringType(), True),
    StructField("escalated", StringType(), True),  # Will convert to boolean
    StructField("reopened_count", IntegerType(), True),
    StructField("related_ticket_ids", StringType(), True)  # Will convert to array
])

df_tickets = (spark.read
    .option("header", "true")
    .option("multiLine", "true")
    .option("escape", '"')
    .schema(tickets_schema)
    .csv(f"{CSV_BASE_PATH}/tickets.csv")
)

# Transform data
df_tickets_transformed = (df_tickets
    .withColumn("tags", F.when(F.col("tags").isNotNull(), F.split(F.col("tags"), "\\|")).otherwise(F.array()))
    .withColumn("sla_breached", F.when(F.col("sla_breached") == "TRUE", True).when(F.col("sla_breached") == "FALSE", False).otherwise(None))
    .withColumn("escalated", F.when(F.col("escalated") == "TRUE", True).when(F.col("escalated") == "FALSE", False).otherwise(None))
    .withColumn("related_ticket_ids", F.when(F.col("related_ticket_ids").isNotNull() & (F.col("related_ticket_ids") != ""), 
                                            F.split(F.col("related_ticket_ids"), "\\|")).otherwise(F.array()))
    .withColumn("agent_id", F.when(F.col("agent_id") == "", None).otherwise(F.col("agent_id")))
)

df_tickets_transformed.write.mode("overwrite").saveAsTable(f"{TICKETS_TABLE}")

display(df_tickets_transformed)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Load TICKET_INTERACTIONS

# COMMAND ----------

# Define schema for interactions
interactions_schema = StructType([
    StructField("interaction_id", StringType(), False),
    StructField("ticket_id", StringType(), False),
    StructField("interaction_timestamp", TimestampType(), False),
    StructField("author_type", StringType(), False),
    StructField("author_id", StringType(), True),
    StructField("author_name", StringType(), True),
    StructField("message", StringType(), False),
    StructField("interaction_type", StringType(), True),
    StructField("channel", StringType(), True),
    StructField("attachments", StringType(), True)  # Will convert to array
])

df_interactions = (spark.read
    .option("header", "true")
    .option("multiLine", "true")
    .option("escape", '"')
    .schema(interactions_schema)
    .csv(f"{CSV_BASE_PATH}/ticket_interactions.csv")
)

# Transform data
df_interactions_transformed = (df_interactions
    .withColumn("attachments", F.when(F.col("attachments").isNotNull() & (F.col("attachments") != ""), 
                                     F.split(F.col("attachments"), "\\|")).otherwise(F.array()))
)

df_interactions_transformed.write.mode("overwrite").saveAsTable(f"{INTERACTIONS_TABLE}")

display(df_interactions_transformed)

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Step 5: Validate Data Load

# COMMAND ----------

# Verify record counts
print("="*70)
print("DATA VALIDATION")
print("="*70)

validation_results = []

for table_name, display_name in [
    (COMPANIES_TABLE, "Companies"),
    (CUSTOMERS_TABLE, "Customers"),
    (AGENTS_TABLE, "Agents"),
    (TICKETS_TABLE, "Tickets"),
    (INTERACTIONS_TABLE, "Ticket Interactions")
]:
    count = spark.table(table_name).count()
    validation_results.append((display_name, count))
    print(f"{display_name:.<30} {count:>6} records")

print("="*70)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🚀 Step 6: Optimize Tables
# MAGIC
# MAGIC Apply Z-ordering and collect statistics for better query performance

# COMMAND ----------

print("Optimizing tables...")

# Optimize companies
spark.sql(f"OPTIMIZE {COMPANIES_TABLE} ZORDER BY (company_id, status)")
print(f"✓ Optimized {COMPANIES_TABLE}")

# Optimize customers
spark.sql(f"OPTIMIZE {CUSTOMERS_TABLE} ZORDER BY (company_id, customer_id)")
print(f"✓ Optimized {CUSTOMERS_TABLE}")

# Optimize agents
spark.sql(f"OPTIMIZE {AGENTS_TABLE} ZORDER BY (agent_id, team)")
print(f"✓ Optimized {AGENTS_TABLE}")

# Optimize tickets
spark.sql(f"OPTIMIZE {TICKETS_TABLE} ZORDER BY (created_at, status, priority, company_id)")
print(f"✓ Optimized {TICKETS_TABLE}")

# Optimize interactions
spark.sql(f"OPTIMIZE {INTERACTIONS_TABLE} ZORDER BY (ticket_id, interaction_timestamp)")
print(f"✓ Optimized {INTERACTIONS_TABLE}")

print("\n✅ All tables optimized")

# COMMAND ----------

# Collect statistics
print("\nCollecting statistics...")

for table in [COMPANIES_TABLE, CUSTOMERS_TABLE, AGENTS_TABLE, TICKETS_TABLE, INTERACTIONS_TABLE]:
    spark.sql(f"ANALYZE TABLE {table} COMPUTE STATISTICS FOR ALL COLUMNS")
    print(f"✓ Statistics collected for {table}")

print("\n✅ All statistics collected")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 📊 ANALYSIS SECTION
# MAGIC ---

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📈 Analysis 1: Weekly Executive Summary
# MAGIC
# MAGIC **Business Question:** "What's happening this week?"

# COMMAND ----------

# Load tickets data
tickets_df = spark.table(TICKETS_TABLE)
companies_df = spark.table(COMPANIES_TABLE)
customers_df = spark.table(CUSTOMERS_TABLE)
agents_df = spark.table(AGENTS_TABLE)
interactions_df = spark.table(INTERACTIONS_TABLE)

# Filter for recent tickets (last 7 days)
recent_tickets = tickets_df.filter(
    F.col("created_at") >= F.date_sub(F.current_date(), 7)
)

print(f"Analyzing tickets from last 7 days...")
print(f"Total tickets in period: {recent_tickets.count()}")

# COMMAND ----------

# Calculate key metrics
weekly_summary = recent_tickets.agg(
    F.count("*").alias("total_tickets"),
    F.sum(F.when(F.col("status") == "OPEN", 1).otherwise(0)).alias("open_tickets"),
    F.sum(F.when(F.col("status") == "IN_PROGRESS", 1).otherwise(0)).alias("in_progress"),
    F.sum(F.when(F.col("status") == "CLOSED", 1).otherwise(0)).alias("closed_tickets"),
    F.sum(F.when(F.col("priority") == "CRITICAL", 1).otherwise(0)).alias("critical_tickets"),
    F.sum(F.when(F.col("priority") == "HIGH", 1).otherwise(0)).alias("high_priority"),
    F.round(F.avg(F.when(F.col("status").isin("RESOLVED", "CLOSED"), F.col("resolution_time_hours"))), 2).alias("avg_resolution_hours"),
    F.round(F.avg("first_response_time_minutes"), 2).alias("avg_first_response_minutes"),
    F.sum(F.when(F.col("sla_breached") == True, 1).otherwise(0)).alias("sla_breaches"),
    F.round(F.avg("csat_score"), 2).alias("avg_csat"),
    F.round(F.avg("nps_score"), 1).alias("avg_nps")
)

display(weekly_summary)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📊 Analysis 2: Top Issues and Trends

# COMMAND ----------

# Category breakdown
category_summary = recent_tickets.groupBy("category", "subcategory").agg(
    F.count("*").alias("ticket_count"),
    F.round(F.avg(F.when(F.col("status").isin("RESOLVED", "CLOSED"), F.col("resolution_time_hours"))), 2).alias("avg_resolution_hours"),
    F.sum(F.when(F.col("priority").isin("HIGH", "CRITICAL"), 1).otherwise(0)).alias("urgent_count"),
    F.round(F.avg("csat_score"), 2).alias("avg_csat")
).orderBy(F.desc("ticket_count"))

print("Top 10 Issues This Week:")
display(category_summary.limit(10))

# COMMAND ----------

from pyspark.sql.window import Window

# Status distribution
status_dist = recent_tickets.groupBy("status").agg(
    F.count("*").alias("count")
).withColumn(
    "percentage",
    F.round(F.col("count") * 100.0 / F.sum("count").over(Window.partitionBy()), 2)
).orderBy(F.desc("count"))

display(status_dist)

# COMMAND ----------

# MAGIC %md
# MAGIC ## ⚠️ Analysis 3: Churn Risk Detection
# MAGIC
# MAGIC **Business Question:** "Which customers are at risk of leaving?"

# COMMAND ----------

# Identify companies at risk
churn_risk = (
    companies_df
    .filter(F.col("churn_risk_score") > 0.5)
    .join(
        tickets_df
        .filter(F.col("created_at") >= F.date_sub(F.current_date(), 30))
        .groupBy("company_id").agg(
            F.count("*").alias("recent_tickets"),
            F.sum(F.when(F.col("priority").isin("HIGH", "CRITICAL"), 1).otherwise(0)).alias("urgent_tickets"),
            F.sum(F.when(F.col("category") == "COMPLAINT", 1).otherwise(0)).alias("complaints"),
            F.sum(F.when(F.col("sla_breached") == True, 1).otherwise(0)).alias("sla_breaches"),
            F.round(F.avg("csat_score"), 2).alias("avg_csat"),
            F.round(F.avg("nps_score"), 1).alias("avg_nps"),
            F.collect_set("category").alias("issue_categories")
        ),
        "company_id",
        "left"
    )
    .select(
        "company_name",
        "segment",
        "company_size",
        "churn_risk_score",
        "monthly_transaction_volume",
        "recent_tickets",
        "urgent_tickets",
        "complaints",
        "sla_breaches",
        "avg_csat",
        "avg_nps",
        "issue_categories"
    )
    .orderBy(F.desc("churn_risk_score"))
)

print("Companies at High Risk of Churn:")
display(churn_risk.limit(20))

# COMMAND ----------

# Add recommended actions
churn_with_actions = churn_risk.withColumn(
    "recommended_action",
    F.when((F.col("churn_risk_score") > 0.8) & (F.col("complaints") >= 2), 
           "🔴 IMMEDIATE: Schedule executive call")
    .when((F.col("churn_risk_score") > 0.7) & (F.col("urgent_tickets") >= 3), 
          "🟠 URGENT: Escalate to account manager")
    .when((F.col("churn_risk_score") > 0.6) & (F.col("avg_csat") < 3.0), 
          "🟡 HIGH: Proactive outreach needed")
    .when(F.col("sla_breaches") >= 2,
          "🟡 MEDIUM: Review SLA compliance")
    .otherwise("🟢 Monitor closely")
)

display(churn_with_actions.select(
    "company_name", 
    "churn_risk_score", 
    "recent_tickets", 
    "complaints", 
    "avg_csat",
    "recommended_action"
))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📉 Analysis 4: SLA Performance

# COMMAND ----------

# SLA compliance by priority
sla_performance = (
    tickets_df
    .filter(F.col("status").isin("RESOLVED", "CLOSED"))
    .filter(F.col("created_at") >= F.date_sub(F.current_date(), 30))
    .groupBy("priority")
    .agg(
        F.count("*").alias("total_tickets"),
        F.sum(F.when(F.col("sla_breached") == True, 1).otherwise(0)).alias("sla_breached"),
        F.sum(F.when(F.col("sla_breached") == False, 1).otherwise(0)).alias("sla_met"),
        F.round(F.avg("resolution_time_hours"), 2).alias("avg_resolution_hours"),
        F.round(F.min("resolution_time_hours"), 2).alias("min_resolution_hours"),
        F.round(F.max("resolution_time_hours"), 2).alias("max_resolution_hours")
    )
    .withColumn(
        "sla_compliance_pct",
        F.round(F.col("sla_met") * 100.0 / F.col("total_tickets"), 2)
    )
    .withColumn(
        "sla_target_hours",
        F.when(F.col("priority") == "CRITICAL", 4)
        .when(F.col("priority") == "HIGH", 8)
        .when(F.col("priority") == "MEDIUM", 24)
        .when(F.col("priority") == "LOW", 48)
    )
)

print("SLA Performance by Priority (Last 30 Days):")
display(sla_performance)

# COMMAND ----------

# Recent SLA breaches
recent_sla_breaches = (
    tickets_df
    .filter(F.col("sla_breached") == True)
    .filter(F.col("created_at") >= F.date_sub(F.current_date(), 7))
    .join(companies_df.select("company_id", "company_name"), "company_id")
    .join(customers_df.select("customer_id", "customer_name"), "customer_id")
    .join(agents_df.select("agent_id", "agent_name"), "agent_id", "left")
    .select(
        "ticket_id",
        "created_at",
        "closed_at",
        "priority",
        "category",
        "subject",
        "resolution_time_hours",
        "company_name",
        "customer_name",
        "agent_name"
    )
    .orderBy("priority", F.desc("created_at"))
)

print("Recent SLA Breaches (Last 7 Days):")
display(recent_sla_breaches.limit(20))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 👥 Analysis 5: Agent Performance

# COMMAND ----------

# Agent performance metrics (last 30 days)
agent_performance = (
    agents_df
    .filter(F.col("status") == "ACTIVE")
    .join(
        tickets_df
        .filter(F.col("created_at") >= F.date_sub(F.current_date(), 30))
        .groupBy("agent_id").agg(
            F.count("*").alias("tickets_handled"),
            F.sum(F.when(F.col("status").isin("RESOLVED", "CLOSED"), 1).otherwise(0)).alias("tickets_resolved_30d"),
            F.round(F.avg("resolution_time_hours"), 2).alias("avg_resolution_hours"),
            F.round(F.avg("first_response_time_minutes"), 2).alias("avg_first_response_min"),
            F.round(F.avg("csat_score"), 2).alias("avg_csat_30d"),
            F.round(F.avg("nps_score"), 1).alias("avg_nps_30d"),
            F.sum(F.when(F.col("sla_breached") == True, 1).otherwise(0)).alias("sla_breaches"),
            F.sum(F.when(F.col("escalated") == True, 1).otherwise(0)).alias("escalations")
        ),
        "agent_id",
        "left"
    )
    .select(
        "agent_name",
        "team",
        "specialization",
        "tickets_handled",
        "tickets_resolved_30d",
        "avg_resolution_hours",
        "avg_first_response_min",
        "avg_csat_30d",
        "avg_nps_30d",
        "sla_breaches",
        "escalations"
    )
    .withColumn(
        "resolution_rate_pct",
        F.round(F.col("tickets_resolved_30d") * 100.0 / F.col("tickets_handled"), 2)
    )
    .filter(F.col("tickets_handled").isNotNull())
    .orderBy(F.desc("tickets_handled"))
)

print("Agent Performance (Last 30 Days):")
display(agent_performance)

# COMMAND ----------

# Team performance comparison
team_performance = (
    agents_df
    .filter(F.col("status") == "ACTIVE")
    .join(
        tickets_df.filter(F.col("created_at") >= F.date_sub(F.current_date(), 30)),
        "agent_id",
        "left"
    )
    .groupBy("team")
    .agg(
        F.countDistinct("agent_id").alias("agent_count"),
        F.count("ticket_id").alias("total_tickets"),
        F.round(F.avg("resolution_time_hours"), 2).alias("avg_resolution_hours"),
        F.round(F.avg("csat_score"), 2).alias("avg_csat"),
        F.sum(F.when(F.col("sla_breached") == True, 1).otherwise(0)).alias("sla_breaches")
    )
    .withColumn(
        "sla_compliance_pct",
        F.round((F.col("total_tickets") - F.col("sla_breaches")) * 100.0 / F.col("total_tickets"), 2)
    )
    .orderBy(F.desc("total_tickets"))
)

print("Team Performance Comparison:")
display(team_performance)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 😊 Analysis 6: Sentiment and Satisfaction

# COMMAND ----------

# Unifica o assunto do ticket e todas as mensagens das interações, e analisa o sentimento usando ai_analyze_sentiment
from pyspark.sql.functions import col, concat_ws, collect_list, lit, coalesce, trim

# Unir todas as mensagens das interações por ticket_id
interactions_text = (
    interactions_df
    .groupBy("ticket_id")
    .agg(concat_ws(" ", collect_list(trim(col("message")))).alias("all_messages"))
)

# Unir assunto do ticket com as mensagens das interações
ticket_text_df = (
    tickets_df
    .select("ticket_id", "subject")
    .join(interactions_text, "ticket_id", "left")
    .withColumn(
        "full_text",
        concat_ws(" ", coalesce(col("subject"), lit("")), coalesce(col("all_messages"), lit("")))
    )
)

# Analisar sentimento usando ai_analyze_sentiment (via SQL)
ticket_text_df.createOrReplaceTempView("vw_ticket_text")

sentiment_trends = spark.sql("""
    SELECT
        ticket_id,
        subject,
        all_messages,
        full_text,
        ai_analyze_sentiment(full_text) AS sentiment
    FROM vw_ticket_text
""")

print("Sentimento dos tickets (assunto + interações):")
display(sentiment_trends)

# COMMAND ----------

# Sentiment distribution over time (last 90 days)
sentiment_trends = (
    tickets_df
    .filter(F.col("created_at") >= F.date_sub(F.current_date(), 90))
    .groupBy(
        F.date_trunc("week", "created_at").alias("week"),
        "sentiment"
    )
    .agg(F.count("*").alias("ticket_count"))
    .withColumn(
        "percentage",
        F.round(F.col("ticket_count") * 100.0 / F.sum("ticket_count").over(Window.partitionBy("week")), 2)
    )
    .orderBy(F.desc("week"), F.desc("ticket_count"))
)

print("Sentiment Trends (Last 90 Days):")
display(sentiment_trends)

# COMMAND ----------

# NPS distribution (last 30 days)
nps_distribution = (
    tickets_df
    .filter(F.col("nps_score").isNotNull())
    .filter(F.col("created_at") >= F.date_sub(F.current_date(), 30))
    .withColumn(
        "nps_category",
        F.when(F.col("nps_score") >= 9, "Promoter (9-10)")
        .when(F.col("nps_score") >= 7, "Passive (7-8)")
        .otherwise("Detractor (0-6)")
    )
    .groupBy("nps_category")
    .agg(F.count("*").alias("response_count"))
    .withColumn(
        "percentage",
        F.round(F.col("response_count") * 100.0 / F.sum("response_count").over(Window.partitionBy()), 2)
    )
)

print("NPS Distribution (Last 30 Days):")
display(nps_distribution)

# COMMAND ----------

# Calculate NPS score
nps_data = tickets_df.filter(F.col("nps_score").isNotNull()).filter(F.col("created_at") >= F.date_sub(F.current_date(), 30))

total_responses = nps_data.count()
promoters = nps_data.filter(F.col("nps_score") >= 9).count()
detractors = nps_data.filter(F.col("nps_score") <= 6).count()

nps_final = ((promoters - detractors) / total_responses) * 100 if total_responses > 0 else 0

print(f"\n📊 Net Promoter Score (NPS): {nps_final:.1f}")
print(f"   Promoters: {promoters} ({promoters*100/total_responses:.1f}%)")
print(f"   Detractors: {detractors} ({detractors*100/total_responses:.1f}%)")

# COMMAND ----------

# CSAT by category
csat_by_category = (
    tickets_df
    .filter(F.col("csat_score").isNotNull())
    .filter(F.col("created_at") >= F.date_sub(F.current_date(), 30))
    .groupBy("category")
    .agg(
        F.count("*").alias("tickets_with_csat"),
        F.round(F.avg("csat_score"), 2).alias("avg_csat"),
        F.round(F.min("csat_score"), 2).alias("min_csat"),
        F.round(F.max("csat_score"), 2).alias("max_csat"),
        F.sum(F.when(F.col("csat_score") >= 4.0, 1).otherwise(0)).alias("satisfied_count")
    )
    .withColumn(
        "satisfaction_rate_pct",
        F.round(F.col("satisfied_count") * 100.0 / F.col("tickets_with_csat"), 2)
    )
    .orderBy(F.desc("avg_csat"))
)

print("CSAT by Category (Last 30 Days):")
display(csat_by_category)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📱 Analysis 7: Channel Performance

# COMMAND ----------

# Channel analysis
channel_performance = (
    tickets_df
    .filter(F.col("created_at") >= F.date_sub(F.current_date(), 30))
    .groupBy("channel")
    .agg(
        F.count("*").alias("total_tickets"),
        F.round(F.avg("first_response_time_minutes"), 2).alias("avg_first_response_min"),
        F.round(F.avg("resolution_time_hours"), 2).alias("avg_resolution_hours"),
        F.round(F.avg("csat_score"), 2).alias("avg_csat"),
        F.sum(F.when(F.col("status").isin("RESOLVED", "CLOSED"), 1).otherwise(0)).alias("resolved_count")
    )
    .withColumn(
        "percentage",
        F.round(F.col("total_tickets") * 100.0 / F.sum("total_tickets").over(Window.partitionBy()), 2)
    )
    .withColumn(
        "resolution_rate",
        F.round(F.col("resolved_count") * 100.0 / F.col("total_tickets"), 2)
    )
    .orderBy(F.desc("total_tickets"))
)

print("Channel Performance (Last 30 Days):")
display(channel_performance)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🔍 Analysis 8: Next Best Action Recommendations
# MAGIC
# MAGIC Find similar resolved tickets to recommend solutions

# COMMAND ----------

# Get open tickets with high priority
open_high_priority = (
    tickets_df
    .filter(F.col("status") == "OPEN")
    .filter(F.col("priority").isin("HIGH", "CRITICAL"))
    .orderBy(F.desc("created_at"))
    .limit(5)
)

print("Open High Priority Tickets Needing Action:")
display(open_high_priority.select("ticket_id", "priority", "category", "subcategory", "subject", "created_at"))

# COMMAND ----------

# For each open ticket, find similar resolved tickets
def find_similar_resolved_tickets(ticket_id, category, subcategory):
    """Find similar successfully resolved tickets"""
    similar = (
        tickets_df
        .filter(F.col("status").isin("RESOLVED", "CLOSED"))
        .filter(F.col("category") == category)
        .filter(F.col("subcategory") == subcategory)
        .filter(F.col("csat_score") >= 4.0)
        .join(agents_df.select("agent_id", "agent_name"), "agent_id", "left")
        .select(
            F.lit(ticket_id).alias("source_ticket_id"),
            F.col("ticket_id").alias("similar_ticket_id"),
            "subject",
            "resolution_time_hours",
            "csat_score",
            "agent_name"
        )
        .orderBy(F.desc("csat_score"), F.asc("resolution_time_hours"))
        .limit(3)
    )
    return similar

# Example: Find similar tickets for first open high priority ticket
first_open = open_high_priority.first()

if first_open:
    print(f"\n🎯 Recommendations for Ticket: {first_open.ticket_id}")
    print(f"   Category: {first_open.category} - {first_open.subcategory}")
    print(f"   Subject: {first_open.subject}")
    print(f"\n   Similar successfully resolved tickets:")
    
    similar_tickets = find_similar_resolved_tickets(
        first_open.ticket_id,
        first_open.category,
        first_open.subcategory
    )
    
    display(similar_tickets)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📝 Analysis 9: Generate Executive Summary

# COMMAND ----------

from datetime import datetime, timedelta

# Collect key metrics
summary_data = weekly_summary.first()

# Top issues
top_issues = category_summary.limit(5).collect()

# Critical alerts
critical_alerts = recent_tickets.filter(
    (F.col("priority") == "CRITICAL") & 
    (F.col("status").isin("OPEN", "IN_PROGRESS"))
).count()

# High churn risk
high_churn_risk = churn_risk.filter(F.col("churn_risk_score") > 0.7).count()

# Generate summary
current_date = datetime.now()
week_start = current_date - timedelta(days=7)

executive_summary = f"""
{'='*70}
EXECUTIVE SUMMARY - CUSTOMER SUPPORT TICKETS
Week of: {week_start.strftime('%Y-%m-%d')} to {current_date.strftime('%Y-%m-%d')}
{'='*70}

OVERVIEW
--------
Total Tickets: {summary_data.total_tickets}
Open Tickets: {summary_data.open_tickets}
In Progress: {summary_data.in_progress}
Closed Tickets: {summary_data.closed_tickets}
Critical Tickets: {summary_data.critical_tickets}

PERFORMANCE METRICS
------------------
Average Resolution Time: {summary_data.avg_resolution_hours} hours
Average First Response: {summary_data.avg_first_response_minutes} minutes
SLA Breaches: {summary_data.sla_breaches}
Average CSAT Score: {summary_data.avg_csat}/5.0
Average NPS: {summary_data.avg_nps}/10

TOP ISSUES THIS WEEK
--------------------
"""

for idx, issue in enumerate(top_issues, 1):
    executive_summary += f"{idx}. {issue.category} - {issue.subcategory}: {issue.ticket_count} tickets\n"

executive_summary += f"""
CRITICAL ALERTS
--------------
🔴 Active Critical Tickets: {critical_alerts}
⚠️  High Churn Risk Companies: {high_churn_risk}

RECOMMENDATIONS
---------------
"""

# Add dynamic recommendations
if summary_data.sla_breaches and summary_data.sla_breaches > 10:
    executive_summary += "⚠️  SLA breaches above threshold - Review agent capacity\n"

if summary_data.avg_csat and summary_data.avg_csat < 3.5:
    executive_summary += "⚠️  Low CSAT score - Quality review needed\n"

if critical_alerts > 5:
    executive_summary += "⚠️  High number of critical tickets - Consider escalation\n"

if high_churn_risk > 5:
    executive_summary += "⚠️  Multiple companies at churn risk - Proactive outreach required\n"

executive_summary += f"\n{'='*70}\n"

print(executive_summary)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 💾 Step 7: Save Analysis Results

# COMMAND ----------

# Save analysis results as tables for easy access

# Churn risk analysis
churn_with_actions.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.churn_risk_analysis")
print(f"✓ Saved: {SCHEMA_NAME}.churn_risk_analysis")

# Agent performance
agent_performance.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.agent_performance_weekly")
print(f"✓ Saved: {SCHEMA_NAME}.agent_performance_weekly")

# Weekly summary (convert to DataFrame first)
weekly_summary_df = weekly_summary.withColumn("analysis_date", F.current_timestamp())
weekly_summary_df.write.mode("overwrite").saveAsTable(f"{SCHEMA_NAME}.weekly_summary")
print(f"✓ Saved: {SCHEMA_NAME}.weekly_summary")

print("\n✅ All analysis results saved")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🎉 Setup Complete!
# MAGIC ---
# MAGIC
# MAGIC ## ✅ What was accomplished:
# MAGIC
# MAGIC 1. ✅ Created 5 Delta tables with proper schemas
# MAGIC 2. ✅ Loaded all CSV data (3,574 records)
# MAGIC 3. ✅ Optimized tables with Z-ordering
# MAGIC 4. ✅ Performed comprehensive analysis:
# MAGIC    - Weekly executive summary
# MAGIC    - Top issues and trends
# MAGIC    - Churn risk detection
# MAGIC    - SLA performance monitoring
# MAGIC    - Agent performance metrics
# MAGIC    - Sentiment analysis
# MAGIC    - Channel performance
# MAGIC    - Next best action recommendations
# MAGIC 5. ✅ Saved analysis results for reuse
# MAGIC
# MAGIC ## 🚀 Next Steps:
# MAGIC
# MAGIC 1. **Create Dashboards**: Use Databricks SQL to visualize these analyses
# MAGIC 2. **Set up Genie**: Create a Genie Space for natural language queries
# MAGIC 3. **Implement AI Functions**: Use ai_summarize(), ai_classify() for automation
# MAGIC 4. **Build Alerts**: Set up automated alerts for critical tickets
# MAGIC 5. **Deploy ML Models**: Create churn prediction models
# MAGIC
# MAGIC ## 📚 Resources:
# MAGIC
# MAGIC - **analysis_queries.sql**: 50+ ready-to-use SQL queries
# MAGIC - **genie_example_prompts.md**: Example questions for Genie
# MAGIC - **README.md**: Complete project documentation
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC **Ready for demonstration!** 🎯

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🔗 Quick Access Queries

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Quick access: View all tables
# MAGIC SHOW TABLES

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Quick access: Recent tickets summary
# MAGIC SELECT 
# MAGIC     status,
# MAGIC     priority,
# MAGIC     COUNT(*) as ticket_count
# MAGIC FROM tickets
# MAGIC WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS
# MAGIC GROUP BY status, priority
# MAGIC ORDER BY status, priority

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Quick access: Churn risk summary
# MAGIC SELECT * FROM churn_risk_analysis
# MAGIC ORDER BY churn_risk_score DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC *Notebook created for Databricks GenAI Demo - Customer Support Tickets Agent*
# MAGIC
# MAGIC *Version: 1.0 | Date: January 2026*
