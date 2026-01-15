# Databricks notebook source
# MAGIC %md
# MAGIC # Customer Support Tickets - GenAI Agent Demo
# MAGIC
# MAGIC This notebook demonstrates how to build an AI-powered agent for ticket analysis using Databricks AI Functions.
# MAGIC
# MAGIC ## Features:
# MAGIC - Intelligent ticket summarization
# MAGIC - Trend analysis and pattern detection
# MAGIC - Churn risk identification
# MAGIC - Next best action recommendations
# MAGIC - Executive summaries

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Setup and Configuration

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.window import Window
from datetime import datetime, timedelta

# Configuration
CATALOG_NAME = "fabio_goncalves"
SCHEMA_NAME = "tickets_agent"  # Change to your schema name
CURRENT_DATE = datetime.now()
DAYS_BACK = 7

print(f"Analysis Period: Last {DAYS_BACK} days")
print(f"Current Date: {CURRENT_DATE.strftime('%Y-%m-%d')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Load Data

# COMMAND ----------

# Load tables
tickets_df = spark.table(f"{CATALOG_NAME}.{SCHEMA_NAME}.tickets")
companies_df = spark.table(f"{CATALOG_NAME}.{SCHEMA_NAME}.companies")
customers_df = spark.table(f"{CATALOG_NAME}.{SCHEMA_NAME}.customers")
agents_df = spark.table(f"{CATALOG_NAME}.{SCHEMA_NAME}.agents")
interactions_df = spark.table(f"{CATALOG_NAME}.{SCHEMA_NAME}.ticket_interactions")

# Filter for recent tickets
recent_tickets = tickets_df.filter(
    F.col("created_at") >= F.date_sub(F.current_date(), DAYS_BACK)
)

print(f"Total tickets in period: {recent_tickets.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Weekly Summary - "What's happening this week?"

# COMMAND ----------

# Basic metrics
weekly_summary = recent_tickets.agg(
    F.count("*").alias("total_tickets"),
    F.sum(F.when(F.col("status") == "OPEN", 1).otherwise(0)).alias("open_tickets"),
    F.sum(F.when(F.col("status") == "CLOSED", 1).otherwise(0)).alias("closed_tickets"),
    F.sum(F.when(F.col("priority") == "CRITICAL", 1).otherwise(0)).alias("critical_tickets"),
    F.round(F.avg(F.when(F.col("status").isin("RESOLVED", "CLOSED"), F.col("resolution_time_hours"))), 2).alias("avg_resolution_hours"),
    F.sum(F.when(F.col("sla_breached") == "TRUE", 1).otherwise(0)).alias("sla_breaches"),
    F.round(F.avg("csat_score"), 2).alias("avg_csat"),
    F.round(F.avg("nps_score"), 1).alias("avg_nps")
)

display(weekly_summary)

# COMMAND ----------

# Category breakdown
category_summary = recent_tickets.groupBy("category", "subcategory").agg(
    F.count("*").alias("ticket_count"),
    F.round(F.avg(F.when(F.col("status").isin("RESOLVED", "CLOSED"), F.col("resolution_time_hours"))), 2).alias("avg_resolution_hours"),
    F.sum(F.when(F.col("priority").isin("HIGH", "CRITICAL"), 1).otherwise(0)).alias("urgent_count"),
    F.round(F.avg("csat_score"), 2).alias("avg_csat")
).orderBy(F.desc("ticket_count"))

display(category_summary.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. AI-Powered Ticket Summarization
# MAGIC
# MAGIC Using Databricks AI Functions to generate intelligent summaries

# COMMAND ----------

# Get ticket conversations
ticket_conversations = (
    recent_tickets
    .join(interactions_df, "ticket_id")
    .groupBy(
        "ticket_id", "subject", "category", "priority", "status", 
        "company_id", "customer_id"
    )
    .agg(
        F.concat_ws("\n", F.collect_list("message")).alias("full_conversation"),
        F.count("*").alias("interaction_count")
    )
)

# Sample a few tickets to summarize
sample_tickets = ticket_conversations.limit(10)

display(sample_tickets.select("ticket_id", "subject", "category", "interaction_count"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### AI Function Examples (Databricks SQL AI Functions)
# MAGIC
# MAGIC Note: These require Databricks SQL AI Functions to be enabled in your workspace

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Example: Summarize ticket conversations using AI
# MAGIC -- This is a SQL example showing how to use ai_summarize()
# MAGIC
# MAGIC SELECT 
# MAGIC     ticket_id,
# MAGIC     subject,
# MAGIC     category,
# MAGIC     ai_summarize(full_conversation) as ai_summary
# MAGIC FROM (
# MAGIC     SELECT 
# MAGIC         t.ticket_id,
# MAGIC         t.subject,
# MAGIC         t.category,
# MAGIC         CONCAT_WS('\n', COLLECT_LIST(ti.message)) as full_conversation
# MAGIC     FROM fabio_goncalves.tickets_agent.tickets t
# MAGIC     JOIN fabio_goncalves.tickets_agent.ticket_interactions ti ON t.ticket_id = ti.ticket_id
# MAGIC     WHERE t.created_at >= CURRENT_DATE - INTERVAL 7 DAYS
# MAGIC     GROUP BY t.ticket_id, t.subject, t.category
# MAGIC )
# MAGIC LIMIT 10;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Churn Risk Analysis

# COMMAND ----------

# Identify companies at risk
churn_risk = (
    companies_df
    .filter(F.col("churn_risk_score") > 0.5)
    .join(
        recent_tickets.groupBy("company_id").agg(
            F.count("*").alias("recent_tickets"),
            F.sum(F.when(F.col("priority").isin("HIGH", "CRITICAL"), 1).otherwise(0)).alias("urgent_tickets"),
            F.sum(F.when(F.col("category") == "COMPLAINT", 1).otherwise(0)).alias("complaints"),
            F.round(F.avg("csat_score"), 2).alias("avg_csat"),
            F.collect_set("category").alias("issue_categories")
        ),
        "company_id",
        "left"
    )
    .select(
        "company_name",
        "segment",
        "churn_risk_score",
        "recent_tickets",
        "urgent_tickets",
        "complaints",
        "avg_csat",
        "issue_categories"
    )
    .orderBy(F.desc("churn_risk_score"))
)

display(churn_risk.limit(20))

# COMMAND ----------

# Churn risk with recommended actions
churn_with_actions = churn_risk.withColumn(
    "recommended_action",
    F.when((F.col("churn_risk_score") > 0.8) & (F.col("complaints") >= 2), 
           "IMMEDIATE: Schedule executive call")
    .when((F.col("churn_risk_score") > 0.7) & (F.col("urgent_tickets") >= 3), 
          "URGENT: Escalate to account manager")
    .when((F.col("churn_risk_score") > 0.6) & (F.col("avg_csat") < 3.0), 
          "HIGH: Proactive outreach needed")
    .otherwise("Monitor closely")
)

display(churn_with_actions)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. SLA Performance Monitoring

# COMMAND ----------

sla_performance = (
    recent_tickets
    .filter(F.col("status").isin("RESOLVED", "CLOSED"))
    .groupBy("priority")
    .agg(
        F.count("*").alias("total_tickets"),
        F.sum(F.when(F.col("sla_breached") == "TRUE", 1).otherwise(0)).alias("sla_breached"),
        F.sum(F.when(F.col("sla_breached") == "FALSE", 1).otherwise(0)).alias("sla_met"),
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

display(sla_performance)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Agent Performance Analysis

# COMMAND ----------

# DBTITLE 1,Cell 19
agent_performance = (
    agents_df
    .filter(F.col("status") == "ACTIVE")
    .join(
        recent_tickets.groupBy("agent_id").agg(
            F.count("*").alias("tickets_handled"),
            F.sum(F.when(F.col("status").isin("RESOLVED", "CLOSED"), 1).otherwise(0)).alias("tickets_resolved_7d"),
            F.round(F.avg("resolution_time_hours"), 2).alias("avg_resolution_hours"),
            F.round(F.avg("first_response_time_minutes"), 2).alias("avg_first_response_min"),
            F.round(F.avg("csat_score"), 2).alias("avg_csat_7d"),
            F.sum(F.when(F.col("sla_breached") == "TRUE", 1).otherwise(0)).alias("sla_breaches")
        ),
        "agent_id",
        "left"
    )
    .select(
        "agent_name",
        "team",
        "specialization",
        "tickets_handled",
        "tickets_resolved_7d",
        "avg_resolution_hours",
        "avg_first_response_min",
        "avg_csat_7d",
        "sla_breaches"
    )
    .withColumn(
        "resolution_rate_pct",
        F.round(F.col("tickets_resolved_7d") * 100.0 / F.col("tickets_handled"), 2)
    )
    .orderBy(F.desc("tickets_handled"))
)

display(agent_performance)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Sentiment Trend Analysis

# COMMAND ----------

sentiment_trends = (
    tickets_df
    .filter(F.col("created_at") >= F.date_sub(F.current_date(), 90))
    .groupBy(
        F.date_trunc("week", "created_at").alias("week"),
        "sentiment"
    )
    .agg(F.count("*").alias("ticket_count"))
    .orderBy(F.desc("week"), F.desc("ticket_count"))
)

display(sentiment_trends)

# COMMAND ----------

# NPS Distribution
nps_distribution = (
    recent_tickets
    .filter(F.col("nps_score").isNotNull())
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

display(nps_distribution)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Next Best Action Recommendations
# MAGIC
# MAGIC Find similar resolved tickets to recommend solutions

# COMMAND ----------

def find_similar_tickets(target_ticket_id):
    """
    Find similar resolved tickets for a given ticket
    Returns tickets with same category/subcategory that were resolved successfully
    """
    # Get target ticket details
    target = tickets_df.filter(F.col("ticket_id") == target_ticket_id).first()
    
    if not target:
        return None
    
    # Find similar tickets
    similar = (
        tickets_df
        .filter(
            (F.col("status").isin("RESOLVED", "CLOSED")) &
            (F.col("category") == target.category) &
            (F.col("subcategory") == target.subcategory) &
            (F.col("csat_score") >= 4.0)
        )
        .join(agents_df.select("agent_id", "agent_name"), "agent_id", "left")
        .select(
            "ticket_id",
            "subject",
            "status",
            "resolution_time_hours",
            "csat_score",
            "agent_name"
        )
        .orderBy(F.desc("csat_score"), F.asc("resolution_time_hours"))
        .limit(5)
    )
    
    return similar

# Example: Find similar tickets for the first open ticket
first_open_ticket = recent_tickets.filter(F.col("status") == "OPEN").first()

if first_open_ticket:
    print(f"Finding similar tickets for: {first_open_ticket.ticket_id}")
    print(f"Category: {first_open_ticket.category} - {first_open_ticket.subcategory}")
    print(f"Subject: {first_open_ticket.subject}")
    print("\nSimilar resolved tickets:")
    
    similar = find_similar_tickets(first_open_ticket.ticket_id)
    if similar:
        display(similar)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Generate Executive Summary
# MAGIC
# MAGIC Comprehensive weekly report for management

# COMMAND ----------

# Collect key metrics
summary_metrics = weekly_summary.first()

# Top issues
top_issues = (
    category_summary
    .limit(5)
    .select("category", "subcategory", "ticket_count")
    .collect()
)

# Critical alerts
critical_alerts = recent_tickets.filter(
    (F.col("priority") == "CRITICAL") & 
    (F.col("status").isin("OPEN", "IN_PROGRESS"))
).count()

# Churn risk count
high_churn_risk = churn_risk.filter(F.col("churn_risk_score") > 0.7).count()

# Generate summary text
executive_summary = f"""
=================================================================
EXECUTIVE SUMMARY - CUSTOMER SUPPORT TICKETS
Week of: {(CURRENT_DATE - timedelta(days=DAYS_BACK)).strftime('%Y-%m-%d')} to {CURRENT_DATE.strftime('%Y-%m-%d')}
=================================================================

OVERVIEW
--------
Total Tickets: {summary_metrics.total_tickets}
Open Tickets: {summary_metrics.open_tickets}
Closed Tickets: {summary_metrics.closed_tickets}
Critical Tickets: {summary_metrics.critical_tickets}

PERFORMANCE METRICS
------------------
Average Resolution Time: {summary_metrics.avg_resolution_hours} hours
SLA Breaches: {summary_metrics.sla_breaches}
Average CSAT Score: {summary_metrics.avg_csat}/5.0
Average NPS: {summary_metrics.avg_nps}/10

TOP ISSUES THIS WEEK
--------------------
"""

for idx, issue in enumerate(top_issues, 1):
    executive_summary += f"{idx}. {issue.category} - {issue.subcategory}: {issue.ticket_count} tickets\n"

executive_summary += f"""
CRITICAL ALERTS
--------------
Active Critical Tickets: {critical_alerts}
High Churn Risk Companies: {high_churn_risk}

RECOMMENDATIONS
---------------
"""

# Add dynamic recommendations
if summary_metrics.sla_breaches > 10:
    executive_summary += "⚠️ SLA breaches above threshold - Review agent capacity\n"

if summary_metrics.avg_csat and summary_metrics.avg_csat < 3.5:
    executive_summary += "⚠️ Low CSAT score - Quality review needed\n"

if critical_alerts > 5:
    executive_summary += "⚠️ High number of critical tickets - Consider escalation\n"

if high_churn_risk > 5:
    executive_summary += "⚠️ Multiple companies at churn risk - Proactive outreach required\n"

executive_summary += "\n=================================================================\n"

print(executive_summary)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11. Save Results for AI Agent
# MAGIC
# MAGIC Export processed data for use by GenAI applications

# COMMAND ----------

# Save churn risk analysis
churn_with_actions.write.mode("overwrite").saveAsTable(f"{CATALOG_NAME}.{SCHEMA_NAME}.churn_risk_analysis")

# Save agent performance
agent_performance.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG_NAME}.{SCHEMA_NAME}.agent_performance_weekly")

# Save ticket summaries with conversations
ticket_conversations.write.mode("overwrite").saveAsTable(f"{CATALOG_NAME}.{SCHEMA_NAME}.ticket_conversations")

print("✓ Analysis results saved successfully")
print(f"  - {CATALOG_NAME}.{SCHEMA_NAME}.churn_risk_analysis")
print(f"  - {CATALOG_NAME}.{SCHEMA_NAME}.agent_performance_weekly")
print(f"  - {CATALOG_NAME}.{SCHEMA_NAME}.ticket_conversations")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC 1. **Create a Vector Index** for semantic search of similar tickets
# MAGIC 2. **Deploy as a Model** using Databricks Model Serving
# MAGIC 3. **Build a Lakehouse App** for interactive chat interface
# MAGIC 4. **Set up Workflows** for automated daily/weekly reports
# MAGIC 5. **Enable Lakehouse Monitoring** for data quality
# MAGIC 6. **Implement Unity Catalog governance** for PII protection
