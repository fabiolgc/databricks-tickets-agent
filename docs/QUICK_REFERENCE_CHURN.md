# Churn Prediction - Quick Reference Card

## 🚀 Quick Start Commands

### 1. Setup (One Time)
```sql
-- Run in Databricks SQL
%run /Workspace/sql/setup_feature_store.sql
```

### 2. Create Feature Store
```python
# Open and run this notebook
/Workspace/notebooks/churn_feature_store.py

# Key configuration
CATALOG = "main"
SCHEMA = "ticket_analytics"
```

### 3. Train Model
```python
# Option A: Simple example (30 min)
/Workspace/notebooks/churn_prediction_example.py

# Option B: Full AutoML (2 hours)
/Workspace/notebooks/automl_churn_training.py
```

---

## 📊 Key Tables

| Table Name | Purpose | Refresh Frequency |
|------------|---------|-------------------|
| `company_churn_features` | All features | Daily |
| `company_churn_training_data` | ML training dataset | Daily |
| `company_churn_predictions` | Latest predictions | Real-time/Batch |
| `churn_feature_metadata` | Feature documentation | On demand |

---

## 🎯 Common Queries

### Get High Risk Companies
```sql
SELECT 
    company_name,
    churn_probability,
    risk_segment,
    total_tickets,
    avg_nps_score
FROM main.ticket_analytics.company_churn_predictions
WHERE churn_probability > 0.7
ORDER BY churn_probability DESC;
```

### Top Risk Factors
```sql
SELECT 
    company_name,
    tickets_complaint,
    sla_breach_rate,
    negative_sentiment_rate,
    avg_nps_score
FROM main.ticket_analytics.company_churn_features
WHERE churn_risk_score > 0.7
ORDER BY tickets_complaint DESC;
```

### Churn by Segment
```sql
SELECT 
    segment,
    COUNT(*) as total_companies,
    AVG(churn_risk_score) as avg_risk,
    SUM(CASE WHEN churn_risk_score > 0.7 THEN 1 ELSE 0 END) as high_risk_count
FROM main.ticket_analytics.companies c
JOIN main.ticket_analytics.company_churn_features f ON c.company_id = f.company_id
GROUP BY segment
ORDER BY avg_risk DESC;
```

---

## 🔧 Python Snippets

### Load Model and Predict
```python
import mlflow

# Load latest model
model = mlflow.sklearn.load_model("models:/company_churn_prediction/latest")

# Get features
features_df = spark.table("main.ticket_analytics.company_churn_features")

# Predict
X = features_df.drop("company_id", "company_name", "churn_risk_score").toPandas()
predictions = model.predict(X)
```

### Real-Time Scoring
```python
from databricks.feature_store import FeatureStoreClient

fs = FeatureStoreClient()

# Score single company
company_features = fs.read_table("main.ticket_analytics.company_churn_features") \
    .filter("company_id = 'COMP00001'")

prediction = model.predict(company_features.toPandas())
print(f"Churn risk: {prediction[0]}")
```

### Update Features
```python
# Trigger feature refresh
dbutils.notebook.run(
    "/Workspace/notebooks/feature_store_refresh_job",
    timeout_seconds=3600,
    arguments={"refresh_mode": "incremental", "lookback_days": "7"}
)
```

---

## 📈 Feature Importance (Top 10)

| Rank | Feature | Typical Importance | What It Means |
|------|---------|-------------------|---------------|
| 1 | tickets_last_30_days | 0.15-0.20 | Recent activity level |
| 2 | sla_breach_rate | 0.12-0.18 | Service quality |
| 3 | avg_nps_score | 0.10-0.15 | Customer satisfaction |
| 4 | tickets_complaint | 0.08-0.12 | Dissatisfaction level |
| 5 | negative_sentiment_rate | 0.07-0.11 | Sentiment analysis |
| 6 | ticket_resolution_rate | 0.06-0.09 | Resolution efficiency |
| 7 | tickets_churn_risk_tag | 0.05-0.08 | Manual risk flags |
| 8 | avg_resolution_time_hours | 0.04-0.07 | Speed of resolution |
| 9 | days_since_last_ticket | 0.04-0.06 | Engagement level |
| 10 | complaint_rate | 0.03-0.05 | Complaint frequency |

---

## 🎨 Risk Thresholds

| Risk Level | Probability | Action | Response Time |
|------------|-------------|--------|---------------|
| 🟢 Low | 0.0 - 0.3 | Monitor | Quarterly |
| 🟡 Medium | 0.3 - 0.5 | Watch closely | Monthly |
| 🟠 High | 0.5 - 0.7 | Proactive outreach | Weekly |
| 🔴 Critical | 0.7 - 1.0 | Immediate intervention | 24-48h |

---

## 🔄 Refresh Schedule

### Feature Store Refresh Job
```python
# Job configuration
{
    "name": "churn_feature_store_daily_refresh",
    "notebook_path": "/Workspace/notebooks/feature_store_refresh_job",
    "schedule": "0 2 * * *",  # Daily at 2 AM
    "cluster": "job-cluster",
    "parameters": {
        "refresh_mode": "incremental",
        "lookback_days": "7"
    }
}
```

### Model Retraining
```python
# Retrain criteria
if (
    accuracy < 0.75 or
    feature_drift > 0.15 or
    months_since_training > 3
):
    retrain_model()
```

---

## 📧 Alert Templates

### Critical Risk Alert
```python
def send_critical_alert(company):
    subject = f"🚨 CRITICAL: {company.name} at High Churn Risk"
    body = f"""
    Company: {company.name}
    Churn Probability: {company.risk:.1%}
    
    Key Issues:
    - Complaints: {company.complaints}
    - SLA Breaches: {company.sla_breaches}
    - NPS: {company.nps}
    
    Action Required: Immediate executive engagement within 48h
    """
    send_email(to="csm-team@company.com", subject=subject, body=body)
```

---

## 🐛 Troubleshooting

### Feature Store Not Updating
```python
# Check last update
spark.sql("""
    SELECT MAX(feature_timestamp) as last_update
    FROM main.ticket_analytics.company_churn_features
""").show()

# Force full refresh
dbutils.notebook.run(
    "feature_store_refresh_job",
    arguments={"refresh_mode": "full"}
)
```

### Model Performance Degraded
```python
# Check recent accuracy
from sklearn.metrics import accuracy_score

recent_predictions = spark.table("company_churn_predictions") \
    .filter("prediction_timestamp > current_date() - 30")

# Compare with actual churn
# (requires ground truth data)
```

### Missing Features
```python
# Check for nulls
feature_df = spark.table("company_churn_features")

for col in feature_df.columns:
    null_count = feature_df.filter(f"{col} IS NULL").count()
    if null_count > 0:
        print(f"{col}: {null_count} nulls")
```

---

## 📱 API Endpoints

### Batch Prediction
```python
POST /api/2.0/mlflow/runs/{run_id}/predictions

{
    "company_ids": ["COMP00001", "COMP00002"],
    "features": ["total_tickets", "avg_nps", ...]
}
```

### Real-Time Scoring
```python
POST /serving-endpoints/company_churn_prediction/invocations

{
    "dataframe_records": [{
        "total_tickets": 45,
        "avg_nps_score": 6.5,
        "sla_breach_rate": 0.15
    }]
}
```

---

## 📚 File Locations

```
Notebooks:
├── churn_feature_store.py              # Feature creation
├── automl_churn_training.py            # Model training
├── feature_store_refresh_job.py        # Auto refresh
└── churn_prediction_example.py         # Quick example

Documentation:
├── FEATURE_STORE_GUIDE_pt.md           # Full guide (PT)
├── FEATURE_STORE_GUIDE_en.md           # Full guide (EN)
├── CHURN_PREDICTION_SUMMARY_pt.md      # Summary
└── QUICK_REFERENCE_CHURN.md            # This file

SQL:
└── setup_feature_store.sql             # Initial setup
```

---

## ⌨️ Keyboard Shortcuts

| Action | Shortcut | Description |
|--------|----------|-------------|
| Run Cell | Shift + Enter | Execute current cell |
| Run All | Cmd/Ctrl + Shift + Enter | Run all cells |
| Insert Cell | B (below), A (above) | Add new cell |
| Cell to Code | Y | Convert to code |
| Cell to Markdown | M | Convert to markdown |

---

## 🎯 Success Metrics

### Week 1
- [ ] Feature Store created
- [ ] Model trained
- [ ] First predictions generated

### Month 1
- [ ] Daily refresh scheduled
- [ ] Alerts configured
- [ ] Dashboard created
- [ ] 10+ interventions made

### Quarter 1
- [ ] Churn reduced by 15%
- [ ] Model accuracy > 80%
- [ ] ROI measured
- [ ] Team trained

---

## 💬 Quick Help

```python
# Get help on Feature Store
help(feature_store.FeatureStoreClient)

# Get help on AutoML
help(automl.classify)

# List all features
spark.table("churn_feature_metadata").display()

# Check model registry
import mlflow
client = mlflow.tracking.MlflowClient()
client.search_model_versions("name='company_churn_prediction'")
```

---

**Last Updated**: January 2026  
**Version**: 1.0  
**For full documentation, see**: `FEATURE_STORE_GUIDE_pt.md`
