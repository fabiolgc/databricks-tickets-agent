-- Databricks SQL Setup for Feature Store and AutoML
-- This script prepares the environment for churn prediction

-- ============================================================================
-- 1. CREATE CATALOG AND SCHEMA
-- ============================================================================

CREATE CATALOG IF NOT EXISTS main;
USE CATALOG main;

CREATE SCHEMA IF NOT EXISTS ticket_analytics
COMMENT 'Schema for ticket analytics and churn prediction';

USE SCHEMA ticket_analytics;

-- ============================================================================
-- 2. VERIFY REQUIRED TABLES EXIST
-- ============================================================================

-- Check if tables are loaded
SELECT 'companies' as table_name, COUNT(*) as row_count FROM companies
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'tickets', COUNT(*) FROM tickets
UNION ALL
SELECT 'ticket_interactions', COUNT(*) FROM ticket_interactions;

-- ============================================================================
-- 3. DATA QUALITY CHECKS
-- ============================================================================

-- Check for missing company_ids in tickets
SELECT 
    COUNT(*) as tickets_with_missing_company_id
FROM tickets
WHERE company_id IS NULL OR company_id = '';

-- Check for missing timestamps
SELECT 
    COUNT(*) as tickets_with_missing_created_at
FROM tickets
WHERE created_at IS NULL;

-- Check churn_risk_score distribution
SELECT 
    CASE 
        WHEN churn_risk_score < 0.3 THEN 'Low Risk (0-0.3)'
        WHEN churn_risk_score < 0.5 THEN 'Medium Risk (0.3-0.5)'
        WHEN churn_risk_score < 0.7 THEN 'High Risk (0.5-0.7)'
        ELSE 'Critical Risk (0.7-1.0)'
    END as risk_category,
    COUNT(*) as company_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM companies
GROUP BY risk_category
ORDER BY churn_risk_score;

-- ============================================================================
-- 4. PREVIEW KEY METRICS FOR FEATURE ENGINEERING
-- ============================================================================

-- Top companies by ticket volume
SELECT 
    c.company_id,
    c.company_name,
    c.segment,
    c.company_size,
    COUNT(t.ticket_id) as total_tickets,
    SUM(CASE WHEN t.status = 'OPEN' THEN 1 ELSE 0 END) as open_tickets,
    AVG(CAST(t.nps_score AS DOUBLE)) as avg_nps,
    AVG(CAST(t.csat_score AS DOUBLE)) as avg_csat,
    c.churn_risk_score
FROM companies c
LEFT JOIN tickets t ON c.company_id = t.company_id
GROUP BY c.company_id, c.company_name, c.segment, c.company_size, c.churn_risk_score
ORDER BY total_tickets DESC
LIMIT 20;

-- Companies with high churn risk
SELECT 
    c.company_id,
    c.company_name,
    c.segment,
    c.churn_risk_score,
    COUNT(t.ticket_id) as total_tickets,
    SUM(CASE WHEN t.category = 'COMPLAINT' THEN 1 ELSE 0 END) as complaints,
    SUM(CASE WHEN t.sla_breached = 'TRUE' THEN 1 ELSE 0 END) as sla_breaches,
    AVG(CAST(t.nps_score AS DOUBLE)) as avg_nps
FROM companies c
LEFT JOIN tickets t ON c.company_id = t.company_id
WHERE c.churn_risk_score > 0.7
GROUP BY c.company_id, c.company_name, c.segment, c.churn_risk_score
ORDER BY c.churn_risk_score DESC;

-- ============================================================================
-- 5. CREATE HELPER VIEWS
-- ============================================================================

-- View: Recent ticket activity (last 30 days)
CREATE OR REPLACE VIEW v_recent_ticket_activity AS
SELECT 
    company_id,
    COUNT(*) as tickets_last_30_days,
    SUM(CASE WHEN status = 'OPEN' THEN 1 ELSE 0 END) as open_last_30_days,
    SUM(CASE WHEN category = 'COMPLAINT' THEN 1 ELSE 0 END) as complaints_last_30_days,
    AVG(CAST(nps_score AS DOUBLE)) as avg_nps_last_30_days
FROM tickets
WHERE created_at >= CURRENT_DATE() - INTERVAL 30 DAYS
GROUP BY company_id;

-- View: Company satisfaction scores
CREATE OR REPLACE VIEW v_company_satisfaction AS
SELECT 
    company_id,
    AVG(CAST(nps_score AS DOUBLE)) as avg_nps,
    MIN(CAST(nps_score AS DOUBLE)) as min_nps,
    MAX(CAST(nps_score AS DOUBLE)) as max_nps,
    AVG(CAST(csat_score AS DOUBLE)) as avg_csat,
    MIN(CAST(csat_score AS DOUBLE)) as min_csat,
    MAX(CAST(csat_score AS DOUBLE)) as max_csat,
    COUNT(CASE WHEN nps_score IS NOT NULL THEN 1 END) as nps_response_count,
    COUNT(CASE WHEN csat_score IS NOT NULL THEN 1 END) as csat_response_count
FROM tickets
GROUP BY company_id;

-- View: Ticket resolution metrics
CREATE OR REPLACE VIEW v_ticket_resolution_metrics AS
SELECT 
    company_id,
    COUNT(*) as total_tickets,
    SUM(CASE WHEN status = 'CLOSED' THEN 1 ELSE 0 END) as closed_tickets,
    SUM(CASE WHEN status = 'CLOSED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as resolution_rate,
    AVG(CAST(resolution_time_hours AS DOUBLE)) as avg_resolution_hours,
    AVG(CAST(first_response_time_minutes AS DOUBLE)) as avg_first_response_minutes,
    SUM(CASE WHEN sla_breached = 'TRUE' THEN 1 ELSE 0 END) as sla_breaches,
    SUM(CASE WHEN sla_breached = 'TRUE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as sla_breach_rate
FROM tickets
GROUP BY company_id;

-- ============================================================================
-- 6. SAMPLE QUERY: Churn Risk Analysis
-- ============================================================================

-- Comprehensive churn risk analysis
CREATE OR REPLACE VIEW v_churn_risk_analysis AS
SELECT 
    c.company_id,
    c.company_name,
    c.segment,
    c.company_size,
    c.status,
    c.churn_risk_score,
    CASE 
        WHEN c.churn_risk_score > 0.7 THEN 'Critical'
        WHEN c.churn_risk_score > 0.5 THEN 'High'
        WHEN c.churn_risk_score > 0.3 THEN 'Medium'
        ELSE 'Low'
    END as risk_level,
    
    -- Ticket metrics
    trm.total_tickets,
    trm.resolution_rate,
    trm.sla_breach_rate,
    trm.avg_resolution_hours,
    
    -- Satisfaction metrics
    cs.avg_nps,
    cs.avg_csat,
    
    -- Recent activity
    rta.tickets_last_30_days,
    rta.complaints_last_30_days,
    
    -- Risk factors
    CASE WHEN cs.avg_nps < 5 THEN 1 ELSE 0 END as low_nps_flag,
    CASE WHEN cs.avg_csat < 3 THEN 1 ELSE 0 END as low_csat_flag,
    CASE WHEN trm.sla_breach_rate > 20 THEN 1 ELSE 0 END as high_sla_breach_flag,
    CASE WHEN rta.complaints_last_30_days > 5 THEN 1 ELSE 0 END as high_complaints_flag
    
FROM companies c
LEFT JOIN v_ticket_resolution_metrics trm ON c.company_id = trm.company_id
LEFT JOIN v_company_satisfaction cs ON c.company_id = cs.company_id
LEFT JOIN v_recent_ticket_activity rta ON c.company_id = rta.company_id;

-- Query the analysis
SELECT 
    risk_level,
    COUNT(*) as company_count,
    AVG(total_tickets) as avg_tickets,
    AVG(avg_nps) as avg_nps,
    AVG(sla_breach_rate) as avg_sla_breach_rate,
    SUM(low_nps_flag) as companies_with_low_nps,
    SUM(high_sla_breach_flag) as companies_with_high_sla_breach
FROM v_churn_risk_analysis
GROUP BY risk_level
ORDER BY 
    CASE risk_level
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
    END;

-- ============================================================================
-- 7. GRANT PERMISSIONS (if using Unity Catalog)
-- ============================================================================

-- Grant read access to ML engineers
-- GRANT SELECT ON SCHEMA ticket_analytics TO `ml_engineers`;
-- GRANT SELECT ON ALL TABLES IN SCHEMA ticket_analytics TO `ml_engineers`;

-- Grant write access for feature store
-- GRANT CREATE TABLE ON SCHEMA ticket_analytics TO `ml_engineers`;
-- GRANT MODIFY ON SCHEMA ticket_analytics TO `ml_engineers`;

-- ============================================================================
-- 8. VERIFY SETUP
-- ============================================================================

SELECT 
    'Setup Complete' as status,
    CURRENT_CATALOG() as catalog,
    CURRENT_SCHEMA() as schema,
    CURRENT_USER() as user,
    CURRENT_TIMESTAMP() as timestamp;

-- List all tables and views
SHOW TABLES IN ticket_analytics;

-- List all views
SHOW VIEWS IN ticket_analytics;
