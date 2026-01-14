# Databricks Genie - Example Prompts for Tickets Agent (English)

## 📘 About Genie

Databricks Genie is an AI-powered analyst that lets you query your data using natural language.

## 🎯 Setup Genie Space

1. In Databricks, go to **Genie**
2. Click **Create Space**
3. Select your tables: `companies`, `customers`, `agents`, `tickets`, `ticket_interactions`
4. Name it: "Customer Support Tickets Analysis"
5. Add description: "AI agent for analyzing customer support tickets from a payment processing company"

## 💬 Example Prompts

### Executive Analysis

```
Show me a summary of tickets from the last week
```

```
How many critical tickets are currently open?
```

```
What is the average customer satisfaction this month?
```

```
Show ticket resolution rate by priority
```

### Problem Identification

```
What are the 5 most common issues this month?
```

```
Show ticket categories with worst CSAT scores
```

```
Which subcategories have the most critical tickets?
```

```
List tickets that breached SLA this week
```

### Churn Analysis

```
Which companies are at high risk of churn?
```

```
Show companies with more than 5 complaints last month
```

```
List customers with low NPS (detractors) this week
```

```
Which companies have many urgent unresolved tickets?
```

### Team Performance

```
Which agent has the best average CSAT?
```

```
Show average resolution time by agent
```

```
Which team has the most SLA violations?
```

```
List agents with most tickets resolved this month
```

### Trend Analysis

```
Show ticket trends over the last 3 months
```

```
Compare this week's ticket volume with last week
```

```
Which day of the week has the most tickets opened?
```

```
Show NPS evolution over the last 60 days
```

### Channel Analysis

```
Which channel has the best response time?
```

```
Compare satisfaction across support channels
```

```
How many tickets come through live chat vs email?
```

### Sentiment Analysis

```
Show sentiment distribution of tickets this month
```

```
How many tickets have very negative sentiment?
```

```
Compare sentiment by ticket category
```

### Business Analysis

```
Which business segment opens the most tickets?
```

```
Show large companies with low satisfaction
```

```
List top 10 companies by transaction volume that have open tickets
```

## 🎨 Advanced Queries

```
Show RETAIL segment companies with churn risk above 0.7 and more than 3 urgent tickets
```

```
List critical tickets from LARGE companies that still don't have an assigned agent
```

```
What is the correlation between resolution time and customer satisfaction?
```

```
Which companies are likely to cancel based on recent tickets?
```

```
Identify patterns in tickets that lead to escalations
```

```
Show reopened tickets multiple times - is there a pattern?
```

## 💡 Tips for Better Queries

### ✅ DO
- Use natural, conversational language
- Be specific about time periods
- Ask for comparisons and trends
- Request visual outputs (charts, tables)

### ❌ DON'T
- Don't use technical SQL syntax
- Avoid ambiguous terms
- Don't ask multiple unrelated questions at once

## 🔄 Follow-up Questions

```
Initial: "Show critical open tickets"
Follow-up: "Filter only RETAIL segment"
Follow-up: "Show interaction history for these tickets"
Follow-up: "Which agent would be best for each?"
```

## 🎯 Demo Script

**Start with context:**
> "I'm a support manager and want to understand what's happening this week without reading hundreds of tickets."

**Progressive discovery:**
1. "Show me a summary of tickets this week"
2. "What are the main problems?"
3. "Show companies at risk of churn"
4. "What's the performance of the support team?"
5. "Recommend 3 priority actions"

**Address specific concerns:**
> "We have many complaints about mobile payments. Show detailed analysis."

**Proactive management:**
> "Identify customers we should contact today to prevent churn."

## 📈 Business Value

**Traditional approach:**
- Write SQL queries (20 min)
- Export to Excel (5 min)
- Create visualizations (15 min)
- Write summary (10 min)
- **Total: 50 minutes**

**With Genie:**
- Ask in natural language (30 seconds)
- Get instant results with charts
- AI-generated insights included
- **Total: 30 seconds**

**ROI: 100x faster!** ⚡

## 🎓 Teaching Genie About Your Business

Add context to your Genie Space:

**Instructions for Genie:**
```
Context: This is a payment processing company. 
Customers use POS terminals to accept credit cards, debit cards, and mobile payments.

Important definitions:
- CRITICAL priority: Must be resolved in 4 hours
- HIGH priority: Must be resolved in 8 hours
- Churn risk > 0.7 is considered high risk
- CSAT >= 4.0 is considered satisfied
- NPS 9-10 = Promoter, 7-8 = Passive, 0-6 = Detractor

Business priorities:
1. Prevent churn of high-value customers
2. Maintain SLA compliance > 95%
3. Keep CSAT above 4.0
4. Resolve critical issues within SLA
```

---

**Ready to ask your first question?** 🎤
