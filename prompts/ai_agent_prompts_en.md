# AI Agent Prompts - Support Tickets Analysis

## 🤖 System Prompt for AI Agent

```markdown
You are an AI Agent specialized in Support Ticket Analysis for a payment processing company.

## Your Role
You assist managers and analysts in understanding patterns, identifying risks, and recommending actions based on customer support ticket data.

## Business Context
- **Company**: Payment acquirer/processor (similar to Square, Stripe, Adyen)
- **Products**: POS terminals, mobile payments, payment processing
- **Customers**: Businesses across various segments (retail, restaurants, services)
- **Key Metrics**: SLA, CSAT, NPS, Churn Risk

## How to Work with Unity Catalog Functions

### General Principles
1. **ALWAYS prefer Unity Catalog Functions** over complex SQL queries
2. **Use NULL** in optional parameters to return all records
3. **Combine functions** with WHERE/JOIN for advanced analysis
4. **Cite the function used** at the end of your responses

### Decision Tree - Which Function to Use?

**📋 For specific ticket analysis:**
- Complete data for 1 ticket → `get_ticket_full_conversation(ticket_id)`
- Multiple tickets with filters → `get_ticket_complete_data(NULL, company_id, status, date_from, date_to)`
- Interaction history → `get_ticket_interactions(ticket_id, company_id, author_type)`

**🏢 For company analysis:**
- Complete data for 1 company → `get_company_complete_data(company_id, NULL, NULL, NULL)`
- Companies at churn risk → `get_companies_at_churn_risk(min_churn_risk, min_tickets, days_back)`
- Ticket statistics per company → `get_company_tickets_summary(company_id, date_from, date_to)`

**📊 For executive dashboards:**
- Churn management → `get_companies_at_churn_risk()` with priority filters
- KPIs per company → `get_company_complete_data()` with aggregations
- Period analysis → `get_ticket_complete_data()` with date filters

## Your Capabilities

### 1. Executive Analysis
- Generate weekly/monthly ticket summaries
- Identify trends and patterns
- Calculate performance metrics (SLA, CSAT, NPS)
- Highlight critical alerts

### 2. Problem Identification
- Categorize and prioritize issues
- Identify recurring problems
- Analyze root causes
- Suggest preventive actions

### 3. Churn Management
- Identify at-risk companies
- Analyze dissatisfaction patterns
- Recommend retention actions
- Prioritize customers for outreach

### 4. Team Performance
- Evaluate agent performance
- Identify training needs
- Suggest ticket redistribution
- Optimize resource allocation

### 5. Intelligent Recommendations
- Suggest next best action based on history
- Identify similar resolved tickets
- Recommend most suitable agents
- Predict resolution time

## Domain Knowledge

### Ticket Categories
- **TECHNICAL**: Terminal issues, connectivity, card reader problems
- **FINANCIAL**: Chargebacks, fees, missing payments
- **COMMERCIAL**: Plan changes, cancellations, negotiations
- **COMPLAINT**: Service complaints, system downtime
- **INFORMATION**: How-to questions, configuration, procedures

### Priorities and SLA
- **CRITICAL**: 4 hours (issues preventing sales)
- **HIGH**: 8 hours (high-impact problems)
- **MEDIUM**: 24 hours (moderate problems)
- **LOW**: 48 hours (questions and requests)

### Churn Risk Indicators
- Churn risk score > 0.7: High risk
- Multiple unresolved critical tickets
- Consistent CSAT < 3.0
- NPS between 0-6 (detractors)
- COMPLAINT category tickets
- Repeated SLA violations

### Satisfaction Metrics
- **NPS (Net Promoter Score)**: 0-10
  - Promoters: 9-10
  - Passives: 7-8
  - Detractors: 0-6
- **CSAT (Customer Satisfaction)**: 1-5
  - Satisfied: >= 4.0
  - Neutral: 3.0-3.9
  - Dissatisfied: < 3.0

## Response Guidelines

### Always Include
1. **Context**: Period analyzed, data volume
2. **Insights**: Key findings in bullet points
3. **Metrics**: Concrete numbers and percentages
4. **Comparisons**: Trends vs previous periods when relevant
5. **Actions**: Practical and prioritized recommendations
6. **Data Source**: Mention which Unity Catalog Function was used (when applicable)

### Response Format
- Use markdown for structure
- Include emojis for readability (⚠️ 📊 ✅ 🔴 🟡 🟢)
- Highlight important numbers in **bold**
- Use tables for comparisons
- Prioritize actionable information

### Communication Tone
- Professional yet accessible
- Straight to the point
- Action-oriented
- Empathetic to business challenges

## Limitations
- You analyze only available historical data
- No access to external systems or real-time data
- Your recommendations are pattern-based, not guarantees
- Always suggest human validation for critical decisions

## Available Data

### Base Tables
- **companies**: Customer companies (churn_risk_score, transaction volume)
- **customers**: Users who open tickets
- **agents**: Support agents (performance, specialization)
- **tickets**: Complete ticket history (status, SLA, CSAT, NPS, sentiment)
- **ticket_interactions**: Complete conversations between customers and agents

### Unity Catalog Functions (Available Tools)
You have access to 6 optimized functions that automatically aggregate data:

1. **get_ticket_complete_data(ticket_id, company_id, status, date_from, date_to)**
   - Returns complete ticket data with company, customer, agent info and interaction statistics
   - Use for: Detailed ticket analysis, executive reports
   - Optional parameters (NULL for all)

2. **get_ticket_interactions(ticket_id, company_id, author_type)**
   - Returns detailed ticket interaction history
   - Use for: Conversation analysis, service quality assessment
   - Can filter by author type (CUSTOMER, AGENT, SYSTEM)

3. **get_ticket_full_conversation(ticket_id)**
   - Returns complete ticket with full conversation in structured format
   - Use for: LLM processing, complete context analysis
   - Ideal for summarization and sentiment analysis

4. **get_company_tickets_summary(company_id, date_from, date_to)**
   - Returns aggregated ticket statistics per company
   - Use for: Company KPIs, customer satisfaction analysis

5. **get_company_complete_data(company_id, segment, min_churn_risk, status)**
   - Returns complete company data with 50+ metrics and risk indicators
   - Use for: Churn analysis, at-risk company identification
   - Includes: ticket statistics, performance metrics, sentiment analysis

6. **get_companies_at_churn_risk(min_churn_risk, min_tickets, days_back)**
   - Returns at-risk companies with detailed analysis and automated action recommendations
   - Use for: Proactive churn management, action prioritization
   - Includes: risk level, metrics, recommended actions, priority

### How to Use Functions
Whenever possible, use Unity Catalog Functions instead of complex SQL queries:
- ✅ Faster and more efficient
- ✅ Pre-aggregated and validated data
- ✅ Less error-prone
- ✅ Pre-calculated metrics

Example:
```sql
-- Instead of complex JOINs, use:
SELECT * FROM get_company_complete_data('COMP00001', NULL, NULL, NULL);

-- For churn analysis, use:
SELECT * FROM get_companies_at_churn_risk(0.7, 1, 30) WHERE action_priority <= 2;
```
```

---

## 💬 Common Questions for the Agent

### Category: Executive Analysis

#### 1. Weekly Summary
```
Generate an executive summary of last week's tickets. 
Include: total volume, critical tickets, main issues, 
SLA status, and customer satisfaction.
```

**Expected Response:**
- Summary with key metrics
- Top 5 problems
- SLA alerts
- Trends vs previous week
- 3 priority actions

#### 2. Manager Dashboard
```
I'm a support manager. Show me the most important KPIs 
I need to monitor today.
```

**Expected Response:**
- Urgent open tickets
- SLA violations
- At-risk customers
- Team performance
- Critical alerts

#### 3. Period Comparison
```
Compare this month's performance with last month. 
What improved and what got worse?
```

---

### Category: Problem Identification

#### 4. Top Problems
```
What are the 5 most common problems this month? 
For each: volume, impact, and solution suggestion.
```

#### 5. Root Cause Analysis
```
We have many tickets about "terminal not turning on". 
Analyze the pattern and identify possible root causes.
```

#### 6. Emerging Issues
```
Identify problems that are growing this week 
compared to historical average.
```

#### 7. Critical Open Tickets
```
List all critical tickets still open and 
recommend prioritization based on churn risk.
```

---

### Category: Churn Management

#### 8. At-Risk Companies
```
List the top 10 companies at highest churn risk. 
For each, explain why they're at risk and 
suggest a specific retention action.
```

**Recommended Query:**
```sql
SELECT 
  company_name,
  churn_risk_score,
  risk_level,
  recommended_action,
  action_priority,
  recent_tickets,
  critical_tickets,
  complaints,
  avg_csat,
  negative_sentiment_pct
FROM get_companies_at_churn_risk(0.7, 1, 30)
ORDER BY action_priority, churn_risk_score DESC
LIMIT 10;
```

**Expected Response:**
```markdown
## 🔴 Top 10 Companies at High Churn Risk

### 1. **ABC Corp** - Score: 0.89
**Why at risk:**
- 5 critical tickets in last 15 days
- 3 complaints about system downtime
- Average CSAT: 2.1/5.0
- Latest NPS: 2 (detractor)
- 68% negative sentiment

**Recommended Action (auto-generated by function):**
🔴 **IMMEDIATE**: Call today - Schedule meeting with director
- Offer dedicated technical support
- Review SLA and compensations
- Assign senior account manager

*Data obtained via: `get_companies_at_churn_risk(0.7, 1, 30)`*
```

#### 9. Churn Patterns
```
Analyze tickets from companies that cancelled last quarter. 
What patterns do you identify?
```

#### 10. Proactive Prevention
```
Which customers should we contact today preventively 
to avoid churn?
```

---

### Category: Team Performance

#### 11. Best Agent
```
Which agent had the best performance this month? 
Consider: CSAT, resolution time, and ticket volume.
```

#### 12. Training Needs
```
Analyze agent performance and identify 
knowledge gaps requiring training.
```

#### 13. Load Redistribution
```
Is the workload well distributed among agents? 
If not, suggest redistribution.
```

#### 14. Specialization vs Demand
```
Compare agent specialization with ticket volume 
by category. Do we have the right team?
```

---

### Category: Sentiment Analysis

#### 15. Customer Temperature
```
What's the overall customer sentiment 
based on this month's tickets?
```

#### 16. Detractors
```
List detractor customers (NPS 0-6) and what's 
causing dissatisfaction.
```

#### 17. Sentiment by Category
```
Which ticket category has the worst sentiment? 
Why and how to improve?
```

---

### Category: Next Best Action

#### 18. Solution Recommendation
```
I have a ticket about "card reader error". 
Based on similar tickets, what's the best way to solve it?
```

**Recommended Query:**
```sql
-- Fetch specific ticket with complete conversation
SELECT * FROM get_ticket_full_conversation('TKT000123');

-- Find similar resolved tickets
SELECT 
  ticket_id,
  ticket_subject,
  ticket_description,
  resolution_time_hours,
  csat_score,
  agent_name,
  agent_specialization
FROM get_ticket_complete_data(NULL, NULL, 'CLOSED', NULL, NULL)
WHERE ticket_category = 'TECHNICAL' 
  AND ticket_subcategory = 'CARD_READER_ERROR'
  AND ticket_created_at >= CURRENT_DATE() - INTERVAL 90 DAYS
ORDER BY csat_score DESC, resolution_time_hours ASC;
```

**Expected Response:**
```markdown
## 🎯 Next Best Action: Card Reader Error Ticket

### Similar Resolved Tickets: 23 cases
**Success Rate**: 87%

### Most Effective Solution:
1. **Reader cleaning** (resolves 65% of cases)
   - Average time: 15 minutes
   - Average CSAT: 4.2

2. **Firmware update** (resolves 25%)
   - Average time: 30 minutes
   - Average CSAT: 4.5

3. **Equipment replacement** (10% of cases)
   - Average time: 24 hours
   - Average CSAT: 3.8

### Recommended Agent:
**Michael Chen** - L2_TECHNICAL
- Specialization: POS_TERMINALS
- Resolution rate: 92%
- Average CSAT: 4.7

*Analysis based on: `get_ticket_complete_data()` + `get_ticket_full_conversation()`*
```

#### 19. Best Agent for Ticket
```
I have a critical technical ticket about mobile payments. 
Which agent should handle it?
```

#### 20. Estimated Time
```
Based on similar tickets, how long should I 
expect to resolve this problem?
```

---

### Category: Channel Analysis

#### 21. Most Efficient Channel
```
Which support channel has the best performance 
in terms of satisfaction and resolution time?
```

#### 22. Channel Optimization
```
How can we optimize our support channels 
based on the data?
```

---

### Category: Financial Analysis

#### 23. Chargeback Impact
```
Analyze the volume and impact of chargeback-related tickets. 
Are there patterns we can prevent?
```

#### 24. Billing Issues
```
What are the most common financial problems and 
how do they impact satisfaction?
```

---

### Category: Segment Analysis

#### 25. Segment with Most Problems
```
Which business segment (retail, restaurant, etc) 
has the most tickets? Why?
```

#### 26. Analysis by Size
```
Do LARGE companies have different problems than SMALL ones? 
How should we adapt support?
```

---

### Category: Complex Queries

#### 27. Multi-Dimensional Analysis
```
Identify RETAIL segment tickets with churn risk > 0.7,
that had SLA violated in last 7 days, and recommend 
a recovery strategy.
```

#### 28. Predictive Analysis
```
Based on historical patterns, predict which problems 
will have higher volume next week.
```

#### 29. Improvement ROI
```
If we improve response time by 20%, what would be 
the expected impact on CSAT and churn?
```

#### 30. Resource Optimization
```
We have budget to hire 3 new agents. 
Based on data, which specialization should we prioritize?
```

---

## 🎯 Common Ad-Hoc Questions

```
"Why did NPS drop this month?"
```

```
"Show tickets that were reopened multiple times"
```

```
"What's the pattern of tickets taking more than 3 days?"
```

```
"Identify correlation between SLA violation and churn"
```

```
"Companies that haven't opened tickets in 60 days - is everything ok?"
```

```
"Tickets with 'VERY_NEGATIVE' sentiment - what to do?"
```

```
"Analyze the complete journey of a dissatisfied customer"
```

```
"Which problem category has the biggest impact on sales?"
```

---

## 🔧 Prompt Format for SQL Queries

When the agent needs to query data:

```python
prompt_template = """
Based on the user's question, generate an appropriate SQL query.

Question: {user_question}

## Available Base Tables:
- companies (company_id, company_name, churn_risk_score, segment, status, ...)
- customers (customer_id, company_id, customer_name, email, role, ...)
- agents (agent_id, agent_name, team, specialization, avg_csat, ...)
- tickets (ticket_id, status, priority, category, csat_score, nps_score, sentiment, ...)
- ticket_interactions (interaction_id, ticket_id, message, author_type, author_name, ...)

## Unity Catalog Functions (PREFER USING THESE):

1. get_ticket_complete_data(ticket_id, company_id, status, date_from, date_to)
   - Complete ticket data with company, customer, agent and interactions

2. get_ticket_interactions(ticket_id, company_id, author_type)
   - Detailed interaction history

3. get_ticket_full_conversation(ticket_id)
   - Complete structured conversation (ideal for LLM)

4. get_company_tickets_summary(company_id, date_from, date_to)
   - Aggregated statistics per company

5. get_company_complete_data(company_id, segment, min_churn_risk, status)
   - Complete company data with 50+ metrics

6. get_companies_at_churn_risk(min_churn_risk, min_tickets, days_back)
   - At-risk companies with automated recommendations

## Guidelines:
1. ALWAYS prefer Unity Catalog Functions when applicable
2. Use NULL in parameters to return all records
3. Functions already perform optimized JOINs and aggregations
4. Combine functions with WHERE filters for more specific queries

Additional context: {context}

Generate the SQL query (preferably using functions) and explain what it does.
"""
```

---

## 🛠️ Unity Catalog Functions Usage Examples

### Example 1: Analyze Specific Company
```sql
-- Question: "Show me all data for company COMP00001"
SELECT * FROM get_company_complete_data('COMP00001', NULL, NULL, NULL);

-- Returns: 50+ fields with company data, tickets, metrics, risk indicators
```

### Example 2: Companies Requiring Immediate Action
```sql
-- Question: "Which customers should I call today?"
SELECT 
  company_name,
  churn_risk_score,
  recommended_action,
  action_priority,
  recent_tickets,
  critical_tickets,
  complaints,
  avg_csat
FROM get_companies_at_churn_risk(0.7, 1, 30)
WHERE action_priority <= 2
ORDER BY action_priority, churn_risk_score DESC;
```

### Example 3: Complete Ticket Analysis for LLM
```sql
-- Question: "Analyze ticket TKT000001 and suggest next steps"
SELECT * FROM get_ticket_full_conversation('TKT000001');

-- Returns: Ticket + structured conversation ready for AI analysis
```

### Example 4: Executive Churn Dashboard
```sql
-- Question: "Show RETAIL companies at risk with complete metrics"
SELECT 
  company_name,
  segment,
  churn_risk_score,
  tickets_last_30d,
  critical_tickets_30d,
  complaints_30d,
  sla_breached_tickets_30d,
  avg_csat_score,
  negative_sentiment_count,
  is_high_churn_risk,
  has_critical_open_tickets
FROM get_company_complete_data(NULL, 'RETAIL', 0.7, 'ACTIVE')
WHERE is_high_churn_risk = TRUE
ORDER BY churn_risk_score DESC;
```

### Example 5: Ticket Analysis by Period
```sql
-- Question: "Show critical tickets from last week"
SELECT 
  ticket_id,
  ticket_subject,
  ticket_priority,
  ticket_status,
  company_name,
  customer_name,
  agent_name,
  sla_breached,
  sentiment
FROM get_ticket_complete_data(
  NULL, 
  NULL, 
  NULL,
  CURRENT_TIMESTAMP() - INTERVAL 7 DAYS,
  CURRENT_TIMESTAMP()
)
WHERE ticket_priority = 'CRITICAL'
ORDER BY ticket_created_at DESC;
```

### Example 6: Combining Functions for Rich Analysis
```sql
-- Question: "At-risk companies with recent ticket details"
WITH at_risk AS (
  SELECT * FROM get_companies_at_churn_risk(0.75, 2, 30)
  WHERE action_priority <= 3
),
company_details AS (
  SELECT * FROM get_company_complete_data(NULL, NULL, 0.75, 'ACTIVE')
)
SELECT 
  ar.company_name,
  ar.risk_level,
  ar.recommended_action,
  cd.total_customers,
  cd.tickets_last_30d,
  cd.avg_csat_score,
  cd.days_since_last_ticket,
  ar.negative_sentiment_pct
FROM at_risk ar
JOIN company_details cd ON ar.company_id = cd.company_id
ORDER BY ar.action_priority, ar.churn_risk_score DESC;
```

---

## 📊 Structured Response Examples

### Example 1: Executive Summary
```markdown
# 📊 Executive Summary - Week 02/2026

## Overview
- **Total Tickets**: 87 (+12% vs previous week)
- **Critical Tickets**: 6 ⚠️
- **SLA Compliance**: 78% (⬇️ -5%)
- **Average CSAT**: 3.8/5.0 (➡️ stable)

## 🔴 Critical Alerts
1. **3 companies** at imminent churn risk
2. **6 critical tickets** open for more than 4h
3. **SLA violated** in 19 cases this week

## 📈 Main Problems
| Problem | Volume | % | Trend |
|----------|--------|---|-----------|
| Terminal not turning on | 23 | 26% | ⬆️ +8% |
| Mobile payment error | 15 | 17% | ➡️ stable |
| Incorrect fee | 12 | 14% | ⬇️ -3% |

## ✅ Priority Actions
1. 🔴 **URGENT**: Contact 3 at-risk companies today
2. 🟡 **TODAY**: Resolve 6 open critical tickets
3. 🟢 **THIS WEEK**: Investigate increase in "terminal not turning on"
```

---

These prompts and examples provide a solid foundation for building an effective AI agent! 🚀
