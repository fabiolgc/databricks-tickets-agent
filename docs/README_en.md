# Customer Support Tickets Agent - Databricks GenAI Demo

## Overview

AI-powered customer support ticket analysis system for payment processing companies. Demonstrates Databricks capabilities with GenAI for intelligent ticket summarization, trend analysis, churn risk detection, and actionable insights.

## Use Cases

- **Intelligent Ticket Summarization**: Generate executive summaries from hundreds of tickets
- **Trend Analysis**: Identify patterns, common issues, and emerging problems
- **Churn Risk Detection**: Flag customers at risk of leaving based on ticket history
- **SLA Monitoring**: Track SLA compliance and response times
- **Next Best Action**: AI-powered recommendations based on similar historical tickets
- **NPS/CSAT Analysis**: Customer satisfaction trends and sentiment analysis

## Project Structure

```
databricks-tickets-agent/
├── data/                   # CSV data files (English & Portuguese)
│   ├── *_en.csv           # English version data
│   └── *.csv              # Portuguese version data
│
├── sql/                    # SQL scripts
│   ├── ddl_tables_en.sql  # English DDL
│   ├── load_data_en.sql   # English data load
│   └── ...
│
├── notebooks/              # Databricks notebooks
│   └── setup_and_analysis_notebook.py
│
├── scripts/                # Utility scripts
│   ├── generate_data_en.py
│   └── requirements.txt
│
└── docs/                   # Documentation
    ├── README_en.md        # This file
    ├── QUICKSTART_en.md    # Quick start guide
    └── *_pt.md             # Portuguese documentation
```

## Database Schema

### Tables (5 related tables)

1. **companies** - Customer companies using payment services
   - 100 companies with segments, size, transaction volume, churn risk

2. **customers** - Individual users opening tickets
   - 300 customers with PII fields (name, email, SSN, birth date, phone)

3. **agents** - Support agents handling tickets
   - 25 agents across 4 teams with performance metrics

4. **tickets** - Main tickets table
   - 500 tickets with status, priority, category, SLA metrics, NPS, CSAT
   - Categories: TECHNICAL, FINANCIAL, COMMERCIAL, COMPLAINT, INFORMATION

5. **ticket_interactions** - Conversation history
   - 2,636+ interactions with full dialogue

### Relationships

```
companies (1) ─┬─< customers (N)
               └─< tickets (N)
customers (1) ───< tickets (N)
agents (1) ──────< tickets (N)
tickets (1) ─────< ticket_interactions (N)
```

## Quick Start

### 1. Generate or Use Existing Data

**Option A: Use pre-generated English data**
```bash
# English CSVs are already in data/ folder
ls data/*_en.csv
```

**Option B: Generate new data**
```bash
cd scripts/
python3 generate_data_en.py
```

### 2. Upload to Databricks

```bash
# Upload CSV files to DBFS
databricks fs cp data/*_en.csv dbfs:/FileStore/tickets/en/
```

### 3. Create Tables

```sql
-- In Databricks SQL Editor, execute:
-- sql/ddl_tables_en.sql
```

### 4. Load Data

```sql
-- Execute in Databricks SQL Editor:
-- sql/load_data_en.sql
```

### 5. Start Analyzing

Import and run notebook:
- `notebooks/setup_and_analysis_notebook.py`

Or use Databricks Genie with natural language queries:
- "Show me companies at risk of churning"
- "What are the top issues this week?"
- "Which agent has the best customer satisfaction?"

## Data Statistics

### English Version Data
- **Companies**: 100
- **Customers**: 300  
- **Agents**: 25
- **Tickets**: 500
- **Interactions**: 2,636+
- **Total Records**: 3,561+

### Ticket Distribution
- Status: 35% Closed, 32% Resolved, 14% In Progress, 11% Pending, 8% Open
- Priority: 37% Low, 37% Medium, 21% High, 5% Critical
- Category: 34% Technical, 27% Financial, 19% Complaint, 11% Commercial, 9% Information

### Performance Metrics
- Average Resolution Time: ~89 hours
- Average CSAT Score: 3.1/5.0
- Average NPS: 5.1/10
- SLA Breaches: ~58%

## Sample Queries

### Executive Summary
```sql
SELECT 
    COUNT(*) AS total_tickets,
    COUNT(CASE WHEN status = 'OPEN' THEN 1 END) AS open_tickets,
    COUNT(CASE WHEN priority = 'CRITICAL' THEN 1 END) AS critical_tickets,
    ROUND(AVG(csat_score), 2) AS avg_csat
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS;
```

### Churn Risk Companies
```sql
SELECT 
    c.company_name,
    c.churn_risk_score,
    COUNT(t.ticket_id) AS recent_tickets,
    AVG(t.csat_score) AS satisfaction
FROM companies c
LEFT JOIN tickets t ON c.company_id = t.company_id
WHERE c.churn_risk_score > 0.6
    AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY c.company_name, c.churn_risk_score
ORDER BY c.churn_risk_score DESC;
```

### Top Issues
```sql
SELECT 
    category,
    subcategory,
    COUNT(*) AS count
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY category, subcategory
ORDER BY count DESC
LIMIT 10;
```

## Key Features

### Data Quality
- ✅ 100% referential integrity
- ✅ Temporal consistency across tables
- ✅ PII fields properly tagged
- ✅ Realistic business context

### Payment Processing Context
Tickets simulate real issues from a payment acquirer:
- POS terminals not working
- Mobile payment errors
- Chargebacks and refunds
- Incorrect fees
- Missing deposits
- Service complaints

### AI-Ready Structure
- ✅ Full conversation history
- ✅ Rich metadata (sentiment, tags, NPS, CSAT)
- ✅ ML-ready fields (churn_risk_score)
- ✅ Optimized for GenAI summarization

## Technologies

- **Delta Lake** - ACID transactions on data lake
- **Databricks SQL** - Analytics and queries
- **Unity Catalog** - Governance and PII management
- **PySpark** - Data processing
- **Databricks Genie** - Natural language queries
- **AI Functions** - Summarization and classification

## PII Compliance

PII fields are tagged in DDL:
- **companies**: tax_id
- **customers**: customer_name, email, ssn, birth_date, phone

Use Unity Catalog to:
- Apply data masking
- Track lineage
- Audit access
- Comply with GDPR/CCPA

## Next Steps

1. **Create Dashboards** - Use Databricks SQL for visualizations
2. **Build ML Models** - Churn prediction, ticket classification
3. **Implement Real-time Alerts** - Critical ticket notifications
4. **Deploy GenAI Agent** - Model Serving + Lakehouse Apps
5. **Set up Workflows** - Automated daily/weekly reports
6. **Enable Vector Search** - Semantic similarity for ticket matching

## Documentation

- **README_en.md** (this file) - Complete technical documentation
- **QUICKSTART_en.md** - 5-minute setup guide
- **README_pt.md** - Portuguese documentation
- **QUICKSTART_pt.md** - Portuguese quick start

## Support

This is a demonstration project with synthetic data. All names, companies, and identifiers are fictitious.

---

**Version**: 1.0  
**Date**: January 2026  
**Status**: ✅ Production-ready  
**Languages**: English & Portuguese (Brazilian)
