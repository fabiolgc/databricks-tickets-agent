# AI Agent - Support Ticket Analysis

## 🤖 System Prompt

```markdown
You are a Support Ticket Analysis AI Agent for a payment processing company.

## Context
- **Business**: Payment acquirer (POS terminals, mobile payments, instant payments)
- **Customers**: Companies across retail, restaurants, services
- **Key Metrics**: SLA, CSAT, NPS, Churn Risk

## Your Mission
Analyze support tickets to identify patterns, predict churn, and recommend actions.

## Catalog Tools Available
You have access to 9 Unity Catalog Functions in `fabio_goncalves.tickets_agent`:

1. **get_company_id_by_name**(company_name) - Search company by name
2. **get_company_all_tickets**(company_id) - All company tickets for pattern analysis and next best action
3. **get_ticket_by_id**(ticket_id) - Complete ticket information
4. **get_ticket_interactions**(ticket_id) - Ticket conversation history
5. **get_ticket_full_conversation**(ticket_id) - Ticket with interactions array (for AI)
6. **get_company_info**(company_id) - Complete company information with metrics
7. **get_company_tickets_summary**(company_id) - Aggregated ticket statistics
8. **get_customer_info**(customer_id) - Customer profile and ticket history
9. **get_agent_info**(agent_id) - Agent profile and performance metrics

## ⚡ IMPORTANT: Aggregated Analysis (ALL Companies)

**For executive analysis and reports that need ALL companies, use NULL as parameter:**

| Function | Individual Use | Aggregated Use (ALL) |
|----------|----------------|----------------------|
| `get_company_info()` | `get_company_info('COMP00001')` | `get_company_info(NULL)` ✅ |
| `get_company_tickets_summary()` | `get_company_tickets_summary('COMP00001')` | `get_company_tickets_summary(NULL)` ✅ |
| `get_company_all_tickets()` | `get_company_all_tickets('COMP00001')` | `get_company_all_tickets(NULL)` ✅ |

**Use cases with NULL:**
- 📊 Weekly/monthly executive summary
- 📈 Portfolio dashboard
- 🔍 Top problems across all companies
- ⚠️ At-risk companies (WHERE is_high_churn_risk = TRUE)
- 📉 Aggregated metrics (SUM, AVG, COUNT)

## Quick Reference

### For Company Lookup
- **ALWAYS** use this first when user provides company name → `get_company_id_by_name('company name')`
- Returns company_id to use in other functions
- Supports partial/fuzzy matching (case-insensitive)

### For Ticket Analysis
- Single ticket complete info → `get_ticket_by_id(ticket_id)`
- Ticket conversation history → `get_ticket_interactions(ticket_id)`
- Ticket for AI processing → `get_ticket_full_conversation(ticket_id)` (returns interactions as array)
- **All company tickets** → `get_company_all_tickets(company_id)` (ideal for pattern analysis and next best action)

### For Company Analysis
- Company complete info + metrics → `get_company_info(company_id)`
- Company ticket statistics → `get_company_tickets_summary(company_id)`
- Find companies by name → `get_company_id_by_name('partial name')`

### For Customer/Agent Analysis
- Customer profile + history → `get_customer_info(customer_id)`
- Agent performance metrics → `get_agent_info(agent_id)`

## Domain Knowledge

**Ticket Categories**: TECHNICAL, FINANCIAL, COMMERCIAL, COMPLAINT, INFORMATION

**Priorities**: CRITICAL (4h), HIGH (8h), MEDIUM (24h), LOW (48h)

**Churn Indicators**: score > 0.7, CSAT < 3.0, NPS 0-6, repeated SLA violations

**Satisfaction**: CSAT 1-5 (≥4 good), NPS 0-10 (9-10 promoters, 0-6 detractors)

## Response Format
- Use markdown with emojis (⚠️ 📊 ✅ 🔴 🟡 🟢)
- Include: context, metrics, insights, actions
- Cite the function used
- Be direct and actionable

## Workflow When User Mentions Company Name

**CRITICAL**: When user provides a company name instead of company_id:

1. **First**, call `get_company_id_by_name()` to find the company_id
2. **Then**, use the returned company_id in other functions

## Workflow for Next Best Action

**To generate action recommendations** based on historical data:

1. Use `get_company_all_tickets(company_id)` to get complete history
2. Analyze the fields:
   - `solution_summary` - Solutions applied in similar tickets
   - `is_repeat_issue` - Identifies recurring problems
   - `resolution_time_hours` - Resolution time for similar tickets
   - `csat_score` - Which solutions had better satisfaction
   - `sentiment` - Emotional impact of tickets
3. Identify patterns by `ticket_subcategory`
4. Recommend actions based on tickets with:
   - Same category/subcategory
   - `is_resolved = TRUE`
   - `csat_score >= 4.0`
   - Lower `resolution_time_hours`

```sql
-- Step 1: Get company_id from name
SELECT company_id, company_name 
FROM fabio_goncalves.tickets_agent.get_company_id_by_name('Pizza Express');

-- Step 2: Use company_id in other functions
SELECT * 
FROM fabio_goncalves.tickets_agent.get_company_tickets_summary('COMP00123');
```

## Examples

### Example 1: Company Name Lookup
```sql
-- Find company by name (partial match works)
SELECT company_id, company_name, segment, churn_risk_score
FROM fabio_goncalves.tickets_agent.get_company_id_by_name('Restaurant');
```

### Example 2: Ticket Details
```sql
SELECT * 
FROM fabio_goncalves.tickets_agent.get_ticket_by_id('TKT000001');
```

### Example 3: Company Deep Dive
```sql
SELECT * 
FROM fabio_goncalves.tickets_agent.get_company_info('COMP00001');
```

### Example 4: Company Ticket Summary
```sql
SELECT * 
FROM fabio_goncalves.tickets_agent.get_company_tickets_summary('COMP00001');
```

### Example 5: All Company Tickets (for Next Best Action)
```sql
-- Analyze all tickets to identify patterns and recommend actions
SELECT ticket_id, ticket_subject, ticket_category, ticket_status,
       solution_summary, is_repeat_issue, sentiment, 
       resolution_time_hours, sla_breached
FROM fabio_goncalves.tickets_agent.get_company_all_tickets('COMP00001')
ORDER BY ticket_created_at DESC;
```

### Example 6: At-Risk Companies (using direct query)
```sql
SELECT company_id, company_name, churn_risk_score, 
       total_tickets_all_time, complaints_30d, sla_breached_tickets_30d
FROM fabio_goncalves.tickets_agent.get_company_info('COMP00001')
WHERE is_high_churn_risk = TRUE;
```

Always prefer catalog functions over complex JOINs.
```

---

## 🔧 Detailed Function Usage Guide

### 1️⃣ get_company_id_by_name(company_name)
**When to use**: Whenever user mentions company name
**Returns**: company_id, company_name, segment, company_size, status, churn_risk_score

```sql
-- Example: Flexible search
SELECT * FROM get_company_id_by_name('pizza');
-- Returns: Pizza Express, Central Pizza, etc.

-- Workflow usage
WITH company AS (
  SELECT company_id FROM get_company_id_by_name('Tech Solutions') LIMIT 1
)
SELECT * FROM get_company_info((SELECT company_id FROM company));
```

### 2️⃣ get_company_all_tickets(company_id)
**When to use**: For pattern analysis, next best action, identify recurring issues
**Parameter**: company_id (STRING) - Use 'COMP00001' for specific company, **NULL for ALL companies**
**Important fields**: solution_summary, is_repeat_issue, is_resolved, has_negative_sentiment

```sql
-- Find effective solutions for specific problem (ONE company)
SELECT solution_summary, resolution_time_hours, csat_score
FROM get_company_all_tickets('COMP00001')
WHERE ticket_subcategory = 'CARD_READER_ERROR'
  AND is_resolved = TRUE
  AND csat_score >= 4.0
ORDER BY ticket_created_at DESC LIMIT 5;

-- Executive analysis - ALL companies (last week)
SELECT 
  COUNT(DISTINCT ticket_id) AS total_tickets,
  SUM(CASE WHEN ticket_priority = 'CRITICAL' THEN 1 ELSE 0 END) AS critical,
  AVG(csat_score) AS avg_satisfaction
FROM get_company_all_tickets(NULL)
WHERE ticket_created_at >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS;

-- Top 5 problems across ALL companies
SELECT ticket_subcategory, COUNT(*) as total
FROM get_company_all_tickets(NULL)
WHERE ticket_created_at >= CURRENT_TIMESTAMP() - INTERVAL 30 DAYS
GROUP BY ticket_subcategory
ORDER BY total DESC LIMIT 5;
```

### 3️⃣ get_ticket_by_id(ticket_id)
**When to use**: For detailed analysis of a specific ticket
**Returns**: All ticket data + company + customer + agent + metrics

```sql
-- Complete ticket analysis
SELECT ticket_id, ticket_subject, ticket_status, 
       company_name, customer_name, agent_name,
       resolution_time_hours, csat_score, sentiment
FROM get_ticket_by_id('TKT000001');
```

### 4️⃣ get_ticket_interactions(ticket_id)
**When to use**: To see chronological conversation history
**Returns**: List of messages ordered by timestamp

```sql
-- View entire conversation
SELECT interaction_timestamp, author_type, author_name, message
FROM get_ticket_interactions('TKT000001')
ORDER BY interaction_timestamp;
```

### 5️⃣ get_ticket_full_conversation(ticket_id)
**When to use**: To process conversation with AI/LLM (returns structured array)
**Returns**: Complete ticket + interactions array

```sql
-- For sentiment analysis or summarization
SELECT ticket_id, ticket_subject, interactions
FROM get_ticket_full_conversation('TKT000001');
```

### 6️⃣ get_company_info(company_id)
**When to use**: For deep company analysis with KPIs and risk indicators
**Parameter**: company_id (STRING) - Use 'COMP00001' for specific company, **NULL for ALL companies**
**Returns**: 40+ fields including ticket metrics, satisfaction, churn risk

```sql
-- Executive dashboard for ONE company
SELECT company_name, churn_risk_score, 
       total_tickets_all_time, tickets_last_30d,
       avg_csat_score, avg_nps_score,
       is_high_churn_risk, has_critical_open_tickets
FROM get_company_info('COMP00001');

-- Complete portfolio - ALL at-risk companies
SELECT company_id, company_name, churn_risk_score,
       complaints_30d, sla_breached_tickets_30d,
       avg_csat_score
FROM get_company_info(NULL)
WHERE is_high_churn_risk = TRUE
ORDER BY churn_risk_score DESC;

-- Executive summary - ALL companies
SELECT 
  COUNT(*) AS total_companies,
  SUM(CASE WHEN is_high_churn_risk THEN 1 ELSE 0 END) AS at_risk,
  SUM(tickets_last_30d) AS total_tickets_30d,
  AVG(avg_csat_score) AS portfolio_csat
FROM get_company_info(NULL);
```

### 7️⃣ get_company_tickets_summary(company_id)
**When to use**: For aggregated ticket statistics of company
**Parameter**: company_id (STRING) - Use 'COMP00001' for specific company, **NULL for ALL companies**
**Returns**: Counters by status, priority, SLA, average metrics

```sql
-- Quick KPIs for ONE company
SELECT company_name, total_tickets, open_tickets,
       avg_resolution_time_hours, avg_csat_score,
       sla_breached_tickets
FROM get_company_tickets_summary('COMP00001');

-- Compare ALL companies
SELECT company_name, company_segment,
       total_tickets, sla_breached_tickets,
       avg_csat_score
FROM get_company_tickets_summary(NULL)
ORDER BY sla_breached_tickets DESC;
```

### 8️⃣ get_customer_info(customer_id)
**When to use**: For customer profile analysis and history
**Returns**: Customer data + ticket statistics

```sql
-- Complete customer profile
SELECT customer_name, customer_email, customer_role,
       total_tickets, avg_csat_score
FROM get_customer_info('CUST00001');
```

### 9️⃣ get_agent_info(agent_id)
**When to use**: To evaluate agent performance and specialization
**Returns**: Agent data + performance metrics

```sql
-- Agent performance
SELECT agent_name, agent_specialization,
       total_tickets_resolved, avg_csat,
       tickets_30d, avg_csat_30d
FROM get_agent_info('AGENT001');

-- Find best agent for technical ticket
SELECT agent_name, agent_specialization, avg_csat
FROM get_agent_info('AGENT001')
WHERE agent_specialization LIKE '%TECHNICAL%'
ORDER BY avg_csat DESC;
```

---

## 🎯 Common Query Patterns

### Pattern 1: Weekly Executive Summary (ALL Companies)
```sql
-- Complete executive summary for last week
WITH weekly_tickets AS (
  SELECT *
  FROM get_company_all_tickets(NULL)
  WHERE ticket_created_at >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
),
problems_summary AS (
  SELECT 
    ticket_subcategory,
    COUNT(*) as occurrence_count,
    AVG(csat_score) as avg_satisfaction
  FROM weekly_tickets
  GROUP BY ticket_subcategory
  ORDER BY occurrence_count DESC
  LIMIT 5
)
SELECT 
  -- Volume
  (SELECT COUNT(DISTINCT ticket_id) FROM weekly_tickets) as total_tickets_week,
  (SELECT COUNT(DISTINCT company_id) FROM weekly_tickets) as companies_with_tickets,
  
  -- Critical Tickets
  (SELECT COUNT(*) FROM weekly_tickets WHERE ticket_priority = 'CRITICAL') as critical_tickets,
  
  -- SLA
  (SELECT COUNT(*) FROM weekly_tickets WHERE sla_breached = TRUE) as sla_violations,
  (SELECT ROUND(AVG(resolution_time_hours), 2) FROM weekly_tickets WHERE is_resolved = TRUE) as avg_resolution_hours,
  
  -- Satisfaction
  (SELECT ROUND(AVG(csat_score), 2) FROM weekly_tickets WHERE csat_score IS NOT NULL) as avg_csat,
  (SELECT COUNT(*) FROM weekly_tickets WHERE has_negative_sentiment = TRUE) as negative_sentiment_count,
  
  -- Top 5 Problems
  (SELECT COLLECT_LIST(STRUCT(ticket_subcategory, occurrence_count, avg_satisfaction)) 
   FROM problems_summary) as top_problems;
```

### Pattern 2: Individual Company Analysis Workflow
```sql
-- 1. Find company
WITH comp AS (
  SELECT company_id FROM get_company_id_by_name('Restaurant') LIMIT 1
),
-- 2. Get company info
comp_info AS (
  SELECT * FROM get_company_info((SELECT company_id FROM comp))
),
-- 3. Analyze tickets
comp_tickets AS (
  SELECT * FROM get_company_all_tickets((SELECT company_id FROM comp))
)
SELECT 
  ci.company_name,
  ci.churn_risk_score,
  COUNT(ct.ticket_id) as total_tickets,
  AVG(ct.csat_score) as avg_satisfaction
FROM comp_info ci
CROSS JOIN comp_tickets ct
GROUP BY ci.company_name, ci.churn_risk_score;
```

### Pattern 3: Next Best Action
```sql
-- Recommend solution based on history
WITH similar_tickets AS (
  SELECT solution_summary, csat_score, resolution_time_hours
  FROM get_company_all_tickets('COMP00001')
  WHERE ticket_subcategory = 'INSTANT_PAYMENT_ERROR'
    AND is_resolved = TRUE
    AND csat_score >= 4.0
  ORDER BY ticket_created_at DESC
  LIMIT 10
)
SELECT 
  solution_summary,
  AVG(csat_score) as avg_satisfaction,
  AVG(resolution_time_hours) as avg_time
FROM similar_tickets
GROUP BY solution_summary
ORDER BY avg_satisfaction DESC, avg_time ASC;
```

### Pattern 4: Identify At-Risk Customers
```sql
-- Companies at high risk + critical open tickets
SELECT 
  company_id, company_name, churn_risk_score,
  critical_tickets_30d, complaints_30d,
  avg_csat_score, days_since_last_ticket
FROM get_company_info('COMP00001')
WHERE is_high_churn_risk = TRUE
  AND (critical_tickets_30d > 0 OR complaints_30d >= 2)
ORDER BY churn_risk_score DESC;
```

### Pattern 5: Ideal Agent Analysis
```sql
-- Which agent should handle critical instant payment ticket?
SELECT 
  agent_name, agent_specialization,
  avg_csat, tickets_resolved,
  avg_csat_30d, resolved_30d
FROM get_agent_info('AGENT001')
WHERE agent_specialization IN ('INSTANT_PAYMENTS', 'TECHNICAL', 'PAYMENT_GATEWAY')
  AND avg_csat >= 4.0
  AND resolved_30d > 5
ORDER BY avg_csat_30d DESC, resolved_30d DESC;
```

---

## 💬 Common Questions

### Executive Analysis

**1. Weekly Summary**
```
Generate executive summary of last week: volume, critical tickets, main issues, SLA, satisfaction.
Use: get_company_info(NULL) for all companies OR get_company_all_tickets(NULL) filtered by last week.

EXAMPLE:
SELECT 
  COUNT(DISTINCT ticket_id) AS total_tickets_week,
  SUM(CASE WHEN ticket_priority = 'CRITICAL' THEN 1 ELSE 0 END) AS critical,
  AVG(csat_score) AS avg_satisfaction
FROM get_company_all_tickets(NULL)
WHERE ticket_created_at >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS;
```

**2. Manager Dashboard**
```
Most important KPIs to monitor today.
```

**3. Period Comparison**
```
Compare this month with previous. What improved/worsened?
```

---

### Problem Identification

**4. Top Problems**
```
5 most common problems this month with volume, impact, and solution suggestions.
Use: get_company_all_tickets() aggregated by ticket_subcategory.
```

**5. Root Cause Analysis**
```
Many tickets about "terminal not turning on". Analyze patterns and identify root causes.
Use: get_company_all_tickets() filtered by subcategory + analyze solution_summary.
```

**6. Emerging Issues**
```
Problems growing this week vs historical average.
```

**7. Critical Open Tickets**
```
List critical open tickets and prioritize by churn risk.
Use: get_company_all_tickets() WHERE is_critical_open = TRUE, join with get_company_info() for churn_risk_score.
```

---

### Churn Management

**8. At-Risk Companies**
```
List companies at highest churn risk (churn_risk_score > 0.7). 
Why are they at risk? Specific actions for each?
Use: get_company_info() WHERE is_high_churn_risk = TRUE, analyze complaints_30d, sla_breached_tickets_30d.
```

**9. Churn Patterns**
```
Analyze tickets from companies that cancelled last quarter. What patterns?
```

**10. Proactive Prevention**
```
Which customers to contact today preventively?
```

---

### Team Performance

**11. Best Agent**
```
Best agent this month? (CSAT, resolution time, volume)
Use: get_agent_info() for all agents, order by avg_csat_30d and resolved_30d.
```

**12. Training Needs**
```
Knowledge gaps requiring training?
```

**13. Load Distribution**
```
Is workload well distributed? If not, how to redistribute?
```

---

### Sentiment Analysis

**14. Customer Temperature**
```
Overall customer sentiment this month?
```

**15. Detractors**
```
List detractor customers (NPS 0-6) and causes of dissatisfaction.
```

---

### Next Best Action

**16. Solution Recommendation**
```
I have ticket about "card reader error" from company X. 
What's the best way to solve based on similar tickets from this company?
Use: get_company_all_tickets() to analyze historical solutions applied.
```

**17. Best Agent for Ticket**
```
Critical technical ticket about instant payments. Which agent should handle it?
Use: get_agent_info() filtered by agent_specialization and ordered by avg_csat_30d.
```

**18. Estimated Time**
```
Based on similar tickets, expected time to resolve?
Use: get_company_all_tickets() filtered by same subcategory, AVG(resolution_time_hours).
```

---

### Financial Analysis

**19. Chargeback Impact**
```
Volume and impact of chargeback tickets. Patterns to prevent?
```

**20. Billing Issues**
```
Most common financial problems and impact on satisfaction?
```

---

### Segment Analysis

**21. Segment with Most Problems**
```
Which segment (retail, restaurant) has most tickets? Why?
```

**22. Analysis by Company Size**
```
Do LARGE companies have different problems than SMALL? How to adapt support?
```

---

### Complex Queries

**23. Multi-Dimensional Analysis**
```
Analyze RETAIL companies with churn risk > 0.7 and SLA violations in last 7 days. 
What are common problems and recovery strategy?
```

**24. Predictive Analysis**
```
Based on patterns, predict problems with higher volume next week.
```

**25. Resource Optimization**
```
Budget for 3 new agents. Which specialization to prioritize based on data?
```

---

## 🎯 Ad-Hoc Questions

```
"Why did NPS drop this month?"
"Tickets reopened multiple times"
"Pattern of tickets taking 3+ days?"
"Correlation between SLA violation and churn"
"Companies without tickets for 60 days - is everything ok?"
"Tickets with VERY_NEGATIVE sentiment - what to do?"
"Complete journey of a dissatisfied customer"
"Which category has biggest impact on sales?"
```

---

## 📊 Response Template

```markdown
# 📊 [Analysis Title]

## Context
- Period: [date]
- Volume: [number] tickets

## 🔍 Key Insights
1. [insight 1]
2. [insight 2]
3. [insight 3]

## 📈 Key Metrics
| Metric | Value | Trend |
|--------|-------|-------|
| [metric] | [value] | [↑/↓/→] |

## ⚠️ Critical Alerts
- [alert 1]
- [alert 2]

## ✅ Recommended Actions
1. 🔴 **URGENT**: [action]
2. 🟡 **TODAY**: [action]
3. 🟢 **THIS WEEK**: [action]

*Data: `fabio_goncalves.tickets_agent.[function_name]()`*
```

---

## ⚙️ Configuration for LLM

```python
# System configuration
CATALOG = "fabio_goncalves.tickets_agent"

# Function registry
FUNCTIONS = {
    "company_lookup": "get_company_id_by_name",
    "company_all_tickets": "get_company_all_tickets",
    "ticket_details": "get_ticket_by_id",
    "ticket_conversation": "get_ticket_full_conversation",
    "ticket_interactions": "get_ticket_interactions",
    "company_info": "get_company_info",
    "company_summary": "get_company_tickets_summary",
    "customer_info": "get_customer_info",
    "agent_info": "get_agent_info"
}

# Prompt template
prompt = f"""
Question: {{user_question}}

Available tools in {CATALOG}:
{{function_list}}

Generate SQL using catalog functions. Prefer functions over raw table queries.
"""
```

---

## 💡 Best Practices and Tips

### ✅ DOs
1. **Always search by name first**: Use `get_company_id_by_name()` when user mentions company name
2. **Use NULL for aggregated analysis**: For executive reports of ALL companies, pass NULL as company_id
3. **Use get_company_all_tickets() for patterns**: Ideal for historical analysis and next best action
4. **Combine functions with CTEs**: Use WITH clauses for complex queries
5. **Filter relevant data**: Leverage fields like `is_resolved`, `is_repeat_issue`, `has_negative_sentiment`
6. **Analyze satisfaction metrics**: CSAT >= 4.0 indicates effective solutions
7. **Order by timestamp**: Use `ORDER BY ticket_created_at DESC` for most recent data
8. **Use LIMIT wisely**: For large histories, limit to most relevant results

### ❌ DON'Ts
1. **Don't use "ALL" as string**: Use NULL (not string "ALL") to return all companies
2. **Don't do manual JOINs**: Functions already handle necessary JOINs
3. **Don't ignore calculated fields**: Use `is_high_churn_risk`, `is_critical_open` instead of recalculating
4. **Don't fetch unnecessary data**: Use only the function needed for the question
5. **Don't assume IDs**: Always validate company_id before using in other functions

### 🎯 Performance Tips
- For multi-company analysis, use aggregations
- For complete history, `get_company_all_tickets()` is more efficient than multiple calls
- Filter by dates when relevant to reduce processed data
- Use subcategory for granular problem analysis

### 📊 Data Quality Analysis
- **High confidence**: CSAT >= 4.0 AND resolution_time_hours < average AND is_resolved = TRUE
- **Recurring issue**: is_repeat_issue = TRUE OR COUNT(subcategory) > 3 in 30 days
- **At-risk customer**: churn_risk_score > 0.7 AND (complaints_30d >= 2 OR sla_breached_tickets_30d > 0)
- **Effective agent**: avg_csat_30d >= 4.0 AND resolved_30d >= team average

### 🔄 Recommended Workflow
```
1. Identify entity (company/ticket/customer/agent)
2. If name → get_company_id_by_name()
3. Get context → get_company_info() or get_ticket_by_id()
4. Deep analysis → get_company_all_tickets() for patterns
5. Specific metrics → get_company_tickets_summary()
6. Granular details → get_ticket_interactions() or get_ticket_full_conversation()
```

---

**Last updated**: 2026-01-15
