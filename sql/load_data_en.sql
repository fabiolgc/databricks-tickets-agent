-- ============================================================================
-- Data Load Script - Import CSV files into Delta tables (English Version)
-- Execute this after creating tables with ddl_tables_en.sql
-- ============================================================================

-- Update the file paths below to point to your actual CSV locations

-- ============================================================================
-- Upload CSV files to DBFS using Databricks UI or CLI:
-- databricks fs cp data/companies_en.csv dbfs:/FileStore/tickets/en/
-- databricks fs cp data/customers_en.csv dbfs:/FileStore/tickets/en/
-- databricks fs cp data/agents_en.csv dbfs:/FileStore/tickets/en/
-- databricks fs cp data/tickets_en.csv dbfs:/FileStore/tickets/en/
-- databricks fs cp data/ticket_interactions_en.csv dbfs:/FileStore/tickets/en/
-- ============================================================================

-- Load companies
COPY INTO companies
FROM '/FileStore/tickets/en/companies_en.csv'
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

-- Load agents
COPY INTO agents
FROM '/FileStore/tickets/en/agents_en.csv'
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
FROM '/FileStore/tickets/en/customers_en.csv'
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
FROM '/FileStore/tickets/en/tickets_en.csv'
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
FROM '/FileStore/tickets/en/ticket_interactions_en.csv'
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

OPTIMIZE companies ZORDER BY (company_id, status);
OPTIMIZE customers ZORDER BY (company_id, customer_id);
OPTIMIZE agents ZORDER BY (agent_id, team);
OPTIMIZE tickets ZORDER BY (created_at, status, priority, company_id);
OPTIMIZE ticket_interactions ZORDER BY (ticket_id, interaction_timestamp);

-- Collect statistics
ANALYZE TABLE companies COMPUTE STATISTICS FOR ALL COLUMNS;
ANALYZE TABLE customers COMPUTE STATISTICS FOR ALL COLUMNS;
ANALYZE TABLE agents COMPUTE STATISTICS FOR ALL COLUMNS;
ANALYZE TABLE tickets COMPUTE STATISTICS FOR ALL COLUMNS;
ANALYZE TABLE ticket_interactions COMPUTE STATISTICS FOR ALL COLUMNS;
