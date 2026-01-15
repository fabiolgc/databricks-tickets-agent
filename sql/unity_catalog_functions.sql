-- ============================================================================
-- Unity Catalog Functions for Ticket Data Retrieval
-- Simplified functions - each receives only one ID parameter
-- ============================================================================

-- ============================================================================
-- Function: get_company_id_by_name
-- Description: Searches for company IDs by company name (supports partial matching)
-- ============================================================================
CREATE OR REPLACE FUNCTION get_company_id_by_name(
  company_name_param STRING COMMENT 'Company name or partial name to search for. Case-insensitive partial matching is supported (e.g., "Tech" will match "Tech Solutions Ltd"). Use this to find company_id when you only know the company name.'
)
RETURNS TABLE(
  company_id STRING,
  company_name STRING,
  segment STRING,
  company_size STRING,
  status STRING,
  churn_risk_score DECIMAL(3,2)
)
COMMENT 'Searches for companies by name using case-insensitive partial matching. Returns company basic info including ID, name, segment, size, status and churn risk score. Useful for finding company_id when you only know part of the company name. Example: searching "Restaurant" will find all companies with "Restaurant" in their name.'
RETURN
  SELECT
    company_id,
    company_name,
    segment,
    company_size,
    status,
    churn_risk_score
  FROM companies
  WHERE LOWER(company_name) LIKE CONCAT('%', LOWER(company_name_param), '%')
  ORDER BY company_name;


-- ============================================================================
-- Function: get_ticket_by_id
-- Description: Returns complete ticket information including company, customer, 
--              agent details and interaction statistics
-- ============================================================================
CREATE OR REPLACE FUNCTION get_ticket_by_id(
  ticket_id_param STRING COMMENT 'Ticket ID to retrieve complete information for (e.g., "TKT000001"). Returns all ticket details including status, priority, category, description, company info, customer info, assigned agent, and interaction statistics.'
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
COMMENT 'Returns comprehensive information for a specific ticket including all related entities (company, customer, agent) and interaction statistics. Use this to get the complete context of a single ticket for analysis, reporting, or AI processing.'
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
  
  WHERE t.ticket_id = ticket_id_param;


-- ============================================================================
-- Function: get_ticket_interactions
-- Description: Returns detailed interaction history for a specific ticket
-- ============================================================================
CREATE OR REPLACE FUNCTION get_ticket_interactions(
  ticket_id_param STRING COMMENT 'Ticket ID to retrieve interaction history for (e.g., "TKT000001"). Returns all messages/interactions for this ticket ordered chronologically, including author details, message content, and timestamps.'
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
COMMENT 'Returns the complete interaction/conversation history for a specific ticket. Each row is one message with timestamp, author info (customer/agent/system), message content, and channel. Results ordered chronologically. Use this to view the full communication thread, analyze response patterns, or feed conversations to AI models.'
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
  
  WHERE ti.ticket_id = ticket_id_param
  
  ORDER BY ti.interaction_timestamp;


-- ============================================================================
-- Function: get_ticket_full_conversation
-- Description: Returns complete ticket with all interactions as structured array
--              (optimized for AI/LLM processing)
-- ============================================================================
CREATE OR REPLACE FUNCTION get_ticket_full_conversation(
  ticket_id_param STRING COMMENT 'Ticket ID to retrieve full conversation for (e.g., "TKT000001"). Returns a single row with ticket details and all interactions aggregated into a structured array, ideal for AI/LLM processing, summarization, or sentiment analysis.'
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
  company_id STRING,
  company_name STRING,
  company_segment STRING,
  company_size STRING,
  -- Customer Information
  customer_id STRING,
  customer_name STRING,
  customer_email STRING,
  customer_role STRING,
  -- Agent Information
  agent_id STRING,
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
COMMENT 'Returns a single row with complete ticket information and all interactions as a structured array. Perfect for AI/LLM processing as it provides the entire ticket context in one denormalized record. Use for conversation analysis, sentiment detection, summarization, or feeding to language models for next-best-action recommendations.'
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
    co.company_id,
    co.company_name,
    co.segment AS company_segment,
    co.company_size,
    
    -- Customer Information
    cu.customer_id,
    cu.customer_name,
    cu.email AS customer_email,
    cu.role AS customer_role,
    
    -- Agent Information
    a.agent_id,
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
-- Function: get_company_info
-- Description: Returns complete company information with ticket statistics,
--              customer counts, and risk indicators
-- ============================================================================
CREATE OR REPLACE FUNCTION get_company_info(
  company_id_param STRING COMMENT 'Company ID to retrieve complete information for (e.g., "COMP00001"). Returns comprehensive company profile including ticket statistics, customer counts, performance metrics (CSAT, NPS), risk indicators, and last activity date.'
)
RETURNS TABLE(
  -- Company Information
  company_id STRING,
  company_name STRING,
  cnpj STRING,
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
COMMENT 'Returns the most comprehensive view of a company including profile info, customer counts (total and active), ticket statistics (all-time and last 30 days), performance metrics (resolution time, CSAT, NPS), sentiment distribution, boolean risk indicators (high churn risk, recent complaints, SLA violations, critical open tickets), and days since last activity. Primary function for company health assessment, account management, and identifying intervention needs.'
RETURN
  SELECT
    -- Company Information
    c.company_id,
    c.company_name,
    c.cnpj,
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
  
  WHERE c.company_id = company_id_param;


-- ============================================================================
-- Function: get_company_tickets_summary
-- Description: Returns aggregated ticket statistics for a company
-- ============================================================================
CREATE OR REPLACE FUNCTION get_company_tickets_summary(
  company_id_param STRING COMMENT 'Company ID to retrieve ticket summary for (e.g., "COMP00001"). Returns aggregated statistics including ticket counts by status, priority distribution, SLA metrics, average resolution times, and satisfaction scores.'
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
  first_ticket_date TIMESTAMP,
  last_ticket_date TIMESTAMP
)
COMMENT 'Returns comprehensive aggregated statistics for a company including ticket counts by status (open, in progress, resolved, closed), priority distribution (critical, high), SLA breach count, escalation count, average resolution and response times, satisfaction scores (CSAT, NPS), total interactions, and date range of tickets. Use for company health checks, executive reporting, account reviews, and performance analysis.'
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
    MIN(t.created_at) AS first_ticket_date,
    MAX(t.created_at) AS last_ticket_date
    
  FROM companies co
  LEFT JOIN tickets t ON co.company_id = t.company_id
  LEFT JOIN (
    SELECT ticket_id, COUNT(*) AS interaction_count
    FROM ticket_interactions
    GROUP BY ticket_id
  ) int_count ON t.ticket_id = int_count.ticket_id
  
  WHERE co.company_id = company_id_param
  GROUP BY co.company_id, co.company_name, co.segment, co.company_size;


-- ============================================================================
-- Function: get_customer_info
-- Description: Returns complete customer information with ticket history
-- ============================================================================
CREATE OR REPLACE FUNCTION get_customer_info(
  customer_id_param STRING COMMENT 'Customer ID to retrieve information for (e.g., "CUST00001"). Returns customer profile, company affiliation, and ticket activity statistics including total tickets, open tickets, satisfaction scores, and last contact date.'
)
RETURNS TABLE(
  -- Customer Information
  customer_id STRING,
  customer_name STRING,
  email STRING,
  cpf STRING,
  birth_date DATE,
  phone STRING,
  role STRING,
  customer_created_at TIMESTAMP,
  -- Company Information
  company_id STRING,
  company_name STRING,
  company_segment STRING,
  company_size STRING,
  -- Ticket Statistics
  total_tickets INT,
  open_tickets INT,
  closed_tickets INT,
  avg_csat_score DECIMAL(3,2),
  avg_nps_score DECIMAL(5,2),
  last_ticket_date TIMESTAMP,
  days_since_last_ticket INT
)
COMMENT 'Returns complete customer profile including personal information (name, email, phone, role), company affiliation, and ticket activity summary (total tickets, open/closed counts, satisfaction scores, last contact date). Use for customer support context, account history review, or identifying inactive customers.'
RETURN
  SELECT
    -- Customer Information
    cu.customer_id,
    cu.customer_name,
    cu.email,
    cu.cpf,
    cu.birth_date,
    cu.phone,
    cu.role,
    cu.created_at AS customer_created_at,
    
    -- Company Information
    co.company_id,
    co.company_name,
    co.segment AS company_segment,
    co.company_size,
    
    -- Ticket Statistics
    COALESCE(ticket_stats.total_tickets, 0) AS total_tickets,
    COALESCE(ticket_stats.open_tickets, 0) AS open_tickets,
    COALESCE(ticket_stats.closed_tickets, 0) AS closed_tickets,
    ticket_stats.avg_csat_score,
    ticket_stats.avg_nps_score,
    ticket_stats.last_ticket_date,
    CASE 
      WHEN ticket_stats.last_ticket_date IS NOT NULL 
      THEN DATEDIFF(CURRENT_DATE(), CAST(ticket_stats.last_ticket_date AS DATE))
      ELSE NULL 
    END AS days_since_last_ticket
    
  FROM customers cu
  INNER JOIN companies co ON cu.company_id = co.company_id
  LEFT JOIN (
    SELECT
      customer_id,
      COUNT(*) AS total_tickets,
      SUM(CASE WHEN status = 'OPEN' THEN 1 ELSE 0 END) AS open_tickets,
      SUM(CASE WHEN status = 'CLOSED' THEN 1 ELSE 0 END) AS closed_tickets,
      AVG(csat_score) AS avg_csat_score,
      AVG(nps_score) AS avg_nps_score,
      MAX(created_at) AS last_ticket_date
    FROM tickets
    GROUP BY customer_id
  ) ticket_stats ON cu.customer_id = ticket_stats.customer_id
  
  WHERE cu.customer_id = customer_id_param;


-- ============================================================================
-- Function: get_agent_info
-- Description: Returns complete agent information with performance metrics
-- ============================================================================
CREATE OR REPLACE FUNCTION get_agent_info(
  agent_id_param STRING COMMENT 'Agent ID to retrieve information for (e.g., "AGENT001"). Returns agent profile, performance metrics, workload statistics, and specialized expertise areas. Use for agent performance review, workload balancing, or ticket assignment decisions.'
)
RETURNS TABLE(
  -- Agent Information
  agent_id STRING,
  agent_name STRING,
  email STRING,
  team STRING,
  specialization STRING,
  hire_date DATE,
  agent_created_at TIMESTAMP,
  -- Performance Metrics
  avg_csat DECIMAL(3,2),
  tickets_resolved INT,
  current_open_tickets INT,
  avg_resolution_time_hours DECIMAL(10,2),
  avg_first_response_minutes DECIMAL(10,2),
  -- Recent Activity (Last 30 Days)
  tickets_last_30d INT,
  resolved_last_30d INT,
  avg_csat_last_30d DECIMAL(3,2),
  sla_breached_last_30d INT
)
COMMENT 'Returns comprehensive agent information including profile (name, team, specialization), performance metrics (average CSAT, tickets resolved, resolution times), current workload (open tickets), and recent activity statistics (last 30 days). Essential for agent performance evaluation, workload management, and intelligent ticket routing.'
RETURN
  SELECT
    -- Agent Information
    a.agent_id,
    a.agent_name,
    a.email,
    a.team,
    a.specialization,
    a.hire_date,
    a.created_at AS agent_created_at,
    
    -- Performance Metrics (All Time)
    a.avg_csat,
    a.tickets_resolved,
    COALESCE(current_tickets.open_count, 0) AS current_open_tickets,
    all_tickets.avg_resolution_time_hours,
    all_tickets.avg_first_response_minutes,
    
    -- Recent Activity (Last 30 Days)
    COALESCE(recent_tickets.tickets_30d, 0) AS tickets_last_30d,
    COALESCE(recent_tickets.resolved_30d, 0) AS resolved_last_30d,
    recent_tickets.avg_csat_30d AS avg_csat_last_30d,
    COALESCE(recent_tickets.sla_breached_30d, 0) AS sla_breached_last_30d
    
  FROM agents a
  
  -- Current Open Tickets
  LEFT JOIN (
    SELECT
      agent_id,
      COUNT(*) AS open_count
    FROM tickets
    WHERE status IN ('OPEN', 'IN_PROGRESS')
    GROUP BY agent_id
  ) current_tickets ON a.agent_id = current_tickets.agent_id
  
  -- All Time Statistics
  LEFT JOIN (
    SELECT
      agent_id,
      AVG(resolution_time_hours) AS avg_resolution_time_hours,
      AVG(first_response_time_minutes) AS avg_first_response_minutes
    FROM tickets
    WHERE agent_id IS NOT NULL
    GROUP BY agent_id
  ) all_tickets ON a.agent_id = all_tickets.agent_id
  
  -- Last 30 Days Statistics
  LEFT JOIN (
    SELECT
      agent_id,
      COUNT(*) AS tickets_30d,
      SUM(CASE WHEN status IN ('RESOLVED', 'CLOSED') THEN 1 ELSE 0 END) AS resolved_30d,
      AVG(csat_score) AS avg_csat_30d,
      SUM(CASE WHEN sla_breached = TRUE THEN 1 ELSE 0 END) AS sla_breached_30d
    FROM tickets
    WHERE created_at >= CURRENT_TIMESTAMP() - INTERVAL 30 DAYS
      AND agent_id IS NOT NULL
    GROUP BY agent_id
  ) recent_tickets ON a.agent_id = recent_tickets.agent_id
  
  WHERE a.agent_id = agent_id_param;


-- ============================================================================
-- Example Usage
-- ============================================================================

-- Example 1: Search for company by name
-- SELECT * FROM get_company_id_by_name('Tech');
-- SELECT * FROM get_company_id_by_name('Restaurant');

-- Example 2: Get complete ticket information
-- SELECT * FROM get_ticket_by_id('TKT000001');

-- Example 3: Get ticket conversation history
-- SELECT * FROM get_ticket_interactions('TKT000001');

-- Example 4: Get ticket with full conversation for AI processing
-- SELECT * FROM get_ticket_full_conversation('TKT000001');

-- Example 5: Get complete company information
-- SELECT * FROM get_company_info('COMP00001');

-- Example 6: Get company ticket statistics summary
-- SELECT * FROM get_company_tickets_summary('COMP00001');

-- Example 7: Get customer information and ticket history
-- SELECT * FROM get_customer_info('CUST00001');

-- Example 8: Get agent information and performance metrics
-- SELECT * FROM get_agent_info('AGENT001');

-- Example 9: Search company by name and get its summary
-- WITH company_lookup AS (
--   SELECT company_id FROM get_company_id_by_name('Restaurant') LIMIT 1
-- )
-- SELECT * FROM get_company_tickets_summary(
--   (SELECT company_id FROM company_lookup)
-- );
