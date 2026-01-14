-- ============================================================================
-- Analysis Queries for GenAI Agent Demo
-- Useful queries for building the AI agent and dashboards
-- ============================================================================

-- ============================================================================
-- 1. EXECUTIVE DASHBOARD QUERIES
-- ============================================================================

-- Weekly Summary - "What's happening this week?"
CREATE OR REPLACE TEMP VIEW weekly_summary AS
SELECT 
    COUNT(*) AS total_tickets,
    COUNT(CASE WHEN status = 'OPEN' THEN 1 END) AS open_tickets,
    COUNT(CASE WHEN status = 'IN_PROGRESS' THEN 1 END) AS in_progress,
    COUNT(CASE WHEN status = 'CLOSED' THEN 1 END) AS closed_tickets,
    COUNT(CASE WHEN priority = 'CRITICAL' THEN 1 END) AS critical_tickets,
    COUNT(CASE WHEN priority = 'HIGH' THEN 1 END) AS high_priority,
    ROUND(AVG(CASE WHEN status IN ('RESOLVED', 'CLOSED') THEN resolution_time_hours END), 2) AS avg_resolution_hours,
    ROUND(AVG(first_response_time_minutes), 2) AS avg_first_response_minutes,
    SUM(CASE WHEN sla_breached = 'TRUE' THEN 1 ELSE 0 END) AS sla_breaches,
    ROUND(AVG(csat_score), 2) AS avg_csat,
    ROUND(AVG(nps_score), 1) AS avg_nps
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS;

SELECT * FROM weekly_summary;

-- ============================================================================
-- 2. TREND ANALYSIS - Main Issues and Categories
-- ============================================================================

-- Top 10 issues this week
SELECT 
    category,
    subcategory,
    COUNT(*) AS ticket_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage,
    ROUND(AVG(CASE WHEN status IN ('RESOLVED', 'CLOSED') THEN resolution_time_hours END), 2) AS avg_resolution_hours,
    SUM(CASE WHEN priority IN ('HIGH', 'CRITICAL') THEN 1 ELSE 0 END) AS urgent_count,
    ROUND(AVG(csat_score), 2) AS avg_csat
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY category, subcategory
ORDER BY ticket_count DESC
LIMIT 10;

-- Trend over time - last 8 weeks
SELECT 
    DATE_TRUNC('week', created_at) AS week,
    category,
    COUNT(*) AS ticket_count
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 56 DAYS
GROUP BY DATE_TRUNC('week', created_at), category
ORDER BY week DESC, ticket_count DESC;

-- ============================================================================
-- 3. CHURN RISK ANALYSIS
-- ============================================================================

-- Companies at high risk of churning
CREATE OR REPLACE TEMP VIEW churn_risk_companies AS
SELECT 
    c.company_id,
    c.company_name,
    c.cnpj,
    c.segment,
    c.company_size,
    c.churn_risk_score,
    c.monthly_transaction_volume,
    COUNT(t.ticket_id) AS total_tickets_30d,
    SUM(CASE WHEN t.priority IN ('HIGH', 'CRITICAL') THEN 1 ELSE 0 END) AS urgent_tickets,
    SUM(CASE WHEN t.category = 'COMPLAINT' THEN 1 ELSE 0 END) AS complaints,
    SUM(CASE WHEN t.sla_breached = 'TRUE' THEN 1 ELSE 0 END) AS sla_breaches,
    ROUND(AVG(t.csat_score), 2) AS avg_csat,
    ROUND(AVG(t.nps_score), 1) AS avg_nps,
    STRING_AGG(DISTINCT t.category, ', ') AS issue_categories,
    MAX(t.created_at) AS last_ticket_date
FROM companies c
LEFT JOIN tickets t ON c.company_id = t.company_id 
    AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
WHERE c.status = 'ACTIVE'
    AND c.churn_risk_score > 0.5
GROUP BY c.company_id, c.company_name, c.cnpj, c.segment, c.company_size, 
         c.churn_risk_score, c.monthly_transaction_volume
HAVING COUNT(t.ticket_id) >= 3 OR c.churn_risk_score > 0.7
ORDER BY c.churn_risk_score DESC, total_tickets_30d DESC;

SELECT * FROM churn_risk_companies LIMIT 20;

-- Churn risk with recommended actions
SELECT 
    company_name,
    churn_risk_score,
    total_tickets_30d,
    urgent_tickets,
    complaints,
    avg_csat,
    CASE 
        WHEN churn_risk_score > 0.8 AND complaints >= 2 THEN 'IMMEDIATE: Schedule executive call'
        WHEN churn_risk_score > 0.7 AND urgent_tickets >= 3 THEN 'URGENT: Escalate to account manager'
        WHEN churn_risk_score > 0.6 AND avg_csat < 3.0 THEN 'HIGH: Proactive outreach needed'
        WHEN sla_breaches >= 2 THEN 'MEDIUM: Review SLA compliance'
        ELSE 'Monitor closely'
    END AS recommended_action
FROM churn_risk_companies
ORDER BY churn_risk_score DESC;

-- ============================================================================
-- 4. SLA PERFORMANCE ANALYSIS
-- ============================================================================

-- SLA compliance by priority
SELECT 
    priority,
    COUNT(*) AS total_tickets,
    SUM(CASE WHEN sla_breached = 'TRUE' THEN 1 ELSE 0 END) AS sla_breached,
    SUM(CASE WHEN sla_breached = 'FALSE' THEN 1 ELSE 0 END) AS sla_met,
    ROUND(100.0 * SUM(CASE WHEN sla_breached = 'FALSE' THEN 1 ELSE 0 END) / COUNT(*), 2) AS sla_compliance_pct,
    ROUND(AVG(resolution_time_hours), 2) AS avg_resolution_hours,
    ROUND(MIN(resolution_time_hours), 2) AS min_resolution_hours,
    ROUND(MAX(resolution_time_hours), 2) AS max_resolution_hours,
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
    END;

-- Recent SLA breaches
SELECT 
    t.ticket_id,
    t.created_at,
    t.closed_at,
    t.priority,
    t.category,
    t.subject,
    t.resolution_time_hours,
    c.company_name,
    cu.customer_name,
    a.agent_name
FROM tickets t
JOIN companies c ON t.company_id = c.company_id
JOIN customers cu ON t.customer_id = cu.customer_id
LEFT JOIN agents a ON t.agent_id = a.agent_id
WHERE t.sla_breached = 'TRUE'
    AND t.created_at >= CURRENT_DATE - INTERVAL 7 DAYS
ORDER BY t.priority, t.created_at DESC;

-- ============================================================================
-- 5. AGENT PERFORMANCE ANALYSIS
-- ============================================================================

-- Agent performance metrics
SELECT 
    a.agent_id,
    a.agent_name,
    a.team,
    a.specialization,
    COUNT(t.ticket_id) AS tickets_handled_30d,
    COUNT(CASE WHEN t.status IN ('RESOLVED', 'CLOSED') THEN 1 END) AS tickets_resolved,
    ROUND(100.0 * COUNT(CASE WHEN t.status IN ('RESOLVED', 'CLOSED') THEN 1 END) / 
          NULLIF(COUNT(t.ticket_id), 0), 2) AS resolution_rate_pct,
    ROUND(AVG(t.resolution_time_hours), 2) AS avg_resolution_hours,
    ROUND(AVG(t.first_response_time_minutes), 2) AS avg_first_response_min,
    ROUND(AVG(t.csat_score), 2) AS avg_csat,
    ROUND(AVG(t.nps_score), 1) AS avg_nps,
    SUM(CASE WHEN t.sla_breached = 'TRUE' THEN 1 ELSE 0 END) AS sla_breaches,
    SUM(CASE WHEN t.escalated = 'TRUE' THEN 1 ELSE 0 END) AS escalations
FROM agents a
LEFT JOIN tickets t ON a.agent_id = t.agent_id
    AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
WHERE a.status = 'ACTIVE'
GROUP BY a.agent_id, a.agent_name, a.team, a.specialization
HAVING COUNT(t.ticket_id) > 0
ORDER BY tickets_handled_30d DESC;

-- Team performance comparison
SELECT 
    a.team,
    COUNT(DISTINCT a.agent_id) AS agent_count,
    COUNT(t.ticket_id) AS total_tickets,
    ROUND(AVG(t.resolution_time_hours), 2) AS avg_resolution_hours,
    ROUND(AVG(t.csat_score), 2) AS avg_csat,
    SUM(CASE WHEN t.sla_breached = 'TRUE' THEN 1 ELSE 0 END) AS sla_breaches,
    ROUND(100.0 * SUM(CASE WHEN t.sla_breached = 'FALSE' THEN 1 ELSE 0 END) / 
          COUNT(t.ticket_id), 2) AS sla_compliance_pct
FROM agents a
LEFT JOIN tickets t ON a.agent_id = t.agent_id
    AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
WHERE a.status = 'ACTIVE'
GROUP BY a.team
ORDER BY total_tickets DESC;

-- ============================================================================
-- 6. SENTIMENT AND SATISFACTION ANALYSIS
-- ============================================================================

-- Sentiment distribution over time
SELECT 
    DATE_TRUNC('week', created_at) AS week,
    sentiment,
    COUNT(*) AS ticket_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY DATE_TRUNC('week', created_at)), 2) AS percentage
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 90 DAYS
GROUP BY DATE_TRUNC('week', created_at), sentiment
ORDER BY week DESC, ticket_count DESC;

-- NPS distribution
SELECT 
    CASE 
        WHEN nps_score >= 9 THEN 'Promoter (9-10)'
        WHEN nps_score >= 7 THEN 'Passive (7-8)'
        WHEN nps_score >= 0 THEN 'Detractor (0-6)'
    END AS nps_category,
    COUNT(*) AS response_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage
FROM tickets
WHERE nps_score IS NOT NULL
    AND created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY 
    CASE 
        WHEN nps_score >= 9 THEN 'Promoter (9-10)'
        WHEN nps_score >= 7 THEN 'Passive (7-8)'
        WHEN nps_score >= 0 THEN 'Detractor (0-6)'
    END
ORDER BY 
    CASE 
        WHEN nps_score >= 9 THEN 1
        WHEN nps_score >= 7 THEN 2
        ELSE 3
    END;

-- CSAT by category
SELECT 
    category,
    COUNT(*) AS tickets_with_csat,
    ROUND(AVG(csat_score), 2) AS avg_csat,
    ROUND(MIN(csat_score), 2) AS min_csat,
    ROUND(MAX(csat_score), 2) AS max_csat,
    COUNT(CASE WHEN csat_score >= 4.0 THEN 1 END) AS satisfied_count,
    ROUND(100.0 * COUNT(CASE WHEN csat_score >= 4.0 THEN 1 END) / COUNT(*), 2) AS satisfaction_rate_pct
FROM tickets
WHERE csat_score IS NOT NULL
    AND created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY category
ORDER BY avg_csat DESC;

-- ============================================================================
-- 7. CHANNEL PERFORMANCE
-- ============================================================================

-- Ticket volume and performance by channel
SELECT 
    channel,
    COUNT(*) AS total_tickets,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage,
    ROUND(AVG(first_response_time_minutes), 2) AS avg_first_response_min,
    ROUND(AVG(resolution_time_hours), 2) AS avg_resolution_hours,
    ROUND(AVG(csat_score), 2) AS avg_csat,
    COUNT(CASE WHEN status IN ('RESOLVED', 'CLOSED') THEN 1 END) AS resolved_count
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY channel
ORDER BY total_tickets DESC;

-- ============================================================================
-- 8. TICKET CONVERSATION ANALYSIS
-- ============================================================================

-- Average interactions per ticket
SELECT 
    t.priority,
    t.category,
    COUNT(DISTINCT t.ticket_id) AS ticket_count,
    ROUND(AVG(interaction_count), 2) AS avg_interactions_per_ticket,
    ROUND(AVG(t.resolution_time_hours), 2) AS avg_resolution_hours
FROM tickets t
LEFT JOIN (
    SELECT ticket_id, COUNT(*) AS interaction_count
    FROM ticket_interactions
    GROUP BY ticket_id
) ti ON t.ticket_id = ti.ticket_id
WHERE t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY t.priority, t.category
ORDER BY avg_interactions_per_ticket DESC;

-- Tickets with most interactions (potential issues)
SELECT 
    t.ticket_id,
    t.subject,
    t.priority,
    t.category,
    t.status,
    COUNT(ti.interaction_id) AS interaction_count,
    c.company_name,
    t.created_at
FROM tickets t
JOIN ticket_interactions ti ON t.ticket_id = ti.ticket_id
JOIN companies c ON t.company_id = c.company_id
WHERE t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY t.ticket_id, t.subject, t.priority, t.category, t.status, c.company_name, t.created_at
HAVING COUNT(ti.interaction_id) >= 8
ORDER BY interaction_count DESC, t.priority;

-- ============================================================================
-- 9. BUSINESS SEGMENT ANALYSIS
-- ============================================================================

-- Ticket patterns by business segment
SELECT 
    c.segment,
    COUNT(DISTINCT c.company_id) AS company_count,
    COUNT(t.ticket_id) AS total_tickets,
    ROUND(AVG(tickets_per_company), 2) AS avg_tickets_per_company,
    STRING_AGG(DISTINCT t.category, ', ') AS main_categories,
    ROUND(AVG(t.csat_score), 2) AS avg_csat,
    SUM(CASE WHEN t.category = 'COMPLAINT' THEN 1 ELSE 0 END) AS complaint_count
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
ORDER BY total_tickets DESC;

-- ============================================================================
-- 10. REOPENED TICKETS ANALYSIS
-- ============================================================================

-- Tickets that were reopened (quality issues)
SELECT 
    t.ticket_id,
    t.subject,
    t.category,
    t.subcategory,
    t.reopened_count,
    a.agent_name,
    c.company_name,
    t.created_at,
    t.status
FROM tickets t
JOIN companies c ON t.company_id = c.company_id
LEFT JOIN agents a ON t.agent_id = a.agent_id
WHERE t.reopened_count > 0
    AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
ORDER BY t.reopened_count DESC, t.created_at DESC;

-- Categories with most reopened tickets
SELECT 
    category,
    subcategory,
    COUNT(*) AS total_tickets,
    SUM(reopened_count) AS total_reopens,
    ROUND(AVG(reopened_count), 2) AS avg_reopens,
    COUNT(CASE WHEN reopened_count > 0 THEN 1 END) AS tickets_with_reopens,
    ROUND(100.0 * COUNT(CASE WHEN reopened_count > 0 THEN 1 END) / COUNT(*), 2) AS reopen_rate_pct
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY category, subcategory
HAVING SUM(reopened_count) > 0
ORDER BY reopen_rate_pct DESC;

-- ============================================================================
-- 11. SIMILAR TICKETS FINDER (for Next Best Action)
-- ============================================================================

-- Find similar resolved tickets for a given ticket
-- Usage: Replace 'TKT000123' with actual ticket_id
CREATE OR REPLACE TEMP VIEW similar_tickets AS
WITH target_ticket AS (
    SELECT category, subcategory, priority, subject, description
    FROM tickets
    WHERE ticket_id = 'TKT000001'  -- Replace with target ticket
)
SELECT 
    t.ticket_id,
    t.subject,
    t.status,
    t.resolution_time_hours,
    t.csat_score,
    a.agent_name,
    -- Get the resolution from interactions
    (SELECT message 
     FROM ticket_interactions ti 
     WHERE ti.ticket_id = t.ticket_id 
         AND ti.author_type = 'AGENT' 
     ORDER BY ti.interaction_timestamp DESC 
     LIMIT 1) AS last_agent_response
FROM tickets t
CROSS JOIN target_ticket tt
LEFT JOIN agents a ON t.agent_id = a.agent_id
WHERE t.status IN ('RESOLVED', 'CLOSED')
    AND t.category = tt.category
    AND t.subcategory = tt.subcategory
    AND t.csat_score >= 4.0
ORDER BY t.csat_score DESC, t.resolution_time_hours ASC
LIMIT 5;

-- SELECT * FROM similar_tickets;
