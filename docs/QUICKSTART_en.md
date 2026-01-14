# Quick Start Guide - Databricks Tickets Agent (English Version)

## 🚀 5-Minute Setup

### Files Generated

```
✓ 5 CSV files with synthetic data (English):
  - companies_en.csv (100 companies)
  - customers_en.csv (300 customers)
  - agents_en.csv (25 agents)
  - tickets_en.csv (500 tickets)
  - ticket_interactions_en.csv (2,636+ interactions)

✓ SQL Scripts:
  - ddl_tables_en.sql (table creation)
  - load_data_en.sql (data import)

✓ Documentation:
  - README_en.md (technical docs)
  - QUICKSTART_en.md (this file)
```

## 📋 Step-by-Step

### 1. Create Tables (1 min)

In Databricks SQL Editor:

```sql
-- Copy and execute the content of sql/ddl_tables_en.sql
-- This will create 5 tables: companies, customers, agents, tickets, ticket_interactions
```

### 2. Upload CSVs (2 min)

**Option A - Databricks UI:**
1. Go to: Data → Add Data → Upload File
2. Upload all 5 CSV files from `data/*_en.csv`
3. Note the path where they were saved (e.g., `/FileStore/tables/`)

**Option B - Databricks CLI:**
```bash
databricks fs cp data/*_en.csv dbfs:/FileStore/tickets/en/
```

### 3. Load Data (2 min)

In Databricks SQL Editor, adjust paths and execute:

```sql
-- Load companies
COPY INTO companies
FROM '/FileStore/tickets/en/companies_en.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');

-- Load agents
COPY INTO agents
FROM '/FileStore/tickets/en/agents_en.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');

-- Load customers
COPY INTO customers
FROM '/FileStore/tickets/en/customers_en.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');

-- Load tickets
COPY INTO tickets
FROM '/FileStore/tickets/en/tickets_en.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');

-- Load interactions
COPY INTO ticket_interactions
FROM '/FileStore/tickets/en/ticket_interactions_en.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');
```

### 4. Verify Data

```sql
-- Count records in each table
SELECT 'companies' AS table_name, COUNT(*) AS records FROM companies
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'agents', COUNT(*) FROM agents
UNION ALL
SELECT 'tickets', COUNT(*) FROM tickets
UNION ALL
SELECT 'ticket_interactions', COUNT(*) FROM ticket_interactions;
```

Expected result:
- companies: 100
- customers: 300
- agents: 25
- tickets: 500
- ticket_interactions: 2,636+

## 🎯 First Queries - Test Now!

### "What's happening this week?"

```sql
SELECT 
    COUNT(*) AS total_tickets,
    COUNT(CASE WHEN status = 'OPEN' THEN 1 END) AS open,
    COUNT(CASE WHEN priority = 'CRITICAL' THEN 1 END) AS critical,
    ROUND(AVG(csat_score), 2) AS avg_satisfaction
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS;
```

### "What are the main problems?"

```sql
SELECT 
    category,
    subcategory,
    COUNT(*) AS total,
    ROUND(AVG(resolution_time_hours), 2) AS avg_hours
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY category, subcategory
ORDER BY total DESC
LIMIT 10;
```

### "Companies at risk of churning?"

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

## 🚨 Troubleshooting

### Error: "Table not found"
- Verify you executed `ddl_tables_en.sql` completely
- Confirm correct schema/database name

### Error: "File not found"
- Check CSV path in DBFS
- Use `%fs ls /FileStore/tickets/en/` to list files

### Error: "Foreign key violation"
- Load tables in correct order:
  1. companies, agents
  2. customers
  3. tickets
  4. ticket_interactions

### Data not appearing
- Execute: `REFRESH TABLE table_name`
- Verify COPY INTO was successful

## 🤖 Using Databricks Genie

Create a Genie Space:
1. Go to **Genie** in Databricks
2. Click **Create Space**
3. Select your tables
4. Start asking questions:
   - "Show me companies at risk of churning"
   - "What are the top issues this week?"
   - "Which agent has the best CSAT?"

## 📚 Next Steps

1. ✅ **Data loaded** → Explore analysis queries
2. 🤖 **Test Genie** → Natural language queries
3. 📊 **Create dashboards** → Databricks SQL Dashboards
4. 🧠 **Implement AI** → Use AI Functions (ai_summarize, ai_classify)
5. 🔍 **Vector Search** → Semantic search for similar tickets
6. 🚀 **Deploy Agent** → Model Serving + Lakehouse Apps

## 💡 Demo Tips

1. **Start with the problem**: "Manager needs to understand what's happening without reading 500 tickets"
2. **Show real data**: Tickets in English, payment processing context
3. **Demonstrate AI**: Summarization, classification, recommendations
4. **Highlight insights**: Churn risk, SLA breaches, sentiment trends
5. **Governance**: Show PII tags and Unity Catalog
6. **Scalability**: Delta Lake, Z-ordering, optimizations

---

**Total setup time: ~5 minutes** ⚡  
**Ready to demonstrate!** 🎯
