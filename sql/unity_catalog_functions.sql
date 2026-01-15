-- ============================================================================
-- Unity Catalog Functions for Ticket Data Retrieval
-- Functions to query comprehensive ticket information with related entities
-- ============================================================================

-- ============================================================================
-- Function: get_ticket_complete_data
-- Description: Returns complete ticket information including company, customer, 
--              agent details and aggregated interaction statistics
-- Parameters: 
--   - ticket_id_param: Optional ticket ID filter (NULL returns all tickets)
--   - company_id_param: Optional company ID filter (NULL returns all companies)
--   - status_param: Optional status filter (NULL returns all statuses)
--   - date_from: Optional start date filter (NULL = no start date limit)
--   - date_to: Optional end date filter (NULL = no end date limit)
-- Returns: Table with comprehensive ticket data
-- ============================================================================
CREATE OR REPLACE FUNCTION get_ticket_complete_data(
  ticket_id_param STRING,
  company_id_param STRING,
  status_param STRING,
  date_from TIMESTAMP,
  date_to TIMESTAMP
)
RETURNS TABLE(
  -- Ticket Information
  ticket_id STRING,
  ticket_status STRING,
  ticket_priority STRING,
  ticket_category STRING,
  ticket_subcategory STRING,
  ticket_channel STRING,
  ticket_subject STRING,
  ticket_description STRING,
  ticket_tags ARRAY<STRING>,
  ticket_created_at TIMESTAMP,
  ticket_updated_at TIMESTAMP,
  ticket_closed_at TIMESTAMP,
  resolution_time_hours DECIMAL(10,2),
  first_response_time_minutes INT,
  sla_breached BOOLEAN,
  escalated BOOLEAN,
  reopened_count INT,
  nps_score INT,
  csat_score DECIMAL(3,2),
  sentiment STRING,
  -- Company Information
  company_id STRING,
  company_name STRING,
  company_segment STRING,
  company_size STRING,
  company_status STRING,
  company_contract_start_date DATE,
  monthly_transaction_volume DECIMAL(15,2),
  churn_risk_score DECIMAL(3,2),
  -- Customer Information
  customer_id STRING,
  customer_name STRING,
  customer_email STRING,
  customer_role STRING,
  customer_phone STRING,
  -- Agent Information
  agent_id STRING,
  agent_name STRING,
  agent_email STRING,
  agent_team STRING,
  agent_specialization STRING,
  agent_avg_csat DECIMAL(3,2),
  agent_tickets_resolved INT,
  -- Interaction Statistics
  total_interactions INT,
  customer_interactions_count INT,
  agent_interactions_count INT,
  system_interactions_count INT,
  last_interaction_timestamp TIMESTAMP,
  last_interaction_author STRING
)
COMMENT 'Returns comprehensive ticket data with company, customer, agent and interaction statistics'
RETURN
  SELECT
    -- Ticket Information
    t.ticket_id,
    t.status AS ticket_status,
    t.priority AS ticket_priority,
    t.category AS ticket_category,
    t.subcategory AS ticket_subcategory,
    t.channel AS ticket_channel,
    t.subject AS ticket_subject,
    t.description AS ticket_description,
    t.tags AS ticket_tags,
    t.created_at AS ticket_created_at,
    t.updated_at AS ticket_updated_at,
    t.closed_at AS ticket_closed_at,
    t.resolution_time_hours,
    t.first_response_time_minutes,
    t.sla_breached,
    t.escalated,
    t.reopened_count,
    t.nps_score,
    t.csat_score,
    t.sentiment,
    
    -- Company Information
    co.company_id,
    co.company_name,
    co.segment AS company_segment,
    co.company_size,
    co.status AS company_status,
    co.contract_start_date AS company_contract_start_date,
    co.monthly_transaction_volume,
    co.churn_risk_score,
    
    -- Customer Information
    cu.customer_id,
    cu.customer_name,
    cu.email AS customer_email,
    cu.role AS customer_role,
    cu.phone AS customer_phone,
    
    -- Agent Information
    a.agent_id,
    a.agent_name,
    a.email AS agent_email,
    a.team AS agent_team,
    a.specialization AS agent_specialization,
    a.avg_csat AS agent_avg_csat,
    a.tickets_resolved AS agent_tickets_resolved,
    
    -- Interaction Statistics
    COALESCE(int_stats.total_interactions, 0) AS total_interactions,
    COALESCE(int_stats.customer_interactions, 0) AS customer_interactions_count,
    COALESCE(int_stats.agent_interactions, 0) AS agent_interactions_count,
    COALESCE(int_stats.system_interactions, 0) AS system_interactions_count,
    int_stats.last_interaction_timestamp,
    int_stats.last_interaction_author
    
  FROM tickets t
  INNER JOIN companies co ON t.company_id = co.company_id
  INNER JOIN customers cu ON t.customer_id = cu.customer_id
  LEFT JOIN agents a ON t.agent_id = a.agent_id
  LEFT JOIN (
    SELECT 
      ticket_id,
      COUNT(*) AS total_interactions,
      SUM(CASE WHEN author_type = 'CUSTOMER' THEN 1 ELSE 0 END) AS customer_interactions,
      SUM(CASE WHEN author_type = 'AGENT' THEN 1 ELSE 0 END) AS agent_interactions,
      SUM(CASE WHEN author_type = 'SYSTEM' THEN 1 ELSE 0 END) AS system_interactions,
      MAX(interaction_timestamp) AS last_interaction_timestamp,
      FIRST_VALUE(author_name) OVER (PARTITION BY ticket_id ORDER BY interaction_timestamp DESC) AS last_interaction_author
    FROM ticket_interactions
    GROUP BY ticket_id, author_name, interaction_timestamp
  ) int_stats ON t.ticket_id = int_stats.ticket_id
  
  WHERE 
    (ticket_id_param IS NULL OR t.ticket_id = ticket_id_param)
    AND (company_id_param IS NULL OR t.company_id = company_id_param)
    AND (status_param IS NULL OR t.status = status_param)
    AND (date_from IS NULL OR t.created_at >= date_from)
    AND (date_to IS NULL OR t.created_at <= date_to);


-- ============================================================================
-- Function: get_ticket_interactions
-- Description: Returns detailed interaction history for tickets
-- Parameters:
--   - ticket_id_param: Optional ticket ID filter (NULL returns all tickets)
--   - company_id_param: Optional company ID filter (NULL returns all companies)
--   - author_type_param: Optional author type filter (CUSTOMER, AGENT, SYSTEM)
-- Returns: Table with detailed ticket interactions
-- ============================================================================
CREATE OR REPLACE FUNCTION get_ticket_interactions(
  ticket_id_param STRING,
  company_id_param STRING,
  author_type_param STRING
)
RETURNS TABLE(
  -- Ticket Basic Info
  ticket_id STRING,
  ticket_subject STRING,
  ticket_status STRING,
  ticket_priority STRING,
  ticket_category STRING,
  -- Company Info
  company_id STRING,
  company_name STRING,
  -- Interaction Details
  interaction_id STRING,
  interaction_timestamp TIMESTAMP,
  author_type STRING,
  author_id STRING,
  author_name STRING,
  message STRING,
  interaction_type STRING,
  channel STRING,
  attachments ARRAY<STRING>
)
COMMENT 'Returns detailed interaction history for tickets with company and ticket context'
RETURN
  SELECT
    -- Ticket Basic Info
    t.ticket_id,
    t.subject AS ticket_subject,
    t.status AS ticket_status,
    t.priority AS ticket_priority,
    t.category AS ticket_category,
    
    -- Company Info
    co.company_id,
    co.company_name,
    
    -- Interaction Details
    ti.interaction_id,
    ti.interaction_timestamp,
    ti.author_type,
    ti.author_id,
    ti.author_name,
    ti.message,
    ti.interaction_type,
    ti.channel,
    ti.attachments
    
  FROM ticket_interactions ti
  INNER JOIN tickets t ON ti.ticket_id = t.ticket_id
  INNER JOIN companies co ON t.company_id = co.company_id
  
  WHERE
    (ticket_id_param IS NULL OR ti.ticket_id = ticket_id_param)
    AND (company_id_param IS NULL OR t.company_id = company_id_param)
    AND (author_type_param IS NULL OR ti.author_type = author_type_param)
  
  ORDER BY ti.interaction_timestamp;


-- ============================================================================
-- Function: get_ticket_full_conversation
-- Description: Returns complete ticket data with all interactions in a 
--              single denormalized view (useful for AI/LLM processing)
-- Parameters:
--   - ticket_id_param: Specific ticket ID (REQUIRED)
-- Returns: Single row with ticket info and all interactions as array
-- ============================================================================
CREATE OR REPLACE FUNCTION get_ticket_full_conversation(
  ticket_id_param STRING
)
RETURNS TABLE(
  -- Ticket Information
  ticket_id STRING,
  ticket_subject STRING,
  ticket_description STRING,
  ticket_status STRING,
  ticket_priority STRING,
  ticket_category STRING,
  ticket_subcategory STRING,
  ticket_created_at TIMESTAMP,
  ticket_closed_at TIMESTAMP,
  resolution_time_hours DECIMAL(10,2),
  sla_breached BOOLEAN,
  sentiment STRING,
  csat_score DECIMAL(3,2),
  -- Company Information
  company_name STRING,
  company_segment STRING,
  company_size STRING,
  -- Customer Information
  customer_name STRING,
  customer_email STRING,
  customer_role STRING,
  -- Agent Information
  agent_name STRING,
  agent_team STRING,
  agent_specialization STRING,
  -- Full Conversation
  total_interactions INT,
  interactions ARRAY<STRUCT<
    timestamp: TIMESTAMP,
    author_type: STRING,
    author_name: STRING,
    message: STRING,
    interaction_type: STRING
  >>
)
COMMENT 'Returns complete ticket with full conversation history as structured array'
RETURN
  SELECT
    -- Ticket Information
    t.ticket_id,
    t.subject AS ticket_subject,
    t.description AS ticket_description,
    t.status AS ticket_status,
    t.priority AS ticket_priority,
    t.category AS ticket_category,
    t.subcategory AS ticket_subcategory,
    t.created_at AS ticket_created_at,
    t.closed_at AS ticket_closed_at,
    t.resolution_time_hours,
    t.sla_breached,
    t.sentiment,
    t.csat_score,
    
    -- Company Information
    co.company_name,
    co.segment AS company_segment,
    co.company_size,
    
    -- Customer Information
    cu.customer_name,
    cu.email AS customer_email,
    cu.role AS customer_role,
    
    -- Agent Information
    a.agent_name,
    a.team AS agent_team,
    a.specialization AS agent_specialization,
    
    -- Full Conversation
    COALESCE(int_agg.total_interactions, 0) AS total_interactions,
    int_agg.interactions
    
  FROM tickets t
  INNER JOIN companies co ON t.company_id = co.company_id
  INNER JOIN customers cu ON t.customer_id = cu.customer_id
  LEFT JOIN agents a ON t.agent_id = a.agent_id
  LEFT JOIN (
    SELECT 
      ticket_id,
      COUNT(*) AS total_interactions,
      COLLECT_LIST(
        STRUCT(
          interaction_timestamp AS timestamp,
          author_type,
          author_name,
          message,
          interaction_type
        )
      ) AS interactions
    FROM ticket_interactions
    GROUP BY ticket_id
  ) int_agg ON t.ticket_id = int_agg.ticket_id
  
  WHERE t.ticket_id = ticket_id_param;


-- ============================================================================
-- Function: get_company_tickets_summary
-- Description: Returns aggregated ticket statistics for a company
-- Parameters:
--   - company_id_param: Company ID (REQUIRED)
--   - date_from: Optional start date filter
--   - date_to: Optional end date filter
-- Returns: Table with company ticket statistics
-- ============================================================================
CREATE OR REPLACE FUNCTION get_company_tickets_summary(
  company_id_param STRING,
  date_from TIMESTAMP,
  date_to TIMESTAMP
)
RETURNS TABLE(
  company_id STRING,
  company_name STRING,
  company_segment STRING,
  company_size STRING,
  total_tickets INT,
  open_tickets INT,
  in_progress_tickets INT,
  resolved_tickets INT,
  closed_tickets INT,
  cancelled_tickets INT,
  critical_priority_tickets INT,
  high_priority_tickets INT,
  sla_breached_tickets INT,
  escalated_tickets INT,
  avg_resolution_time_hours DECIMAL(10,2),
  avg_first_response_time_minutes DECIMAL(10,2),
  avg_csat_score DECIMAL(3,2),
  avg_nps_score DECIMAL(5,2),
  total_interactions INT,
  period_start TIMESTAMP,
  period_end TIMESTAMP
)
COMMENT 'Returns aggregated ticket statistics and KPIs for a specific company'
RETURN
  SELECT
    co.company_id,
    co.company_name,
    co.segment AS company_segment,
    co.company_size,
    COUNT(DISTINCT t.ticket_id) AS total_tickets,
    SUM(CASE WHEN t.status = 'OPEN' THEN 1 ELSE 0 END) AS open_tickets,
    SUM(CASE WHEN t.status = 'IN_PROGRESS' THEN 1 ELSE 0 END) AS in_progress_tickets,
    SUM(CASE WHEN t.status = 'RESOLVED' THEN 1 ELSE 0 END) AS resolved_tickets,
    SUM(CASE WHEN t.status = 'CLOSED' THEN 1 ELSE 0 END) AS closed_tickets,
    SUM(CASE WHEN t.status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled_tickets,
    SUM(CASE WHEN t.priority = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_priority_tickets,
    SUM(CASE WHEN t.priority = 'HIGH' THEN 1 ELSE 0 END) AS high_priority_tickets,
    SUM(CASE WHEN t.sla_breached = TRUE THEN 1 ELSE 0 END) AS sla_breached_tickets,
    SUM(CASE WHEN t.escalated = TRUE THEN 1 ELSE 0 END) AS escalated_tickets,
    AVG(t.resolution_time_hours) AS avg_resolution_time_hours,
    AVG(t.first_response_time_minutes) AS avg_first_response_time_minutes,
    AVG(t.csat_score) AS avg_csat_score,
    AVG(t.nps_score) AS avg_nps_score,
    COALESCE(SUM(int_count.interaction_count), 0) AS total_interactions,
    COALESCE(MIN(t.created_at), date_from) AS period_start,
    COALESCE(MAX(t.created_at), date_to) AS period_end
    
  FROM companies co
  LEFT JOIN tickets t ON co.company_id = t.company_id
    AND (date_from IS NULL OR t.created_at >= date_from)
    AND (date_to IS NULL OR t.created_at <= date_to)
  LEFT JOIN (
    SELECT ticket_id, COUNT(*) AS interaction_count
    FROM ticket_interactions
    GROUP BY ticket_id
  ) int_count ON t.ticket_id = int_count.ticket_id
  
  WHERE co.company_id = company_id_param
  GROUP BY co.company_id, co.company_name, co.segment, co.company_size;


-- ============================================================================
-- Function: get_company_complete_data
-- Description: Returns complete company information with ticket statistics,
--              customer counts, and risk indicators
-- Parameters:
--   - company_id_param: Optional company ID filter (NULL returns all companies)
--   - segment_param: Optional segment filter (NULL returns all segments)
--   - min_churn_risk: Optional minimum churn risk score filter (NULL = no filter)
--   - status_param: Optional company status filter (NULL returns all statuses)
-- Returns: Table with comprehensive company data and KPIs
-- ============================================================================
CREATE OR REPLACE FUNCTION get_company_complete_data(
  company_id_param STRING,
  segment_param STRING,
  min_churn_risk DECIMAL(3,2),
  status_param STRING
)
RETURNS TABLE(
  -- Company Information
  company_id STRING,
  company_name STRING,
  tax_id STRING,
  segment STRING,
  company_size STRING,
  contract_start_date DATE,
  monthly_transaction_volume DECIMAL(15,2),
  status STRING,
  churn_risk_score DECIMAL(3,2),
  company_created_at TIMESTAMP,
  -- Customer Counts
  total_customers INT,
  active_customers_30d INT,
  -- Ticket Statistics (All Time)
  total_tickets_all_time INT,
  open_tickets INT,
  in_progress_tickets INT,
  pending_customer_tickets INT,
  resolved_tickets INT,
  closed_tickets INT,
  -- Ticket Statistics (Last 30 Days)
  tickets_last_30d INT,
  critical_tickets_30d INT,
  high_priority_tickets_30d INT,
  sla_breached_tickets_30d INT,
  escalated_tickets_30d INT,
  complaints_30d INT,
  -- Performance Metrics (Last 30 Days)
  avg_resolution_time_hours DECIMAL(10,2),
  avg_first_response_minutes DECIMAL(10,2),
  avg_csat_score DECIMAL(3,2),
  avg_nps_score DECIMAL(5,2),
  -- Sentiment Analysis
  positive_sentiment_count INT,
  neutral_sentiment_count INT,
  negative_sentiment_count INT,
  very_negative_sentiment_count INT,
  -- Risk Indicators
  is_high_churn_risk BOOLEAN,
  has_recent_complaints BOOLEAN,
  has_sla_violations BOOLEAN,
  has_critical_open_tickets BOOLEAN,
  -- Last Activity
  last_ticket_date TIMESTAMP,
  days_since_last_ticket INT
)
COMMENT 'Returns comprehensive company data with ticket statistics, KPIs and risk indicators'
RETURN
  SELECT
    -- Company Information
    c.company_id,
    c.company_name,
    c.tax_id,
    c.segment,
    c.company_size,
    c.contract_start_date,
    c.monthly_transaction_volume,
    c.status,
    c.churn_risk_score,
    c.created_at AS company_created_at,
    
    -- Customer Counts
    COALESCE(cust_stats.total_customers, 0) AS total_customers,
    COALESCE(cust_stats.active_customers_30d, 0) AS active_customers_30d,
    
    -- Ticket Statistics (All Time)
    COALESCE(ticket_all.total_tickets, 0) AS total_tickets_all_time,
    COALESCE(ticket_all.open_tickets, 0) AS open_tickets,
    COALESCE(ticket_all.in_progress_tickets, 0) AS in_progress_tickets,
    COALESCE(ticket_all.pending_customer_tickets, 0) AS pending_customer_tickets,
    COALESCE(ticket_all.resolved_tickets, 0) AS resolved_tickets,
    COALESCE(ticket_all.closed_tickets, 0) AS closed_tickets,
    
    -- Ticket Statistics (Last 30 Days)
    COALESCE(ticket_30d.tickets_30d, 0) AS tickets_last_30d,
    COALESCE(ticket_30d.critical_tickets, 0) AS critical_tickets_30d,
    COALESCE(ticket_30d.high_priority_tickets, 0) AS high_priority_tickets_30d,
    COALESCE(ticket_30d.sla_breached_tickets, 0) AS sla_breached_tickets_30d,
    COALESCE(ticket_30d.escalated_tickets, 0) AS escalated_tickets_30d,
    COALESCE(ticket_30d.complaints, 0) AS complaints_30d,
    
    -- Performance Metrics (Last 30 Days)
    ticket_30d.avg_resolution_time_hours,
    ticket_30d.avg_first_response_minutes,
    ticket_30d.avg_csat_score,
    ticket_30d.avg_nps_score,
    
    -- Sentiment Analysis
    COALESCE(sentiment.positive_count, 0) AS positive_sentiment_count,
    COALESCE(sentiment.neutral_count, 0) AS neutral_sentiment_count,
    COALESCE(sentiment.negative_count, 0) AS negative_sentiment_count,
    COALESCE(sentiment.very_negative_count, 0) AS very_negative_sentiment_count,
    
    -- Risk Indicators
    (c.churn_risk_score > 0.7) AS is_high_churn_risk,
    (COALESCE(ticket_30d.complaints, 0) >= 2) AS has_recent_complaints,
    (COALESCE(ticket_30d.sla_breached_tickets, 0) > 0) AS has_sla_violations,
    (COALESCE(ticket_all.open_tickets, 0) > 0 AND COALESCE(ticket_30d.critical_tickets, 0) > 0) AS has_critical_open_tickets,
    
    -- Last Activity
    ticket_all.last_ticket_date,
    CASE 
      WHEN ticket_all.last_ticket_date IS NOT NULL 
      THEN DATEDIFF(CURRENT_DATE(), CAST(ticket_all.last_ticket_date AS DATE))
      ELSE NULL 
    END AS days_since_last_ticket
    
  FROM companies c
  
  -- Customer Statistics
  LEFT JOIN (
    SELECT 
      company_id,
      COUNT(DISTINCT customer_id) AS total_customers,
      COUNT(DISTINCT CASE 
        WHEN customer_id IN (
          SELECT DISTINCT customer_id 
          FROM tickets 
          WHERE created_at >= CURRENT_TIMESTAMP() - INTERVAL 30 DAYS
        ) 
        THEN customer_id 
      END) AS active_customers_30d
    FROM customers
    GROUP BY company_id
  ) cust_stats ON c.company_id = cust_stats.company_id
  
  -- All Time Ticket Statistics
  LEFT JOIN (
    SELECT
      company_id,
      COUNT(*) AS total_tickets,
      SUM(CASE WHEN status = 'OPEN' THEN 1 ELSE 0 END) AS open_tickets,
      SUM(CASE WHEN status = 'IN_PROGRESS' THEN 1 ELSE 0 END) AS in_progress_tickets,
      SUM(CASE WHEN status = 'PENDING_CUSTOMER' THEN 1 ELSE 0 END) AS pending_customer_tickets,
      SUM(CASE WHEN status = 'RESOLVED' THEN 1 ELSE 0 END) AS resolved_tickets,
      SUM(CASE WHEN status = 'CLOSED' THEN 1 ELSE 0 END) AS closed_tickets,
      MAX(created_at) AS last_ticket_date
    FROM tickets
    GROUP BY company_id
  ) ticket_all ON c.company_id = ticket_all.company_id
  
  -- Last 30 Days Ticket Statistics
  LEFT JOIN (
    SELECT
      company_id,
      COUNT(*) AS tickets_30d,
      SUM(CASE WHEN priority = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_tickets,
      SUM(CASE WHEN priority = 'HIGH' THEN 1 ELSE 0 END) AS high_priority_tickets,
      SUM(CASE WHEN sla_breached = TRUE THEN 1 ELSE 0 END) AS sla_breached_tickets,
      SUM(CASE WHEN escalated = TRUE THEN 1 ELSE 0 END) AS escalated_tickets,
      SUM(CASE WHEN category = 'COMPLAINT' THEN 1 ELSE 0 END) AS complaints,
      AVG(resolution_time_hours) AS avg_resolution_time_hours,
      AVG(first_response_time_minutes) AS avg_first_response_minutes,
      AVG(csat_score) AS avg_csat_score,
      AVG(nps_score) AS avg_nps_score
    FROM tickets
    WHERE created_at >= CURRENT_TIMESTAMP() - INTERVAL 30 DAYS
    GROUP BY company_id
  ) ticket_30d ON c.company_id = ticket_30d.company_id
  
  -- Sentiment Analysis (Last 30 Days)
  LEFT JOIN (
    SELECT
      company_id,
      SUM(CASE WHEN sentiment = 'POSITIVE' THEN 1 ELSE 0 END) AS positive_count,
      SUM(CASE WHEN sentiment = 'NEUTRAL' THEN 1 ELSE 0 END) AS neutral_count,
      SUM(CASE WHEN sentiment = 'NEGATIVE' THEN 1 ELSE 0 END) AS negative_count,
      SUM(CASE WHEN sentiment = 'VERY_NEGATIVE' THEN 1 ELSE 0 END) AS very_negative_count
    FROM tickets
    WHERE created_at >= CURRENT_TIMESTAMP() - INTERVAL 30 DAYS
    GROUP BY company_id
  ) sentiment ON c.company_id = sentiment.company_id
  
  WHERE
    (company_id_param IS NULL OR c.company_id = company_id_param)
    AND (segment_param IS NULL OR c.segment = segment_param)
    AND (min_churn_risk IS NULL OR c.churn_risk_score >= min_churn_risk)
    AND (status_param IS NULL OR c.status = status_param);


-- ============================================================================
-- Function: get_companies_at_churn_risk
-- Description: Returns companies at risk of churning with detailed analysis
-- Parameters:
--   - min_churn_risk: Minimum churn risk score (default 0.6)
--   - min_tickets: Minimum number of recent tickets to consider (default 1)
--   - days_back: Number of days to look back for ticket analysis (default 30)
-- Returns: Table with at-risk companies and recommended actions
-- ============================================================================
CREATE OR REPLACE FUNCTION get_companies_at_churn_risk(
  min_churn_risk DECIMAL(3,2),
  min_tickets INT,
  days_back INT
)
RETURNS TABLE(
  company_id STRING,
  company_name STRING,
  segment STRING,
  company_size STRING,
  churn_risk_score DECIMAL(3,2),
  monthly_transaction_volume DECIMAL(15,2),
  risk_level STRING,
  recent_tickets INT,
  critical_tickets INT,
  complaints INT,
  sla_violations INT,
  avg_csat DECIMAL(3,2),
  avg_nps DECIMAL(5,2),
  negative_sentiment_pct DECIMAL(5,2),
  days_since_last_ticket INT,
  recommended_action STRING,
  action_priority INT
)
COMMENT 'Returns companies at churn risk with analysis and recommended actions'
RETURN
  WITH company_stats AS (
    SELECT
      c.company_id,
      c.company_name,
      c.segment,
      c.company_size,
      c.churn_risk_score,
      c.monthly_transaction_volume,
      COUNT(t.ticket_id) AS recent_tickets,
      SUM(CASE WHEN t.priority = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_tickets,
      SUM(CASE WHEN t.category = 'COMPLAINT' THEN 1 ELSE 0 END) AS complaints,
      SUM(CASE WHEN t.sla_breached = TRUE THEN 1 ELSE 0 END) AS sla_violations,
      AVG(t.csat_score) AS avg_csat,
      AVG(t.nps_score) AS avg_nps,
      SUM(CASE WHEN t.sentiment IN ('NEGATIVE', 'VERY_NEGATIVE') THEN 1 ELSE 0 END) AS negative_sentiment_count,
      MAX(t.created_at) AS last_ticket_date
    FROM companies c
    LEFT JOIN tickets t ON c.company_id = t.company_id
      AND t.created_at >= CURRENT_TIMESTAMP() - INTERVAL days_back DAYS
    WHERE c.churn_risk_score >= min_churn_risk
      AND c.status = 'ACTIVE'
    GROUP BY c.company_id, c.company_name, c.segment, c.company_size, 
             c.churn_risk_score, c.monthly_transaction_volume
    HAVING COUNT(t.ticket_id) >= min_tickets OR c.churn_risk_score >= 0.8
  )
  SELECT
    company_id,
    company_name,
    segment,
    company_size,
    churn_risk_score,
    monthly_transaction_volume,
    
    -- Risk Level Classification
    CASE
      WHEN churn_risk_score >= 0.9 THEN 'CRITICAL'
      WHEN churn_risk_score >= 0.8 THEN 'VERY_HIGH'
      WHEN churn_risk_score >= 0.7 THEN 'HIGH'
      ELSE 'MEDIUM'
    END AS risk_level,
    
    recent_tickets,
    critical_tickets,
    complaints,
    sla_violations,
    ROUND(avg_csat, 2) AS avg_csat,
    ROUND(avg_nps, 2) AS avg_nps,
    
    -- Negative Sentiment Percentage
    CASE 
      WHEN recent_tickets > 0 
      THEN ROUND((negative_sentiment_count * 100.0) / recent_tickets, 2)
      ELSE 0
    END AS negative_sentiment_pct,
    
    DATEDIFF(CURRENT_DATE(), CAST(last_ticket_date AS DATE)) AS days_since_last_ticket,
    
    -- Recommended Action
    CASE
      WHEN churn_risk_score >= 0.9 AND complaints >= 3 
        THEN 'IMMEDIATE: Executive escalation - Schedule C-level meeting within 24h'
      WHEN churn_risk_score >= 0.85 AND critical_tickets >= 2 
        THEN 'URGENT: Senior account manager call today - Resolve critical issues'
      WHEN churn_risk_score >= 0.8 AND sla_violations >= 3 
        THEN 'HIGH: Review SLA compliance - Offer compensation and service improvement plan'
      WHEN churn_risk_score >= 0.75 AND avg_csat < 2.5 
        THEN 'HIGH: Customer satisfaction intervention - Dedicated support team assignment'
      WHEN churn_risk_score >= 0.7 AND complaints >= 2 
        THEN 'MEDIUM: Proactive outreach - Address complaints and gather feedback'
      WHEN churn_risk_score >= 0.65 
        THEN 'MEDIUM: Account review - Schedule check-in call this week'
      ELSE 'LOW: Monitor closely - Continue regular touchpoints'
    END AS recommended_action,
    
    -- Action Priority (1-5, 1 being highest)
    CASE
      WHEN churn_risk_score >= 0.9 AND complaints >= 3 THEN 1
      WHEN churn_risk_score >= 0.85 AND critical_tickets >= 2 THEN 1
      WHEN churn_risk_score >= 0.8 AND sla_violations >= 3 THEN 2
      WHEN churn_risk_score >= 0.75 AND avg_csat < 2.5 THEN 2
      WHEN churn_risk_score >= 0.7 AND complaints >= 2 THEN 3
      WHEN churn_risk_score >= 0.65 THEN 3
      ELSE 4
    END AS action_priority
    
  ORDER BY action_priority, churn_risk_score DESC, recent_tickets DESC;


-- ============================================================================
-- Example Usage / Tests
-- ============================================================================

-- Example 1: Get all complete ticket data
-- SELECT * FROM get_ticket_complete_data(NULL, NULL, NULL, NULL, NULL);

-- Example 2: Get specific ticket
-- SELECT * FROM get_ticket_complete_data('TKT-001', NULL, NULL, NULL, NULL);

-- Example 3: Get all open tickets for a company
-- SELECT * FROM get_ticket_complete_data(NULL, 'COMP-001', 'OPEN', NULL, NULL);

-- Example 4: Get tickets created in last 30 days
-- SELECT * FROM get_ticket_complete_data(
--   NULL, NULL, NULL, 
--   CURRENT_TIMESTAMP() - INTERVAL 30 DAYS, 
--   CURRENT_TIMESTAMP()
-- );

-- Example 5: Get all interactions for a ticket
-- SELECT * FROM get_ticket_interactions('TKT-001', NULL, NULL);

-- Example 6: Get only customer interactions for a company
-- SELECT * FROM get_ticket_interactions(NULL, 'COMP-001', 'CUSTOMER');

-- Example 7: Get full conversation for a ticket (useful for AI processing)
-- SELECT * FROM get_ticket_full_conversation('TKT-001');

-- Example 8: Get company ticket summary
-- SELECT * FROM get_company_tickets_summary('COMP-001', NULL, NULL);

-- Example 9: Get company summary for last quarter
-- SELECT * FROM get_company_tickets_summary(
--   'COMP-001',
--   CURRENT_TIMESTAMP() - INTERVAL 90 DAYS,
--   CURRENT_TIMESTAMP()
-- );

-- Example 10: Get complete company data for all companies
-- SELECT * FROM get_company_complete_data(NULL, NULL, NULL, NULL);

-- Example 11: Get specific company complete data
-- SELECT * FROM get_company_complete_data('COMP00001', NULL, NULL, NULL);

-- Example 12: Get all RETAIL companies with high churn risk
-- SELECT * FROM get_company_complete_data(NULL, 'RETAIL', 0.7, 'ACTIVE');

-- Example 13: Get all companies at churn risk (default: risk >= 0.6)
-- SELECT * FROM get_companies_at_churn_risk(0.6, 1, 30);

-- Example 14: Get critical churn risk companies (risk >= 0.8, last 15 days)
-- SELECT * FROM get_companies_at_churn_risk(0.8, 2, 15);

-- Example 15: Get companies needing immediate action
-- SELECT 
--   company_name,
--   churn_risk_score,
--   recommended_action,
--   recent_tickets,
--   complaints,
--   avg_csat
-- FROM get_companies_at_churn_risk(0.7, 1, 30)
-- WHERE action_priority <= 2
-- ORDER BY action_priority, churn_risk_score DESC;

-- Example 16: Combine company data with churn analysis
-- SELECT 
--   c.company_name,
--   c.segment,
--   c.churn_risk_score,
--   c.total_tickets_all_time,
--   c.tickets_last_30d,
--   c.critical_tickets_30d,
--   c.sla_breached_tickets_30d,
--   c.avg_csat_score,
--   c.has_critical_open_tickets,
--   c.days_since_last_ticket
-- FROM get_company_complete_data(NULL, NULL, 0.7, 'ACTIVE') c
-- WHERE c.is_high_churn_risk = TRUE
-- ORDER BY c.churn_risk_score DESC, c.tickets_last_30d DESC;

-- Example 17: Find companies with no recent activity (potential issue)
-- SELECT 
--   company_name,
--   segment,
--   churn_risk_score,
--   days_since_last_ticket,
--   total_tickets_all_time,
--   monthly_transaction_volume
-- FROM get_company_complete_data(NULL, NULL, NULL, 'ACTIVE')
-- WHERE days_since_last_ticket > 60
--   AND total_tickets_all_time > 0
-- ORDER BY days_since_last_ticket DESC;
