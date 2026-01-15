# Guide: Feature Store and AutoML for Churn Prediction

## 📋 Overview

This guide demonstrates how to create a Feature Store in Databricks and use AutoML to train a churn prediction model based on support ticket data.

## 🎯 Objective

Create a machine learning model that identifies companies at high risk of churn based on:
- Ticket volume and status
- Customer satisfaction (NPS, CSAT)
- Resolution time
- Interaction sentiment
- Temporal trends

## 📁 Files Created

### 1. `churn_feature_store.py`
Main notebook that creates the Feature Store with 60+ features.

**Generated features:**
- **Volume**: total tickets, open/closed tickets, by priority
- **Satisfaction**: average NPS, average CSAT, sentiment distribution
- **Time**: resolution time, first response time
- **Trends**: tickets in last 30/60/90 days
- **Quality**: SLA breach rate, complaint rate
- **Derived**: resolution rates, tickets per customer

### 2. `automl_churn_training.py`
Notebook for training model using Databricks AutoML.

**Features:**
- Runs AutoML with multiple algorithms
- Analyzes feature importance
- Registers best model in MLflow
- Generates batch predictions

### 3. `feature_store_refresh_job.py`
Automated job to update Feature Store periodically.

**Execution modes:**
- `full`: recalculates all features
- `incremental`: updates only recent data

### 4. `setup_feature_store.sql`
SQL script for initial environment setup and validation.

## 🚀 Quick Start

### Step 1: Setup Environment

1. **Load data into Databricks**:
```sql
-- Create schema
CREATE SCHEMA IF NOT EXISTS main.ticket_analytics;

-- Load tables (adjust paths)
CREATE TABLE main.ticket_analytics.companies AS 
SELECT * FROM csv.`/path/to/companies.csv`;

CREATE TABLE main.ticket_analytics.customers AS 
SELECT * FROM csv.`/path/to/customers.csv`;

CREATE TABLE main.ticket_analytics.tickets AS 
SELECT * FROM csv.`/path/to/tickets.csv`;

CREATE TABLE main.ticket_analytics.ticket_interactions AS 
SELECT * FROM csv.`/path/to/ticket_interactions.csv`;
```

2. **Run setup SQL**:
   - Execute `sql/setup_feature_store.sql`
   - Verify data quality checks pass

### Step 2: Create Feature Store

1. Open notebook `churn_feature_store.py` in Databricks
2. Adjust configuration variables:
   ```python
   CATALOG = "main"
   SCHEMA = "ticket_analytics"
   ```
3. Run all notebook commands
4. Verify tables created:
   - `main.ticket_analytics.company_churn_features`
   - `main.ticket_analytics.company_churn_training_data`
   - `main.ticket_analytics.churn_feature_metadata`

### Step 3: Train Model with AutoML

#### Option A: Using the Notebook

1. Open `automl_churn_training.py`
2. Run complete notebook
3. AutoML will:
   - Test multiple algorithms (Random Forest, XGBoost, LightGBM, etc.)
   - Optimize hyperparameters
   - Select best model
   - Register in MLflow

#### Option B: Using Databricks UI

1. Go to **Machine Learning** > **AutoML**
2. Click **Start AutoML**
3. Configure:
   - **Table**: `main.ticket_analytics.company_churn_training_data`
   - **Problem**: Classification
   - **Target**: `is_churn_risk`
   - **Metric**: F1 Score
   - **Timeout**: 30 minutes
4. Click **Start**

### Step 4: Evaluate Results

After training, check:

1. **Experiments in MLflow**:
   - Go to **Machine Learning** > **Experiments**
   - Find your churn experiment
   - Compare model metrics

2. **Feature Importance**:
   - In AutoML notebook, see importance chart
   - Identify features that most impact churn

3. **Model Metrics**:
   ```
   - Accuracy: % of correct predictions
   - Precision: % of correct positive predictions
   - Recall: % of positive cases identified
   - F1 Score: harmonic mean of precision and recall
   - ROC AUC: ability to separate classes
   ```

### Step 5: Use Model in Production

#### Batch Predictions

```python
import mlflow

# Load model
model = mlflow.sklearn.load_model("models:/company_churn_prediction/latest")

# Load data
companies_df = spark.table("main.ticket_analytics.company_churn_training_data")

# Make predictions
predictions = model.predict(companies_df.drop("is_churn_risk").toPandas())

# Save results
result_df = companies_df.select("company_id", "company_name")
result_df = result_df.withColumn("predicted_churn_risk", predictions)
result_df.write.format("delta").mode("overwrite").saveAsTable(
    "main.ticket_analytics.company_churn_predictions"
)
```

#### Real-Time Endpoint

1. Go to **Machine Learning** > **Models**
2. Select `company_churn_prediction`
3. Click **Serve Model**
4. Configure endpoint:
   - **Compute**: Small (1-2 cores)
   - **Scale**: 1-5 instances
5. Use API:

```python
import requests
import json

url = "https://<databricks-instance>/serving-endpoints/company_churn_prediction/invocations"
headers = {"Authorization": f"Bearer {token}"}

data = {
    "dataframe_records": [{
        "total_tickets": 45,
        "tickets_open": 5,
        "avg_nps_score": 6.5,
        "avg_csat_score": 3.8,
        "sla_breach_rate": 0.15,
        # ... other features
    }]
}

response = requests.post(url, headers=headers, json=data)
prediction = response.json()
```

### Step 6: Schedule Automatic Updates

1. Go to **Workflows** > **Jobs**
2. Click **Create Job**
3. Configure:
   - **Task**: `feature_store_refresh_job`
   - **Notebook**: `notebooks/feature_store_refresh_job.py`
   - **Cluster**: Shared cluster or job cluster
   - **Schedule**: Daily at 2:00 AM
   - **Parameters**:
     ```json
     {
       "refresh_mode": "incremental",
       "lookback_days": "7"
     }
     ```
4. Save and enable job

## 📊 Feature Metrics

### Most Important Features (typical)

1. **tickets_last_30_days**: Recent activity
2. **sla_breach_rate**: Service quality
3. **avg_nps_score**: Overall satisfaction
4. **tickets_complaint**: Explicit dissatisfaction
5. **negative_sentiment_rate**: Negative sentiment
6. **ticket_resolution_rate**: Efficiency
7. **days_since_last_ticket**: Engagement
8. **tickets_churn_risk_tag**: Direct indicator

### Prediction Interpretation

| Score | Risk | Recommended Action |
|-------|------|-------------------|
| 0.0 - 0.3 | Low | Maintain standard relationship |
| 0.3 - 0.5 | Medium | Monitor closely |
| 0.5 - 0.7 | High | Proactive CSM contact |
| 0.7 - 1.0 | Critical | Urgent leadership intervention |

## 🔍 Monitoring and Maintenance

### 1. Monitor Feature Drift

```python
from databricks.feature_store import FeatureStoreClient

fs = FeatureStoreClient()

# Current vs historical features
current = spark.table("main.ticket_analytics.company_churn_features")
historical = spark.table("main.ticket_analytics.company_churn_features@v100")

# Compare statistics
current.select("avg_nps_score").summary().show()
historical.select("avg_nps_score").summary().show()
```

### 2. Monitor Model Performance

```python
from sklearn.metrics import classification_report

recent_data = spark.table("main.ticket_analytics.company_churn_predictions") \
    .filter("prediction_timestamp > current_date() - interval 7 days")

# Compare predictions vs reality
# (requires actual churn label after several weeks)
```

### 3. Retrain Model

Retrain when:
- Accuracy drops > 5%
- Significant feature drift
- New business patterns
- Every 3-6 months (minimum)

## 🛠️ Troubleshooting

### Error: "Feature table already exists"

```python
# Delete and recreate
spark.sql("DROP TABLE IF EXISTS main.ticket_analytics.company_churn_features")
# Run notebook again
```

### Error: "Memory error during AutoML"

- Reduce dataset: `training_df.sample(0.5)`
- Increase cluster size
- Reduce `max_trials` in AutoML

### Features with many null values

```python
# Investigate specific features
feature_df.select("avg_nps_score").filter(col("avg_nps_score").isNull()).count()

# Add more imputation in notebook
feature_df = feature_df.fillna({"avg_nps_score": 0})
```

## 📚 Next Steps

1. **Enrich Features**:
   - Add billing data
   - Include product usage
   - Payment history

2. **Segmentation**:
   - Create segment-specific models
   - Different thresholds by company_size

3. **Explainability**:
   - Use SHAP values
   - Create interpretation dashboards

4. **Integration**:
   - Automatic alerts in Slack/Email
   - Churn risk dashboard
   - CRM integration

## 📞 Support

For questions:
- Databricks Documentation: https://docs.databricks.com/
- Feature Store: https://docs.databricks.com/machine-learning/feature-store/
- AutoML: https://docs.databricks.com/machine-learning/automl/

---

**Created by**: Fabio Gonçalves  
**Date**: January 2026  
**Version**: 1.0
