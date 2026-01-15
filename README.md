# Databricks Tickets Agent - Customer Support Analysis with GenAI

Complete solution for analyzing customer support tickets using Databricks and GenAI.

## Project Structure

```
databricks-tickets-agent/
├── data/                    # CSV data files (3,574 records)
│   ├── companies.csv        # 100 customer companies
│   ├── customers.csv        # 300 individual users
│   ├── agents.csv          # 25 support agents
│   ├── tickets.csv         # 500 support tickets
│   └── ticket_interactions.csv  # 2,649 interactions
│
├── sql/                     # SQL scripts for Databricks
│   ├── ddl_tables.sql      # DDL to create Delta tables
│   ├── load_data.sql       # Data loading scripts
│   ├── analysis_queries.sql # 50+ ready-to-use queries
│   └── quick_demo_notebook.sql # SQL demo notebook
│
├── notebooks/               # Databricks notebooks
│   ├── setup_and_analysis_notebook.py  # Complete setup + analysis
│   ├── genai_agent_example.py          # GenAI examples
│   ├── ai_agent_implementation.py      # AI Agent implementation
│   ├── churn_feature_store.py          # Feature Store for churn prediction
│   ├── automl_churn_training.py        # AutoML training notebook
│   └── feature_store_refresh_job.py    # Automated feature refresh
│
├── prompts/                 # AI Agent prompts (PT & EN)
│   ├── ai_agent_prompts_pt.md          # AI Agent prompts (Portuguese)
│   ├── ai_agent_prompts_en.md          # AI Agent prompts (English)
│   ├── genie_example_prompts_pt.md     # Genie examples (Portuguese)
│   └── genie_example_prompts_en.md     # Genie examples (English)
│
├── scripts/                 # Python utility scripts
│   ├── generate_data.py    # Synthetic data generator
│   ├── validate_data.py    # Data quality validation
│   └── requirements.txt    # Python dependencies
│
└── docs/                    # Documentation (PT & EN)
    ├── README_pt.md         # Complete documentation (Portuguese)
    ├── README_en.md         # Complete documentation (English)
    ├── QUICKSTART_pt.md     # 5-minute quick start (Portuguese)
    ├── QUICKSTART_en.md     # 5-minute quick start (English)
    ├── PROJECT_SUMMARY_pt.md # Executive summary (Portuguese)
    ├── PROJECT_SUMMARY_en.md # Executive summary (English)
    ├── FEATURE_STORE_GUIDE_pt.md # Feature Store guide (Portuguese)
    └── FEATURE_STORE_GUIDE_en.md # Feature Store guide (English)

```

## Quick Start

### 1. Upload Data to Databricks
```bash
# Upload CSV files to DBFS
databricks fs cp data/*.csv dbfs:/FileStore/tickets/
```

### 2. Import Notebook
- Import `notebooks/setup_and_analysis_notebook.py` into Databricks
- Configure parameters (schema, CSV path)
- Run all cells

### 3. Start Analyzing
- Use `sql/quick_demo_notebook.sql` for quick demos
- Execute queries from `sql/analysis_queries.sql`
- Create Genie Space for natural language queries

### 4. 🆕 Train Churn Prediction Model (Optional)
- Run `sql/setup_feature_store.sql` to setup environment
- Execute `notebooks/churn_feature_store.py` to create features
- Use `notebooks/automl_churn_training.py` to train model
- See `docs/FEATURE_STORE_GUIDE_pt.md` for detailed instructions

## Key Features

- ✅ 500 realistic support tickets in Portuguese (BR)
- ✅ Payment processing context (similar to Cielo)
- ✅ 5 related Delta tables with referential integrity
- ✅ PII fields identified and tagged
- ✅ Ready-to-use notebooks and queries
- ✅ Churn risk detection
- ✅ SLA monitoring
- ✅ Sentiment analysis
- ✅ Agent performance tracking

## Documentation

All detailed documentation is available in Portuguese in the `docs/` folder:

- **README_pt.md** - Complete technical documentation
- **QUICKSTART_pt.md** - 5-minute setup guide
- **PROJECT_SUMMARY_pt.md** - Executive summary and statistics
- **genie_example_prompts_pt.md** - Example questions for Databricks Genie

## Use Cases

1. **Executive Summaries** - "What's happening this week?"
2. **Churn Risk Analysis** - Identify customers at risk of leaving
3. **Performance Monitoring** - Track SLA compliance and team metrics
4. **Trend Analysis** - Discover patterns and common issues
5. **Next Best Action** - AI-powered recommendations
6. **🆕 ML-Powered Churn Prediction** - Train and deploy AutoML models using Feature Store

## Technical Stack

- **Delta Lake** - ACID transactions
- **Databricks SQL** - Analytics engine
- **Unity Catalog** - Governance and PII tags
- **PySpark** - Data processing
- **Databricks Genie** - Natural language queries
- **🆕 Feature Store** - ML feature management and versioning
- **🆕 AutoML** - Automated model training and optimization
- **🆕 MLflow** - Model tracking and deployment

## Requirements

- Databricks workspace
- Python 3.8+ (for local data generation)
- Faker library (included in requirements.txt)

## Data Statistics

- Companies: 100
- Customers: 300
- Agents: 25
- Tickets: 500
- Interactions: 2,649
- **Total Records: 3,574**

## Support

This is a demonstration project with synthetic data. All names, companies, and identifiers are fictitious.

For detailed instructions in Portuguese, see `docs/README_pt.md`.

---

**Version:** 1.0  
**Date:** January 2026  
**Status:** ✅ Production-ready
