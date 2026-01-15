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
