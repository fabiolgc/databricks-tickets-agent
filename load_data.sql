-- ============================================================================
-- Data Load Script - Import CSV files into Delta tables
-- Execute this after creating tables with ddl_tables.sql
-- ============================================================================

-- Note: Update the file paths below to point to your actual CSV locations
-- Option 1: Upload CSVs to DBFS and reference them
-- Option 2: Use Databricks Auto Loader for continuous ingestion
-- Option 3: Use COPY INTO for batch loads

-- ============================================================================
-- OPTION 1: Direct COPY INTO from DBFS (after uploading CSVs)
-- ============================================================================

-- Step 1: Upload CSV files to DBFS
-- Use Databricks UI or CLI:
-- databricks fs cp companies.csv dbfs:/FileStore/tickets/companies.csv
-- databricks fs cp customers.csv dbfs:/FileStore/tickets/customers.csv
-- databricks fs cp agents.csv dbfs:/FileStore/tickets/agents.csv
-- databricks fs cp tickets.csv dbfs:/FileStore/tickets/tickets.csv
-- databricks fs cp ticket_interactions.csv dbfs:/FileStore/tickets/ticket_interactions.csv

-- Step 2: Load data using COPY INTO

-- Load companies
COPY INTO companies
FROM '/FileStore/tickets/companies.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS (
  'header' = 'true',
  'inferSchema' = 'false',
  'delimiter' = ',',
  'quote' = '"',
  'escape' = '"',
  'multiLine' = 'true'
)
COPY_OPTIONS ('mergeSchema' = 'false');

-- Load agents (load before customers due to FK dependencies)
COPY INTO agents
FROM '/FileStore/tickets/agents.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS (
  'header' = 'true',
  'inferSchema' = 'false',
  'delimiter' = ',',
  'quote' = '"',
  'escape' = '"',
  'multiLine' = 'true'
)
COPY_OPTIONS ('mergeSchema' = 'false');

-- Load customers
COPY INTO customers
FROM '/FileStore/tickets/customers.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS (
  'header' = 'true',
  'inferSchema' = 'false',
  'delimiter' = ',',
  'quote' = '"',
  'escape' = '"',
  'multiLine' = 'true'
)
COPY_OPTIONS ('mergeSchema' = 'false');

-- Load tickets
COPY INTO tickets
FROM '/FileStore/tickets/tickets.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS (
  'header' = 'true',
  'inferSchema' = 'false',
  'delimiter' = ',',
  'quote' = '"',
  'escape' = '"',
  'multiLine' = 'true'
)
COPY_OPTIONS ('mergeSchema' = 'false');

-- Load ticket interactions
COPY INTO ticket_interactions
FROM '/FileStore/tickets/ticket_interactions.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS (
  'header' = 'true',
  'inferSchema' = 'false',
  'delimiter' = ',',
  'quote' = '"',
  'escape' = '"',
  'multiLine' = 'true'
)
COPY_OPTIONS ('mergeSchema' = 'false');

-- ============================================================================
-- OPTION 2: Using Spark DataFrame API (in Databricks Notebook)
-- ============================================================================

/*
# Python code to run in Databricks notebook

from pyspark.sql.types import *

# Define schemas to ensure correct data types

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

# Load companies
df_companies = (spark.read
    .option("header", "true")
    .option("multiLine", "true")
    .option("escape", "\"")
    .schema(companies_schema)
    .csv("/FileStore/tickets/companies.csv")
)
df_companies.write.mode("append").saveAsTable("companies")

# Repeat for other tables...
# agents -> customers -> tickets -> ticket_interactions
*/

-- ============================================================================
-- Verify data load
-- ============================================================================

SELECT 'companies' AS table_name, COUNT(*) AS record_count FROM companies
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'agents', COUNT(*) FROM agents
UNION ALL
SELECT 'tickets', COUNT(*) FROM tickets
UNION ALL
SELECT 'ticket_interactions', COUNT(*) FROM ticket_interactions;

-- ============================================================================
-- Optimize tables for better query performance
-- ============================================================================

-- Optimize and Z-order tables
OPTIMIZE companies ZORDER BY (company_id, status);
OPTIMIZE customers ZORDER BY (company_id, customer_id);
OPTIMIZE agents ZORDER BY (agent_id, team);
OPTIMIZE tickets ZORDER BY (created_at, status, priority, company_id);
OPTIMIZE ticket_interactions ZORDER BY (ticket_id, interaction_timestamp);

-- Collect statistics for cost-based optimizer
ANALYZE TABLE companies COMPUTE STATISTICS FOR ALL COLUMNS;
ANALYZE TABLE customers COMPUTE STATISTICS FOR ALL COLUMNS;
ANALYZE TABLE agents COMPUTE STATISTICS FOR ALL COLUMNS;
ANALYZE TABLE tickets COMPUTE STATISTICS FOR ALL COLUMNS;
ANALYZE TABLE ticket_interactions COMPUTE STATISTICS FOR ALL COLUMNS;

-- ============================================================================
-- Sample queries to validate data
-- ============================================================================

-- Check recent tickets
SELECT 
    t.ticket_id,
    t.created_at,
    t.status,
    t.priority,
    t.subject,
    c.company_name,
    cu.customer_name,
    a.agent_name
FROM tickets t
JOIN companies c ON t.company_id = c.company_id
JOIN customers cu ON t.customer_id = cu.customer_id
LEFT JOIN agents a ON t.agent_id = a.agent_id
WHERE t.created_at >= CURRENT_DATE - INTERVAL 7 DAYS
ORDER BY t.created_at DESC
LIMIT 10;

-- Check ticket distribution by status
SELECT 
    status,
    COUNT(*) AS ticket_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage
FROM tickets
GROUP BY status
ORDER BY ticket_count DESC;

-- Check average resolution time by priority
SELECT 
    priority,
    COUNT(*) AS total_tickets,
    ROUND(AVG(resolution_time_hours), 2) AS avg_resolution_hours,
    ROUND(AVG(first_response_time_minutes), 2) AS avg_first_response_minutes,
    SUM(CASE WHEN sla_breached = 'TRUE' THEN 1 ELSE 0 END) AS sla_breaches
FROM tickets
WHERE status IN ('RESOLVED', 'CLOSED')
GROUP BY priority
ORDER BY 
    CASE priority
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        WHEN 'LOW' THEN 4
    END;
