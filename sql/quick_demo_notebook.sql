-- Databricks notebook source
-- MAGIC %md
-- MAGIC # 🚀 Quick Demo - Customer Support Tickets Analysis
-- MAGIC 
-- MAGIC ## Fast 5-minute demonstration notebook
-- MAGIC 
-- MAGIC **Prerequisites:** 
-- MAGIC - Tables already created and loaded
-- MAGIC - Run the `setup_and_analysis_notebook` first if tables don't exist
-- MAGIC 
-- MAGIC **Use this notebook for:**
-- MAGIC - Quick demonstrations
-- MAGIC - Executive presentations
-- MAGIC - Testing Genie capabilities
-- MAGIC 
-- MAGIC ---

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 📊 1. Data Overview - "Show me what we have"

-- COMMAND ----------

-- Quick data validation
SELECT 
    'companies' AS table_name, 
    COUNT(*) AS record_count,
    'Customer companies' AS description
FROM companies

UNION ALL

SELECT 
    'customers', 
    COUNT(*),
    'Individual users'
FROM customers

UNION ALL

SELECT 
    'agents', 
    COUNT(*),
    'Support agents'
FROM agents

UNION ALL

SELECT 
    'tickets', 
    COUNT(*),
    'Support tickets'
FROM tickets

UNION ALL

SELECT 
    'ticket_interactions', 
    COUNT(*),
    'Conversation messages'
FROM ticket_interactions

-- COMMAND ----------

-- Sample tickets view
SELECT 
    t.ticket_id,
    t.created_at,
    t.status,
    t.priority,
    t.category,
    t.subject,
    c.company_name,
    cu.customer_name,
    a.agent_name
FROM tickets t
JOIN companies c ON t.company_id = c.company_id
JOIN customers cu ON t.customer_id = cu.customer_id
LEFT JOIN agents a ON t.agent_id = a.agent_id
ORDER BY t.created_at DESC
LIMIT 10

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 📈 2. Executive Dashboard - "What's happening this week?"

-- COMMAND ----------

-- Weekly KPIs
SELECT 
    COUNT(*) AS total_tickets,
    COUNT(CASE WHEN status = 'OPEN' THEN 1 END) AS open_tickets,
    COUNT(CASE WHEN status = 'IN_PROGRESS' THEN 1 END) AS in_progress,
    COUNT(CASE WHEN status = 'CLOSED' THEN 1 END) AS closed_tickets,
    COUNT(CASE WHEN priority = 'CRITICAL' THEN 1 END) AS critical_tickets,
    ROUND(AVG(CASE WHEN status IN ('RESOLVED', 'CLOSED') THEN resolution_time_hours END), 2) AS avg_resolution_hours,
    SUM(CASE WHEN sla_breached = TRUE THEN 1 ELSE 0 END) AS sla_breaches,
    ROUND(AVG(csat_score), 2) AS avg_csat,
    ROUND(AVG(nps_score), 1) AS avg_nps
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS

-- COMMAND ----------

-- Ticket distribution by status
SELECT 
    status,
    COUNT(*) AS ticket_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS percentage
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY status
ORDER BY ticket_count DESC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 🎯 3. Top Problems - "What are customers complaining about?"

-- COMMAND ----------

-- Top 10 issues
SELECT 
    category,
    subcategory,
    COUNT(*) AS ticket_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS percentage,
    ROUND(AVG(CASE WHEN status IN ('RESOLVED', 'CLOSED') THEN resolution_time_hours END), 2) AS avg_resolution_hours,
    COUNT(CASE WHEN priority IN ('HIGH', 'CRITICAL') THEN 1 END) AS urgent_count
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY category, subcategory
ORDER BY ticket_count DESC
LIMIT 10

-- COMMAND ----------

-- Issues by category with sentiment
SELECT 
    category,
    COUNT(*) AS total_tickets,
    COUNT(CASE WHEN sentiment = 'VERY_NEGATIVE' THEN 1 END) AS very_negative,
    COUNT(CASE WHEN sentiment = 'NEGATIVE' THEN 1 END) AS negative,
    COUNT(CASE WHEN sentiment = 'NEUTRAL' THEN 1 END) AS neutral,
    COUNT(CASE WHEN sentiment = 'POSITIVE' THEN 1 END) AS positive,
    ROUND(AVG(csat_score), 2) AS avg_csat
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY category
ORDER BY total_tickets DESC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## ⚠️ 4. Churn Risk - "Which customers might leave us?"

-- COMMAND ----------

-- High risk companies
SELECT 
    c.company_name,
    c.segment,
    c.company_size,
    c.churn_risk_score,
    c.monthly_transaction_volume,
    COUNT(t.ticket_id) AS recent_tickets_30d,
    SUM(CASE WHEN t.priority IN ('HIGH', 'CRITICAL') THEN 1 ELSE 0 END) AS urgent_tickets,
    SUM(CASE WHEN t.category = 'COMPLAINT' THEN 1 ELSE 0 END) AS complaints,
    ROUND(AVG(t.csat_score), 2) AS avg_csat,
    MAX(t.created_at) AS last_ticket_date
FROM companies c
LEFT JOIN tickets t ON c.company_id = t.company_id 
    AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
WHERE c.churn_risk_score > 0.6
    AND c.status = 'ACTIVE'
GROUP BY c.company_id, c.company_name, c.segment, c.company_size, 
         c.churn_risk_score, c.monthly_transaction_volume
ORDER BY c.churn_risk_score DESC, recent_tickets_30d DESC
LIMIT 20

-- COMMAND ----------

-- Churn risk with recommended actions
SELECT 
    company_name,
    segment,
    churn_risk_score,
    recent_tickets_30d,
    urgent_tickets,
    complaints,
    avg_csat,
    CASE 
        WHEN churn_risk_score > 0.8 AND complaints >= 2 THEN '🔴 IMMEDIATE: Schedule executive call'
        WHEN churn_risk_score > 0.7 AND urgent_tickets >= 3 THEN '🟠 URGENT: Escalate to account manager'
        WHEN churn_risk_score > 0.6 AND avg_csat < 3.0 THEN '🟡 HIGH: Proactive outreach needed'
        ELSE '🟢 Monitor closely'
    END AS recommended_action
FROM (
    SELECT 
        c.company_name,
        c.segment,
        c.churn_risk_score,
        COUNT(t.ticket_id) AS recent_tickets_30d,
        SUM(CASE WHEN t.priority IN ('HIGH', 'CRITICAL') THEN 1 ELSE 0 END) AS urgent_tickets,
        SUM(CASE WHEN t.category = 'COMPLAINT' THEN 1 ELSE 0 END) AS complaints,
        ROUND(AVG(t.csat_score), 2) AS avg_csat
    FROM companies c
    LEFT JOIN tickets t ON c.company_id = t.company_id 
        AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
    WHERE c.churn_risk_score > 0.6
        AND c.status = 'ACTIVE'
    GROUP BY c.company_id, c.company_name, c.segment, c.churn_risk_score
)
ORDER BY churn_risk_score DESC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## ⏱️ 5. SLA Performance - "Are we meeting our commitments?"

-- COMMAND ----------

-- SLA compliance by priority
SELECT 
    priority,
    COUNT(*) AS total_tickets,
    SUM(CASE WHEN sla_breached = TRUE THEN 1 ELSE 0 END) AS sla_breached,
    SUM(CASE WHEN sla_breached = FALSE THEN 1 ELSE 0 END) AS sla_met,
    ROUND(100.0 * SUM(CASE WHEN sla_breached = FALSE THEN 1 ELSE 0 END) / COUNT(*), 1) AS sla_compliance_pct,
    ROUND(AVG(resolution_time_hours), 2) AS avg_resolution_hours,
    CASE priority
        WHEN 'CRITICAL' THEN 4
        WHEN 'HIGH' THEN 8
        WHEN 'MEDIUM' THEN 24
        WHEN 'LOW' THEN 48
    END AS sla_target_hours
FROM tickets
WHERE status IN ('RESOLVED', 'CLOSED')
    AND created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY priority
ORDER BY 
    CASE priority
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        WHEN 'LOW' THEN 4
    END

-- COMMAND ----------

-- Recent SLA breaches requiring attention
SELECT 
    t.ticket_id,
    t.created_at,
    t.priority,
    t.category,
    t.subcategory,
    t.subject,
    t.resolution_time_hours,
    t.status,
    c.company_name,
    a.agent_name
FROM tickets t
JOIN companies c ON t.company_id = c.company_id
LEFT JOIN agents a ON t.agent_id = a.agent_id
WHERE t.sla_breached = TRUE
    AND t.created_at >= CURRENT_DATE - INTERVAL 7 DAYS
ORDER BY 
    CASE t.priority
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        WHEN 'LOW' THEN 4
    END,
    t.created_at DESC
LIMIT 20

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 👥 6. Team Performance - "How is our support team doing?"

-- COMMAND ----------

-- Agent performance (last 30 days)
SELECT 
    a.agent_name,
    a.team,
    a.specialization,
    COUNT(t.ticket_id) AS tickets_handled,
    COUNT(CASE WHEN t.status IN ('RESOLVED', 'CLOSED') THEN 1 END) AS tickets_resolved,
    ROUND(100.0 * COUNT(CASE WHEN t.status IN ('RESOLVED', 'CLOSED') THEN 1 END) / 
          COUNT(t.ticket_id), 1) AS resolution_rate_pct,
    ROUND(AVG(t.resolution_time_hours), 2) AS avg_resolution_hours,
    ROUND(AVG(t.first_response_time_minutes), 2) AS avg_first_response_min,
    ROUND(AVG(t.csat_score), 2) AS avg_csat,
    SUM(CASE WHEN t.sla_breached = TRUE THEN 1 ELSE 0 END) AS sla_breaches
FROM agents a
LEFT JOIN tickets t ON a.agent_id = t.agent_id
    AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
WHERE a.status = 'ACTIVE'
GROUP BY a.agent_id, a.agent_name, a.team, a.specialization
HAVING COUNT(t.ticket_id) > 0
ORDER BY tickets_handled DESC

-- COMMAND ----------

-- Team comparison
SELECT 
    a.team,
    COUNT(DISTINCT a.agent_id) AS agent_count,
    COUNT(t.ticket_id) AS total_tickets,
    ROUND(AVG(t.resolution_time_hours), 2) AS avg_resolution_hours,
    ROUND(AVG(t.csat_score), 2) AS avg_csat,
    SUM(CASE WHEN t.sla_breached = TRUE THEN 1 ELSE 0 END) AS sla_breaches,
    ROUND(100.0 * (COUNT(t.ticket_id) - SUM(CASE WHEN t.sla_breached = TRUE THEN 1 ELSE 0 END)) / 
          COUNT(t.ticket_id), 1) AS sla_compliance_pct
FROM agents a
LEFT JOIN tickets t ON a.agent_id = t.agent_id
    AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
WHERE a.status = 'ACTIVE'
GROUP BY a.team
ORDER BY total_tickets DESC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 😊 7. Customer Satisfaction - "How happy are our customers?"

-- COMMAND ----------

-- NPS breakdown
SELECT 
    CASE 
        WHEN nps_score >= 9 THEN '😍 Promoter (9-10)'
        WHEN nps_score >= 7 THEN '😐 Passive (7-8)'
        WHEN nps_score >= 0 THEN '😞 Detractor (0-6)'
    END AS nps_category,
    COUNT(*) AS response_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS percentage
FROM tickets
WHERE nps_score IS NOT NULL
    AND created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY 
    CASE 
        WHEN nps_score >= 9 THEN '😍 Promoter (9-10)'
        WHEN nps_score >= 7 THEN '😐 Passive (7-8)'
        WHEN nps_score >= 0 THEN '😞 Detractor (0-6)'
    END
ORDER BY 
    CASE 
        WHEN nps_score >= 9 THEN 1
        WHEN nps_score >= 7 THEN 2
        ELSE 3
    END

-- COMMAND ----------

-- CSAT trends by category
SELECT 
    category,
    COUNT(*) AS tickets_with_csat,
    ROUND(AVG(csat_score), 2) AS avg_csat,
    COUNT(CASE WHEN csat_score >= 4.0 THEN 1 END) AS satisfied_count,
    ROUND(100.0 * COUNT(CASE WHEN csat_score >= 4.0 THEN 1 END) / COUNT(*), 1) AS satisfaction_rate_pct
FROM tickets
WHERE csat_score IS NOT NULL
    AND created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY category
ORDER BY avg_csat DESC

-- COMMAND ----------

-- Sentiment distribution
SELECT 
    sentiment,
    COUNT(*) AS ticket_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS percentage
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY sentiment
ORDER BY 
    CASE sentiment
        WHEN 'POSITIVE' THEN 1
        WHEN 'NEUTRAL' THEN 2
        WHEN 'NEGATIVE' THEN 3
        WHEN 'VERY_NEGATIVE' THEN 4
    END

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 📱 8. Channel Analysis - "Which channels work best?"

-- COMMAND ----------

-- Channel performance comparison
SELECT 
    channel,
    COUNT(*) AS total_tickets,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS percentage,
    ROUND(AVG(first_response_time_minutes), 2) AS avg_first_response_min,
    ROUND(AVG(resolution_time_hours), 2) AS avg_resolution_hours,
    ROUND(AVG(csat_score), 2) AS avg_csat
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY channel
ORDER BY total_tickets DESC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 🎯 9. Critical Tickets Needing Immediate Action

-- COMMAND ----------

-- Open critical and high priority tickets
SELECT 
    t.ticket_id,
    t.created_at,
    t.priority,
    t.category,
    t.subcategory,
    t.subject,
    c.company_name,
    c.churn_risk_score,
    cu.customer_name,
    COALESCE(a.agent_name, '⚠️ UNASSIGNED') AS agent_name,
    DATEDIFF(HOUR, t.created_at, CURRENT_TIMESTAMP()) AS hours_open
FROM tickets t
JOIN companies c ON t.company_id = c.company_id
JOIN customers cu ON t.customer_id = cu.customer_id
LEFT JOIN agents a ON t.agent_id = a.agent_id
WHERE t.status IN ('OPEN', 'IN_PROGRESS')
    AND t.priority IN ('CRITICAL', 'HIGH')
ORDER BY 
    CASE t.priority WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 END,
    t.created_at ASC

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 🔍 10. Detailed Ticket Investigation

-- COMMAND ----------

-- Example: View complete ticket with conversation
-- Change ticket_id to investigate specific tickets

SELECT 
    t.ticket_id,
    t.created_at,
    t.status,
    t.priority,
    t.category,
    t.subject,
    t.description,
    c.company_name,
    cu.customer_name,
    a.agent_name
FROM tickets t
JOIN companies c ON t.company_id = c.company_id
JOIN customers cu ON t.customer_id = cu.customer_id
LEFT JOIN agents a ON t.agent_id = a.agent_id
WHERE t.ticket_id = 'TKT000001'  -- Change this ID

-- COMMAND ----------

-- View conversation for a specific ticket
SELECT 
    interaction_timestamp,
    author_type,
    author_name,
    message
FROM ticket_interactions
WHERE ticket_id = 'TKT000001'  -- Change this ID
ORDER BY interaction_timestamp

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 📊 11. Business Intelligence Insights

-- COMMAND ----------

-- Tickets by business segment
SELECT 
    c.segment,
    COUNT(t.ticket_id) AS total_tickets,
    COUNT(DISTINCT c.company_id) AS company_count,
    ROUND(AVG(tickets_per_company), 1) AS avg_tickets_per_company,
    ROUND(AVG(t.csat_score), 2) AS avg_csat
FROM companies c
LEFT JOIN tickets t ON c.company_id = t.company_id 
    AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
LEFT JOIN (
    SELECT company_id, COUNT(*) AS tickets_per_company
    FROM tickets
    WHERE created_at >= CURRENT_DATE - INTERVAL 30 DAYS
    GROUP BY company_id
) tpc ON c.company_id = tpc.company_id
GROUP BY c.segment
ORDER BY total_tickets DESC

-- COMMAND ----------

-- Time-based patterns - tickets by day of week
SELECT 
    DAYOFWEEK(created_at) AS day_of_week,
    CASE DAYOFWEEK(created_at)
        WHEN 1 THEN 'Sunday'
        WHEN 2 THEN 'Monday'
        WHEN 3 THEN 'Tuesday'
        WHEN 4 THEN 'Wednesday'
        WHEN 5 THEN 'Thursday'
        WHEN 6 THEN 'Friday'
        WHEN 7 THEN 'Saturday'
    END AS day_name,
    COUNT(*) AS ticket_count,
    ROUND(AVG(first_response_time_minutes), 2) AS avg_response_time
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 60 DAYS
GROUP BY DAYOFWEEK(created_at)
ORDER BY day_of_week

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 📋 12. Executive Summary Query
-- MAGIC 
-- MAGIC Single query for executive dashboard

-- COMMAND ----------

WITH summary_stats AS (
    SELECT 
        COUNT(*) AS total_tickets,
        COUNT(CASE WHEN status = 'OPEN' THEN 1 END) AS open_tickets,
        COUNT(CASE WHEN priority = 'CRITICAL' THEN 1 END) AS critical_tickets,
        ROUND(AVG(CASE WHEN status IN ('RESOLVED', 'CLOSED') THEN resolution_time_hours END), 2) AS avg_resolution_hours,
        SUM(CASE WHEN sla_breached = TRUE THEN 1 ELSE 0 END) AS sla_breaches,
        ROUND(AVG(csat_score), 2) AS avg_csat
    FROM tickets
    WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS
),
churn_risk AS (
    SELECT COUNT(*) AS high_risk_companies
    FROM companies
    WHERE churn_risk_score > 0.7
        AND status = 'ACTIVE'
),
top_category AS (
    SELECT category, COUNT(*) AS count
    FROM tickets
    WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS
    GROUP BY category
    ORDER BY count DESC
    LIMIT 1
)
SELECT 
    s.*,
    c.high_risk_companies,
    t.category AS top_issue_category,
    t.count AS top_issue_count
FROM summary_stats s
CROSS JOIN churn_risk c
CROSS JOIN top_category t

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ---
-- MAGIC # ✅ Demo Complete!
-- MAGIC ---
-- MAGIC 
-- MAGIC ## 💡 Key Takeaways:
-- MAGIC 
-- MAGIC 1. **Real-time Insights**: All metrics updated automatically
-- MAGIC 2. **Churn Prevention**: Proactive identification of at-risk customers
-- MAGIC 3. **Performance Tracking**: SLA compliance and team metrics
-- MAGIC 4. **Customer Satisfaction**: NPS/CSAT trends and sentiment analysis
-- MAGIC 5. **Actionable Intelligence**: Prioritized recommendations
-- MAGIC 
-- MAGIC ## 🚀 Next Steps:
-- MAGIC 
-- MAGIC - **Genie**: Try asking these queries in natural language
-- MAGIC - **Dashboards**: Create visualizations from these queries
-- MAGIC - **Alerts**: Set up automated notifications
-- MAGIC - **AI Functions**: Add summarization and classification
-- MAGIC 
-- MAGIC ---
-- MAGIC 
-- MAGIC **Questions to try in Genie:**
-- MAGIC - "Mostre empresas em risco de churn"
-- MAGIC - "Quais são os principais problemas esta semana?"
-- MAGIC - "Como está a performance do time de suporte?"
-- MAGIC - "Quantos tickets violaram SLA?"
-- MAGIC 
-- MAGIC ---

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## 🎯 Bonus: Sample Genie-style Queries
-- MAGIC 
-- MAGIC These queries demonstrate what Genie can answer:

-- COMMAND ----------

-- "Show me companies at risk of leaving"
SELECT 
    company_name,
    churn_risk_score,
    segment,
    monthly_transaction_volume
FROM companies
WHERE churn_risk_score > 0.7
ORDER BY churn_risk_score DESC
LIMIT 10

-- COMMAND ----------

-- "What are the most common problems?"
SELECT 
    category,
    COUNT(*) AS ticket_count
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY category
ORDER BY ticket_count DESC

-- COMMAND ----------

-- "Which agent has the best customer satisfaction?"
SELECT 
    a.agent_name,
    a.team,
    ROUND(AVG(t.csat_score), 2) AS avg_csat,
    COUNT(t.ticket_id) AS tickets_handled
FROM agents a
JOIN tickets t ON a.agent_id = t.agent_id
WHERE t.csat_score IS NOT NULL
    AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY a.agent_id, a.agent_name, a.team
HAVING COUNT(t.ticket_id) >= 5
ORDER BY avg_csat DESC
LIMIT 10

-- COMMAND ----------

-- "How many critical tickets are open right now?"
SELECT 
    COUNT(*) AS critical_open_tickets,
    COUNT(CASE WHEN agent_id IS NULL THEN 1 END) AS unassigned
FROM tickets
WHERE priority = 'CRITICAL'
    AND status IN ('OPEN', 'IN_PROGRESS')

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ---
-- MAGIC *Quick Demo Notebook - Customer Support Tickets Analysis*
-- MAGIC 
-- MAGIC *Perfect for 5-minute demonstrations and executive presentations*
-- MAGIC 
-- MAGIC *Version: 1.0 | Date: January 2026*
