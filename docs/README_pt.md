# Customer Support Tickets Agent - Databricks GenAI Demo

## Overview

This project demonstrates an AI-powered customer support ticket analysis system for a payment processing company (similar to payment acquirers like Cielo). The system uses Databricks and GenAI to provide intelligent summaries, trend analysis, and actionable insights from customer support tickets.

## Use Cases

- **Intelligent Ticket Summarization**: Generate executive summaries of hundreds of tickets
- **Trend Analysis**: Identify patterns, common issues, and emerging problems
- **Churn Risk Detection**: Flag customers at risk of leaving based on ticket history
- **SLA Monitoring**: Track SLA compliance and response times
- **Next Best Action**: AI-powered recommendations based on similar historical tickets
- **NPS/CSAT Analysis**: Customer satisfaction trends and sentiment analysis

## Project Structure

```
databricks-tickets-agent/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── ddl_tables.sql                # DDL to create Delta tables
├── load_data.sql                 # SQL scripts to load data
├── generate_data.py              # Python script to generate synthetic data
├── companies.csv                 # 100 customer companies
├── customers.csv                 # 300 individual users
├── agents.csv                    # 25 support agents
├── tickets.csv                   # 500 support tickets
└── ticket_interactions.csv       # 2,649 ticket interactions/dialogue
```

## Database Schema

### Tables

1. **companies** - Customer companies using payment processing services
   - company_id (PK), company_name, cnpj (PII), segment, company_size
   - contract_start_date, monthly_transaction_volume, status, churn_risk_score

2. **customers** - Individual users who open support tickets
   - customer_id (PK), company_id (FK), customer_name (PII), email (PII)
   - cpf (PII), birth_date (PII), phone (PII), role

3. **agents** - Support agents handling tickets
   - agent_id (PK), agent_name, email, team, specialization
   - avg_csat, tickets_resolved, status

4. **tickets** - Main tickets table with all ticket information
   - ticket_id (PK), company_id (FK), customer_id (FK), agent_id (FK)
   - status, priority, category, subcategory, channel, subject, description
   - resolution_time_hours, first_response_time_minutes, sla_breached
   - nps_score, csat_score, sentiment, tags

5. **ticket_interactions** - Interaction history/dialogue for each ticket
   - interaction_id (PK), ticket_id (FK), interaction_timestamp
   - author_type, author_id, author_name, message, interaction_type

### Relationships

```
companies (1) ----< (N) customers
companies (1) ----< (N) tickets
customers (1) ----< (N) tickets
agents (1) ----< (N) tickets
tickets (1) ----< (N) ticket_interactions
```

## Setup Instructions

### Step 1: Generate Synthetic Data (Optional)

The repository already includes pre-generated CSV files. If you want to regenerate the data:

```bash
# Install dependencies
pip install -r requirements.txt

# Generate new data
python generate_data.py
```

This will create/overwrite all CSV files with fresh synthetic data.

### Step 2: Create Tables in Databricks

1. Open Databricks SQL Editor or a Databricks notebook
2. Copy and paste the contents of `ddl_tables.sql`
3. Execute the script to create all Delta tables

```sql
-- This will create: companies, customers, agents, tickets, ticket_interactions
-- All tables are Delta format with proper constraints and PII tags
```

### Step 3: Upload CSV Files to DBFS

Use Databricks UI or CLI to upload CSV files:

**Option A: Using Databricks UI**
1. Go to Data → DBFS → FileStore
2. Create folder: `/FileStore/tickets/`
3. Upload all 5 CSV files to this location

**Option B: Using Databricks CLI**
```bash
databricks fs cp companies.csv dbfs:/FileStore/tickets/companies.csv
databricks fs cp customers.csv dbfs:/FileStore/tickets/customers.csv
databricks fs cp agents.csv dbfs:/FileStore/tickets/agents.csv
databricks fs cp tickets.csv dbfs:/FileStore/tickets/tickets.csv
databricks fs cp ticket_interactions.csv dbfs:/FileStore/tickets/ticket_interactions.csv
```

### Step 4: Load Data into Tables

Execute the `load_data.sql` script in Databricks SQL Editor:

```sql
-- Load data using COPY INTO
-- The script includes commands to load all tables in correct order
-- (respecting foreign key dependencies)
```

### Step 5: Optimize Tables

After loading data, optimize tables for query performance:

```sql
OPTIMIZE tickets ZORDER BY (created_at, status, priority, company_id);
OPTIMIZE ticket_interactions ZORDER BY (ticket_id, interaction_timestamp);
```

## Data Details

### Ticket Categories

- **TECHNICAL**: POS issues, connection errors, PIX problems, card reading
- **FINANCIAL**: Chargebacks, missing payments, incorrect fees, receipts
- **COMMERCIAL**: Plan changes, cancellations, contract inquiries
- **COMPLAINT**: Poor service, system downtime, long wait times
- **INFORMATION**: How-to questions, feature inquiries

### Ticket Status Flow

```
OPEN → IN_PROGRESS → PENDING_CUSTOMER → RESOLVED → CLOSED
                   ↘ CANCELLED
```

### Priority Levels

- **CRITICAL**: 4-hour SLA
- **HIGH**: 8-hour SLA
- **MEDIUM**: 24-hour SLA
- **LOW**: 48-hour SLA

### Channels

- EMAIL
- PHONE
- CHAT
- WHATSAPP
- PORTAL

## Sample Queries for GenAI Agent

### 1. Weekly Executive Summary

```sql
-- What's happening this week?
SELECT 
    COUNT(*) AS total_tickets,
    COUNT(CASE WHEN status = 'OPEN' THEN 1 END) AS open_tickets,
    COUNT(CASE WHEN priority = 'CRITICAL' THEN 1 END) AS critical_tickets,
    ROUND(AVG(CASE WHEN status = 'CLOSED' THEN resolution_time_hours END), 2) AS avg_resolution_hours,
    SUM(CASE WHEN sla_breached = 'TRUE' THEN 1 ELSE 0 END) AS sla_breaches,
    ROUND(AVG(csat_score), 2) AS avg_csat
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS;
```

### 2. Top Issues and Trends

```sql
-- What are the main problems this week?
SELECT 
    category,
    subcategory,
    COUNT(*) AS ticket_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage,
    AVG(CASE WHEN status = 'CLOSED' THEN resolution_time_hours END) AS avg_resolution
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY category, subcategory
ORDER BY ticket_count DESC
LIMIT 10;
```

### 3. Churn Risk Analysis

```sql
-- Companies at risk of churning
SELECT 
    c.company_name,
    c.churn_risk_score,
    COUNT(t.ticket_id) AS recent_tickets,
    SUM(CASE WHEN t.priority IN ('HIGH', 'CRITICAL') THEN 1 ELSE 0 END) AS urgent_tickets,
    AVG(t.csat_score) AS avg_satisfaction,
    STRING_AGG(DISTINCT t.category, ', ') AS issue_types
FROM companies c
LEFT JOIN tickets t ON c.company_id = t.company_id 
    AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
WHERE c.churn_risk_score > 0.6
GROUP BY c.company_name, c.churn_risk_score
ORDER BY c.churn_risk_score DESC, recent_tickets DESC;
```

### 4. Agent Performance

```sql
-- Support team performance
SELECT 
    a.agent_name,
    a.team,
    COUNT(t.ticket_id) AS tickets_handled,
    ROUND(AVG(t.resolution_time_hours), 2) AS avg_resolution_hours,
    ROUND(AVG(t.csat_score), 2) AS avg_csat,
    SUM(CASE WHEN t.sla_breached = 'TRUE' THEN 1 ELSE 0 END) AS sla_breaches
FROM agents a
LEFT JOIN tickets t ON a.agent_id = t.agent_id
    AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
WHERE a.status = 'ACTIVE'
GROUP BY a.agent_name, a.team
ORDER BY tickets_handled DESC;
```

### 5. Sentiment Analysis

```sql
-- Customer sentiment trends
SELECT 
    DATE_TRUNC('week', created_at) AS week,
    sentiment,
    COUNT(*) AS ticket_count
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 90 DAYS
GROUP BY DATE_TRUNC('week', created_at), sentiment
ORDER BY week DESC, ticket_count DESC;
```

## GenAI Agent Implementation Suggestions

### Using Databricks AI Functions

```python
# Example: Use Databricks AI Functions for summarization
from databricks import sql
from databricks.sdk import WorkspaceClient

# Connect to Databricks
w = WorkspaceClient()

# Query tickets
query = """
    SELECT ticket_id, subject, description, 
           ARRAY_JOIN(COLLECT_LIST(message), '\n') as conversation
    FROM tickets t
    JOIN ticket_interactions ti ON t.ticket_id = ti.ticket_id
    WHERE t.created_at >= CURRENT_DATE - INTERVAL 7 DAYS
    GROUP BY ticket_id, subject, description
"""

# Use AI function to summarize
summarize_query = """
    SELECT 
        ticket_id,
        ai_summarize(conversation) as summary,
        ai_analyze_sentiment(conversation) as sentiment
    FROM ({}) 
""".format(query)

# Generate executive report
executive_summary = """
    SELECT 
        ai_gen('Based on these ticket summaries, generate an executive 
               report highlighting main issues, trends, and recommendations: ' 
               || STRING_AGG(summary, '\n'))
    FROM ({})
""".format(summarize_query)
```

### Recommended AI Features

1. **AI Functions** - Use `ai_summarize()`, `ai_extract()`, `ai_classify()`
2. **Vector Search** - Find similar tickets for next best action
3. **Genie** - Natural language queries for managers
4. **Unity Catalog** - Tag PII fields for governance
5. **Lakehouse Monitoring** - Track data quality and drift

## PII Compliance

All PII fields are tagged in the DDL:

- **companies**: cnpj
- **customers**: customer_name, email, cpf, birth_date, phone

Use Databricks Unity Catalog to:
- Apply masking policies
- Track data lineage
- Audit data access
- Comply with LGPD/GDPR

## Next Steps

1. **Create dashboards** using Databricks SQL
2. **Build ML models** for churn prediction
3. **Implement real-time alerts** for critical tickets
4. **Deploy GenAI agent** using Databricks Model Serving
5. **Set up workflows** for automated reporting

## Support

For questions about this demo, contact your Databricks Solutions Architect.

---

**Note**: This is a demonstration project with synthetic data. All names, companies, and identifiers are fictitious.
