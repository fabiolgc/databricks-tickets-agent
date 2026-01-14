-- ============================================================================
-- DDL for Customer Support Tickets Analysis - Payment Processing Company
-- Tables: companies, customers, agents, tickets, ticket_interactions
-- English Version
-- ============================================================================

-- Drop tables if they exist (for clean re-run)
DROP TABLE IF EXISTS ticket_interactions;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS agents;
DROP TABLE IF EXISTS companies;

-- ============================================================================
-- Table: companies
-- Description: Customer companies using payment processing services
-- ============================================================================
CREATE TABLE companies (
  company_id STRING NOT NULL COMMENT 'Unique identifier for the company',
  company_name STRING NOT NULL COMMENT 'Company legal name',
  tax_id STRING NOT NULL COMMENT 'Tax identification number - PII',
  segment STRING COMMENT 'Business segment (retail, restaurant, services, etc)',
  company_size STRING COMMENT 'Company size: SMALL, MEDIUM, LARGE, ENTERPRISE',
  contract_start_date DATE COMMENT 'Date when company started using the service',
  monthly_transaction_volume DECIMAL(15,2) COMMENT 'Average monthly transaction volume in USD',
  status STRING COMMENT 'Account status: ACTIVE, SUSPENDED, CANCELLED',
  churn_risk_score DECIMAL(3,2) COMMENT 'Churn risk score from 0.00 to 1.00',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record creation timestamp',
  CONSTRAINT pk_companies PRIMARY KEY (company_id)
)
USING DELTA
COMMENT 'Customer companies using payment processing services'
TBLPROPERTIES (
  'delta.minReaderVersion' = '1',
  'delta.minWriterVersion' = '2',
  'quality.check' = 'enabled',
  'pii.columns' = 'tax_id'
);

-- ============================================================================
-- Table: customers
-- Description: Individual users who open support tickets
-- ============================================================================
CREATE TABLE customers (
  customer_id STRING NOT NULL COMMENT 'Unique identifier for the customer',
  company_id STRING NOT NULL COMMENT 'Foreign key to companies table',
  customer_name STRING NOT NULL COMMENT 'Customer full name - PII',
  email STRING NOT NULL COMMENT 'Customer email address - PII',
  ssn STRING COMMENT 'Social Security Number - PII',
  birth_date DATE COMMENT 'Date of birth - PII',
  phone STRING COMMENT 'Phone number - PII',
  role STRING COMMENT 'Role in company: OWNER, MANAGER, OPERATOR, FINANCIAL',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record creation timestamp',
  CONSTRAINT pk_customers PRIMARY KEY (customer_id),
  CONSTRAINT fk_customers_company FOREIGN KEY (company_id) REFERENCES companies(company_id)
)
USING DELTA
COMMENT 'Individual customers who interact with support'
TBLPROPERTIES (
  'delta.minReaderVersion' = '1',
  'delta.minWriterVersion' = '2',
  'pii.columns' = 'customer_name,email,ssn,birth_date,phone'
);

-- ============================================================================
-- Table: agents
-- Description: Support agents who handle tickets
-- ============================================================================
CREATE TABLE agents (
  agent_id STRING NOT NULL COMMENT 'Unique identifier for the agent',
  agent_name STRING NOT NULL COMMENT 'Agent full name',
  email STRING NOT NULL COMMENT 'Agent email address',
  team STRING COMMENT 'Support team: L1_SUPPORT, L2_TECHNICAL, L3_SPECIALIST, FINANCIAL',
  specialization STRING COMMENT 'Agent specialization area',
  hire_date DATE COMMENT 'Agent hire date',
  avg_csat DECIMAL(3,2) COMMENT 'Average CSAT score (0-5)',
  tickets_resolved INT COMMENT 'Total tickets resolved',
  status STRING COMMENT 'Agent status: ACTIVE, INACTIVE, ON_LEAVE',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record creation timestamp',
  CONSTRAINT pk_agents PRIMARY KEY (agent_id)
)
USING DELTA
COMMENT 'Support agents handling customer tickets';

-- ============================================================================
-- Table: tickets
-- Description: Main tickets table with all ticket information
-- ============================================================================
CREATE TABLE tickets (
  ticket_id STRING NOT NULL COMMENT 'Unique ticket identifier',
  company_id STRING NOT NULL COMMENT 'Foreign key to companies table',
  customer_id STRING NOT NULL COMMENT 'Foreign key to customers table',
  agent_id STRING COMMENT 'Foreign key to agents table - assigned agent',
  created_at TIMESTAMP NOT NULL COMMENT 'Ticket creation timestamp',
  updated_at TIMESTAMP COMMENT 'Last update timestamp',
  closed_at TIMESTAMP COMMENT 'Ticket closure timestamp',
  status STRING NOT NULL COMMENT 'Ticket status: OPEN, IN_PROGRESS, PENDING_CUSTOMER, RESOLVED, CLOSED, CANCELLED',
  priority STRING NOT NULL COMMENT 'Priority level: LOW, MEDIUM, HIGH, CRITICAL',
  category STRING NOT NULL COMMENT 'Ticket category: TECHNICAL, FINANCIAL, COMMERCIAL, COMPLAINT, INFORMATION',
  subcategory STRING COMMENT 'Ticket subcategory for detailed classification',
  channel STRING NOT NULL COMMENT 'Contact channel: EMAIL, PHONE, CHAT, LIVE_CHAT, PORTAL',
  subject STRING NOT NULL COMMENT 'Ticket subject/title',
  description STRING NOT NULL COMMENT 'Detailed ticket description',
  tags ARRAY<STRING> COMMENT 'Tags for categorization and search',
  resolution_time_hours DECIMAL(10,2) COMMENT 'Time to resolve in hours',
  first_response_time_minutes INT COMMENT 'Time to first response in minutes',
  sla_breached BOOLEAN COMMENT 'Indicates if SLA was breached',
  nps_score INT COMMENT 'Net Promoter Score: 0-10 scale',
  csat_score DECIMAL(3,2) COMMENT 'Customer Satisfaction Score: 1.00 to 5.00',
  sentiment STRING COMMENT 'Sentiment analysis: POSITIVE, NEUTRAL, NEGATIVE, VERY_NEGATIVE',
  escalated BOOLEAN COMMENT 'Indicates if ticket was escalated',
  reopened_count INT DEFAULT 0 COMMENT 'Number of times ticket was reopened',
  related_ticket_ids ARRAY<STRING> COMMENT 'Related ticket IDs',
  CONSTRAINT pk_tickets PRIMARY KEY (ticket_id),
  CONSTRAINT fk_tickets_company FOREIGN KEY (company_id) REFERENCES companies(company_id),
  CONSTRAINT fk_tickets_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  CONSTRAINT fk_tickets_agent FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
)
USING DELTA
COMMENT 'Main customer support tickets table'
TBLPROPERTIES (
  'delta.minReaderVersion' = '1',
  'delta.minWriterVersion' = '2'
);

-- ============================================================================
-- Table: ticket_interactions
-- Description: Interaction history/dialogue for each ticket
-- ============================================================================
CREATE TABLE ticket_interactions (
  interaction_id STRING NOT NULL COMMENT 'Unique interaction identifier',
  ticket_id STRING NOT NULL COMMENT 'Foreign key to tickets table',
  interaction_timestamp TIMESTAMP NOT NULL COMMENT 'When the interaction occurred',
  author_type STRING NOT NULL COMMENT 'Who wrote: CUSTOMER, AGENT, SYSTEM',
  author_id STRING COMMENT 'ID of the author (customer_id or agent_id)',
  author_name STRING COMMENT 'Name of the author',
  message STRING NOT NULL COMMENT 'Interaction message content',
  interaction_type STRING COMMENT 'Type: COMMENT, STATUS_CHANGE, ESCALATION, INTERNAL_NOTE',
  channel STRING COMMENT 'Channel used for this interaction',
  attachments ARRAY<STRING> COMMENT 'List of attachment file names',
  CONSTRAINT pk_interactions PRIMARY KEY (interaction_id),
  CONSTRAINT fk_interactions_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
)
USING DELTA
COMMENT 'Ticket interaction history and dialogue'
TBLPROPERTIES (
  'delta.minReaderVersion' = '1',
  'delta.minWriterVersion' = '2'
);

-- ============================================================================
-- Create indexes for better query performance
-- ============================================================================
-- Note: Delta Lake supports data skipping and Z-ordering for optimization
-- Run after data load:
-- OPTIMIZE tickets ZORDER BY (created_at, status, priority, company_id);
-- OPTIMIZE ticket_interactions ZORDER BY (ticket_id, interaction_timestamp);
