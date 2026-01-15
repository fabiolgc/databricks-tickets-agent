# Databricks notebook source
# MAGIC %md
# MAGIC # AI Agent Implementation - Support Tickets Analysis
# MAGIC 
# MAGIC This notebook demonstrates how to implement an AI-powered agent for ticket analysis.
# MAGIC 
# MAGIC ## Features:
# MAGIC - Natural language queries to SQL
# MAGIC - Intelligent summaries and insights
# MAGIC - Churn risk analysis
# MAGIC - Next best action recommendations
# MAGIC - Integration with Databricks AI Functions
# MAGIC 
# MAGIC ## Requirements:
# MAGIC - Databricks Runtime with ML
# MAGIC - Tables created and loaded (companies, customers, agents, tickets, ticket_interactions)
# MAGIC - OpenAI API key or Databricks Foundation Models access

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Setup and Configuration

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.window import Window
from datetime import datetime, timedelta
import json

# Configuration
SCHEMA_NAME = "default"  # Change to your schema
CATALOG_NAME = "hive_metastore"  # Change if using Unity Catalog

# AI Model Configuration
# Option 1: Use Databricks Foundation Models
USE_DATABRICKS_AI = True

# Option 2: Use OpenAI (if USE_DATABRICKS_AI = False)
OPENAI_API_KEY = "your-api-key-here"  # Set your OpenAI key

print("✓ Configuration loaded")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. System Prompt Definition

# COMMAND ----------

SYSTEM_PROMPT = """You are an AI Agent specialized in Support Ticket Analysis for a payment processing company.

## Your Role
Assist managers and analysts in understanding patterns, identifying risks, and recommending actions.

## Business Context
- Company: Payment processor (POS terminals, mobile payments)
- Key Metrics: SLA, CSAT, NPS, Churn Risk

## Capabilities
1. Executive Analysis - Generate summaries and KPIs
2. Problem Identification - Categorize and prioritize issues
3. Churn Management - Identify at-risk customers
4. Team Performance - Evaluate agents
5. Recommendations - Suggest next best actions

## Domain Knowledge
- CRITICAL tickets: 4h SLA
- HIGH tickets: 8h SLA
- MEDIUM tickets: 24h SLA
- LOW tickets: 48h SLA
- Churn risk > 0.7: High risk
- CSAT >= 4.0: Satisfied
- NPS 9-10: Promoters, 0-6: Detractors

## Response Format
- Use markdown structure
- Include metrics and insights
- Provide actionable recommendations
- Use emojis for clarity (⚠️ 📊 ✅ 🔴)

## Available Tables
- companies: Customer companies with churn_risk_score
- customers: Individual users
- agents: Support team with performance metrics
- tickets: Complete ticket history with SLA, CSAT, NPS, sentiment
- ticket_interactions: Full conversation history
"""

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. AI Query Function

# COMMAND ----------

def query_ai_agent(user_question, context_data=None, use_databricks=True):
    """
    Query the AI agent with a question and optional context data
    
    Args:
        user_question: User's natural language question
        context_data: Optional dict with additional context (metrics, data)
        use_databricks: Use Databricks AI Functions vs external API
    
    Returns:
        AI-generated response
    """
    
    # Build context from data if provided
    context_text = ""
    if context_data:
        context_text = "\n\n## Context Data:\n"
        for key, value in context_data.items():
            context_text += f"- {key}: {value}\n"
    
    # Full prompt
    full_prompt = f"""{SYSTEM_PROMPT}

## User Question:
{user_question}
{context_text}

## Your Response:
"""
    
    if use_databricks:
        # Use Databricks AI Functions
        # Note: This requires Databricks Runtime with AI Functions enabled
        try:
            response = spark.sql(f"""
                SELECT ai_query(
                    'databricks-meta-llama-3-1-70b-instruct',
                    '{full_prompt.replace("'", "''")}'
                ) as response
            """).collect()[0]['response']
            
            return response
        except Exception as e:
            return f"Error using Databricks AI: {str(e)}\nPlease configure AI Functions or use OpenAI instead."
    else:
        # Use OpenAI API
        import openai
        openai.api_key = OPENAI_API_KEY
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{user_question}{context_text}"}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Helper Functions - Data Retrieval

# COMMAND ----------

def get_weekly_summary():
    """Get weekly ticket summary metrics"""
    summary = spark.sql(f"""
        SELECT 
            COUNT(*) as total_tickets,
            COUNT(CASE WHEN status = 'OPEN' THEN 1 END) as open_tickets,
            COUNT(CASE WHEN status = 'CLOSED' THEN 1 END) as closed_tickets,
            COUNT(CASE WHEN priority = 'CRITICAL' THEN 1 END) as critical_tickets,
            ROUND(AVG(CASE WHEN status IN ('RESOLVED', 'CLOSED') THEN resolution_time_hours END), 2) as avg_resolution_hours,
            SUM(CASE WHEN sla_breached = TRUE THEN 1 ELSE 0 END) as sla_breaches,
            ROUND(AVG(csat_score), 2) as avg_csat,
            ROUND(AVG(nps_score), 1) as avg_nps
        FROM {CATALOG_NAME}.{SCHEMA_NAME}.tickets
        WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS
    """).collect()[0]
    
    return summary.asDict()

def get_top_issues(limit=5):
    """Get top issues by volume"""
    issues = spark.sql(f"""
        SELECT 
            category,
            subcategory,
            COUNT(*) as count,
            ROUND(AVG(CASE WHEN status IN ('RESOLVED', 'CLOSED') THEN resolution_time_hours END), 2) as avg_hours
        FROM {CATALOG_NAME}.{SCHEMA_NAME}.tickets
        WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS
        GROUP BY category, subcategory
        ORDER BY count DESC
        LIMIT {limit}
    """).collect()
    
    return [issue.asDict() for issue in issues]

def get_churn_risk_companies(min_risk=0.7, limit=10):
    """Get companies at high churn risk"""
    companies = spark.sql(f"""
        SELECT 
            c.company_name,
            c.churn_risk_score,
            COUNT(t.ticket_id) as recent_tickets,
            SUM(CASE WHEN t.priority IN ('HIGH', 'CRITICAL') THEN 1 ELSE 0 END) as urgent_tickets,
            SUM(CASE WHEN t.category = 'COMPLAINT' THEN 1 ELSE 0 END) as complaints,
            ROUND(AVG(t.csat_score), 2) as avg_csat
        FROM {CATALOG_NAME}.{SCHEMA_NAME}.companies c
        LEFT JOIN {CATALOG_NAME}.{SCHEMA_NAME}.tickets t 
            ON c.company_id = t.company_id 
            AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
        WHERE c.churn_risk_score > {min_risk}
            AND c.status = 'ACTIVE'
        GROUP BY c.company_id, c.company_name, c.churn_risk_score
        ORDER BY c.churn_risk_score DESC, recent_tickets DESC
        LIMIT {limit}
    """).collect()
    
    return [company.asDict() for company in companies]

def get_agent_performance():
    """Get agent performance metrics"""
    agents = spark.sql(f"""
        SELECT 
            a.agent_name,
            a.team,
            COUNT(t.ticket_id) as tickets_handled,
            ROUND(AVG(t.resolution_time_hours), 2) as avg_resolution_hours,
            ROUND(AVG(t.csat_score), 2) as avg_csat,
            SUM(CASE WHEN t.sla_breached = TRUE THEN 1 ELSE 0 END) as sla_breaches
        FROM {CATALOG_NAME}.{SCHEMA_NAME}.agents a
        LEFT JOIN {CATALOG_NAME}.{SCHEMA_NAME}.tickets t 
            ON a.agent_id = t.agent_id
            AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
        WHERE a.status = 'ACTIVE'
        GROUP BY a.agent_id, a.agent_name, a.team
        HAVING COUNT(t.ticket_id) > 0
        ORDER BY tickets_handled DESC
    """).collect()
    
    return [agent.asDict() for agent in agents]

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Example Queries

# COMMAND ----------

# MAGIC %md
# MAGIC ### Example 1: Weekly Executive Summary

# COMMAND ----------

# Get data
weekly_data = get_weekly_summary()
top_issues_data = get_top_issues(5)

# Prepare context
context = {
    "Total Tickets": weekly_data['total_tickets'],
    "Open Tickets": weekly_data['open_tickets'],
    "Critical Tickets": weekly_data['critical_tickets'],
    "SLA Breaches": weekly_data['sla_breaches'],
    "Average CSAT": weekly_data['avg_csat'],
    "Average NPS": weekly_data['avg_nps'],
    "Top Issues": str(top_issues_data)
}

# Query AI
question = "Generate an executive summary of last week's tickets with actionable insights."
response = query_ai_agent(question, context, use_databricks=USE_DATABRICKS_AI)

print(response)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Example 2: Churn Risk Analysis

# COMMAND ----------

# Get churn risk data
churn_data = get_churn_risk_companies(min_risk=0.7, limit=10)

context = {
    "High Risk Companies Count": len(churn_data),
    "Companies Data": str(churn_data[:3])  # Show top 3 as example
}

question = """
Analyze the top companies at churn risk. 
For each, explain why they're at risk and recommend specific retention actions.
Prioritize by urgency.
"""

response = query_ai_agent(question, context, use_databricks=USE_DATABRICKS_AI)
print(response)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Example 3: Team Performance Analysis

# COMMAND ----------

# Get agent performance
agent_data = get_agent_performance()

context = {
    "Agent Count": len(agent_data),
    "Performance Data": str(agent_data[:5])  # Top 5 agents
}

question = """
Analyze team performance. Identify:
1. Best performing agents
2. Agents needing support
3. Training needs
4. Workload distribution issues
"""

response = query_ai_agent(question, context, use_databricks=USE_DATABRICKS_AI)
print(response)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Example 4: Problem Trend Analysis

# COMMAND ----------

# Get trend data
trend_data = spark.sql(f"""
    SELECT 
        DATE_TRUNC('day', created_at) as date,
        category,
        COUNT(*) as count
    FROM {CATALOG_NAME}.{SCHEMA_NAME}.tickets
    WHERE created_at >= CURRENT_DATE - INTERVAL 14 DAYS
    GROUP BY DATE_TRUNC('day', created_at), category
    ORDER BY date DESC, count DESC
""").collect()

context = {
    "Trend Data (Last 14 days)": str([t.asDict() for t in trend_data[:20]])
}

question = """
Analyze ticket trends over the last 2 weeks.
Identify:
1. Growing problems
2. Declining issues
3. Emerging patterns
4. Recommended preventive actions
"""

response = query_ai_agent(question, context, use_databricks=USE_DATABRICKS_AI)
print(response)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Interactive Chat Interface

# COMMAND ----------

def chat_with_agent(question, include_data=True):
    """
    Interactive chat function
    
    Args:
        question: User's question
        include_data: Whether to automatically include relevant data
    """
    print(f"\n{'='*70}")
    print(f"❓ Question: {question}")
    print(f"{'='*70}\n")
    
    context = {}
    
    if include_data:
        # Auto-detect what data to include based on question keywords
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['week', 'summary', 'overview', 'kpi']):
            context['Weekly Summary'] = get_weekly_summary()
        
        if any(word in question_lower for word in ['churn', 'risk', 'leave', 'cancel']):
            context['Churn Risk Companies'] = get_churn_risk_companies()[:5]
        
        if any(word in question_lower for word in ['agent', 'team', 'performance']):
            context['Agent Performance'] = get_agent_performance()[:10]
        
        if any(word in question_lower for word in ['problem', 'issue', 'top']):
            context['Top Issues'] = get_top_issues(10)
    
    # Query AI
    response = query_ai_agent(question, context, use_databricks=USE_DATABRICKS_AI)
    
    print(f"🤖 Agent Response:\n")
    print(response)
    print(f"\n{'='*70}\n")
    
    return response

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Example Usage

# COMMAND ----------

# Example 1: Simple question
chat_with_agent("What are the most critical issues I should address today?")

# COMMAND ----------

# Example 2: Churn analysis
chat_with_agent("Which customers should I call today to prevent churn?")

# COMMAND ----------

# Example 3: Performance question
chat_with_agent("How is my support team performing this month?")

# COMMAND ----------

# Example 4: Complex analysis
chat_with_agent("""
Compare this week's performance with last week. 
Identify what's getting better, what's getting worse, 
and provide 3 specific action recommendations.
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Next Best Action Recommendation

# COMMAND ----------

def recommend_next_action(ticket_id):
    """
    Recommend next best action for a specific ticket
    based on similar resolved tickets
    """
    # Get ticket details
    ticket = spark.sql(f"""
        SELECT *
        FROM {CATALOG_NAME}.{SCHEMA_NAME}.tickets
        WHERE ticket_id = '{ticket_id}'
    """).collect()[0]
    
    # Find similar resolved tickets
    similar = spark.sql(f"""
        SELECT 
            ticket_id,
            subject,
            resolution_time_hours,
            csat_score,
            agent_id
        FROM {CATALOG_NAME}.{SCHEMA_NAME}.tickets
        WHERE status IN ('RESOLVED', 'CLOSED')
            AND category = '{ticket.category}'
            AND subcategory = '{ticket.subcategory}'
            AND csat_score >= 4.0
        ORDER BY csat_score DESC, resolution_time_hours ASC
        LIMIT 5
    """).collect()
    
    # Get agent info for similar tickets
    similar_data = []
    for t in similar:
        agent = spark.sql(f"""
            SELECT agent_name, team, specialization
            FROM {CATALOG_NAME}.{SCHEMA_NAME}.agents
            WHERE agent_id = '{t.agent_id}'
        """).collect()[0] if t.agent_id else None
        
        similar_data.append({
            'ticket_id': t.ticket_id,
            'subject': t.subject,
            'resolution_hours': t.resolution_time_hours,
            'csat': t.csat_score,
            'agent': agent.agent_name if agent else 'N/A'
        })
    
    context = {
        "Current Ticket": {
            'id': ticket.ticket_id,
            'category': ticket.category,
            'subcategory': ticket.subcategory,
            'priority': ticket.priority,
            'subject': ticket.subject
        },
        "Similar Resolved Tickets": similar_data
    }
    
    question = f"""
    I have ticket {ticket_id} about "{ticket.subject}".
    Based on similar successfully resolved tickets, recommend:
    1. Best approach to solve it
    2. Estimated resolution time
    3. Most suitable agent
    4. Key steps to follow
    """
    
    return chat_with_agent(question, include_data=False)

# COMMAND ----------

# Example: Get recommendation for a specific ticket
# Replace with actual ticket_id from your data
recommend_next_action('TKT000001')

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Automated Daily Report

# COMMAND ----------

def generate_daily_report():
    """
    Generate automated daily report for management
    """
    # Gather all relevant data
    weekly_summary = get_weekly_summary()
    top_issues = get_top_issues(5)
    churn_risk = get_churn_risk_companies(0.7, 5)
    agent_perf = get_agent_performance()[:5]
    
    # Get critical open tickets
    critical_tickets = spark.sql(f"""
        SELECT ticket_id, subject, company_id, created_at
        FROM {CATALOG_NAME}.{SCHEMA_NAME}.tickets
        WHERE status IN ('OPEN', 'IN_PROGRESS')
            AND priority = 'CRITICAL'
        ORDER BY created_at ASC
    """).collect()
    
    context = {
        "Weekly Metrics": weekly_summary,
        "Top 5 Issues": top_issues,
        "Top 5 Churn Risk Companies": churn_risk,
        "Top 5 Agents": agent_perf,
        "Critical Open Tickets": len(critical_tickets),
        "Critical Tickets Details": [t.asDict() for t in critical_tickets]
    }
    
    question = """
    Generate a comprehensive daily management report including:
    
    1. Executive Summary (key numbers)
    2. Critical Alerts (urgent items requiring immediate action)
    3. Top Problems (what's happening)
    4. Churn Risk (customers at risk)
    5. Team Performance (quick overview)
    6. Top 3 Priority Actions for today
    
    Make it concise, actionable, and easy to scan quickly.
    """
    
    return chat_with_agent(question, include_data=False)

# COMMAND ----------

# Generate daily report
daily_report = generate_daily_report()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Save Agent Responses

# COMMAND ----------

def save_agent_response(question, response, metadata=None):
    """
    Save agent interactions for audit and improvement
    """
    from datetime import datetime
    
    interaction = {
        'timestamp': datetime.now().isoformat(),
        'question': question,
        'response': response,
        'metadata': metadata or {}
    }
    
    # Convert to DataFrame
    df = spark.createDataFrame([interaction])
    
    # Save to Delta table
    df.write.mode('append').saveAsTable(f"{CATALOG_NAME}.{SCHEMA_NAME}.agent_interactions")
    
    print(f"✓ Interaction saved")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11. Configuration for Production

# COMMAND ----------

# MAGIC %md
# MAGIC ### Production Checklist:
# MAGIC 
# MAGIC 1. **Security**
# MAGIC    - Store API keys in Databricks Secrets
# MAGIC    - Enable Unity Catalog for data governance
# MAGIC    - Set up access controls
# MAGIC 
# MAGIC 2. **Performance**
# MAGIC    - Cache frequently accessed data
# MAGIC    - Optimize queries with ZORDER
# MAGIC    - Use Delta Lake optimizations
# MAGIC 
# MAGIC 3. **Monitoring**
# MAGIC    - Log all agent interactions
# MAGIC    - Track response quality
# MAGIC    - Monitor API costs
# MAGIC 
# MAGIC 4. **Integration**
# MAGIC    - Connect to Slack/Teams for notifications
# MAGIC    - Schedule daily reports
# MAGIC    - Create REST API endpoints
# MAGIC 
# MAGIC 5. **Continuous Improvement**
# MAGIC    - Collect user feedback
# MAGIC    - Fine-tune prompts based on usage
# MAGIC    - Update system knowledge regularly

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # 🎉 AI Agent Implementation Complete!
# MAGIC 
# MAGIC ## What You Have Now:
# MAGIC - ✅ Functional AI agent with natural language interface
# MAGIC - ✅ Executive summaries and insights
# MAGIC - ✅ Churn risk analysis
# MAGIC - ✅ Team performance evaluation
# MAGIC - ✅ Next best action recommendations
# MAGIC - ✅ Automated daily reports
# MAGIC 
# MAGIC ## Next Steps:
# MAGIC 1. Test with your specific questions
# MAGIC 2. Customize prompts for your business
# MAGIC 3. Integrate with your workflow tools
# MAGIC 4. Deploy as Lakehouse App or REST API
# MAGIC 5. Schedule automated reports
# MAGIC 
# MAGIC ## Resources:
# MAGIC - Databricks AI Functions: https://docs.databricks.com/sql/language-manual/functions/ai_query.html
# MAGIC - Lakehouse Apps: https://docs.databricks.com/lakehouse-apps/
# MAGIC - Model Serving: https://docs.databricks.com/machine-learning/model-serving/
# MAGIC 
# MAGIC ---
# MAGIC 
# MAGIC **Ready to analyze your tickets with AI!** 🚀
