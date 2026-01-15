# Databricks notebook source
# MAGIC %md
# MAGIC # Churn Prediction - Complete Example
# MAGIC 
# MAGIC This notebook demonstrates a complete end-to-end workflow for churn prediction:
# MAGIC 1. Load and explore data
# MAGIC 2. Create features
# MAGIC 3. Train model
# MAGIC 4. Make predictions
# MAGIC 5. Analyze results

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🎯 Business Objective
# MAGIC 
# MAGIC **Goal**: Identify companies at high risk of churn based on their support ticket patterns
# MAGIC 
# MAGIC **Success Criteria**:
# MAGIC - Model accuracy > 80%
# MAGIC - F1 Score > 0.75
# MAGIC - Identify 90% of companies that will churn
# MAGIC 
# MAGIC **Business Impact**:
# MAGIC - Proactive customer success interventions
# MAGIC - Reduce churn by 15-20%
# MAGIC - Increase customer lifetime value

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Setup and Configuration

# COMMAND ----------

from pyspark.sql import functions as F
from databricks import feature_store
import mlflow
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
CATALOG = "main"
SCHEMA = "ticket_analytics"

# Set style for plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

print(f"✓ Using catalog: {CATALOG}")
print(f"✓ Using schema: {SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Explore the Data

# COMMAND ----------

# Load main tables
companies = spark.table(f"{CATALOG}.{SCHEMA}.companies")
tickets = spark.table(f"{CATALOG}.{SCHEMA}.tickets")

# Basic statistics
print("=== Data Overview ===")
print(f"Total companies: {companies.count()}")
print(f"Total tickets: {tickets.count()}")

print("\n=== Company Status Distribution ===")
companies.groupBy("status").count().orderBy("count", ascending=False).show()

print("\n=== Company Churn Risk Distribution ===")
companies.selectExpr(
    "CASE WHEN churn_risk_score > 0.7 THEN 'High Risk' " +
    "WHEN churn_risk_score > 0.3 THEN 'Medium Risk' " +
    "ELSE 'Low Risk' END as risk_category"
).groupBy("risk_category").count().show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Analyze Ticket Patterns

# COMMAND ----------

# Tickets by company
tickets_by_company = tickets.groupBy("company_id").agg(
    F.count("*").alias("ticket_count"),
    F.avg(F.col("nps_score").cast("double")).alias("avg_nps"),
    F.sum(F.when(F.col("category") == "COMPLAINT", 1).otherwise(0)).alias("complaints")
)

# Join with company churn risk
analysis_df = companies.select("company_id", "company_name", "churn_risk_score") \
    .join(tickets_by_company, "company_id", "left")

# Show companies with high ticket volume
print("=== Top 10 Companies by Ticket Volume ===")
analysis_df.orderBy("ticket_count", ascending=False).show(10)

# COMMAND ----------

# Correlation analysis
print("=== Correlation with Churn Risk ===")
correlation_pdf = analysis_df.toPandas()

correlations = correlation_pdf[['churn_risk_score', 'ticket_count', 'avg_nps', 'complaints']].corr()
print(correlations['churn_risk_score'].sort_values(ascending=False))

# Visualize
plt.figure(figsize=(8, 6))
sns.heatmap(correlations, annot=True, cmap='coolwarm', center=0)
plt.title('Feature Correlation Matrix')
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Quick Feature Engineering

# COMMAND ----------

# Create simple features for demonstration
simple_features = tickets.groupBy("company_id").agg(
    # Volume
    F.count("*").alias("total_tickets"),
    F.sum(F.when(F.col("status") == "OPEN", 1).otherwise(0)).alias("open_tickets"),
    
    # Satisfaction
    F.avg(F.col("nps_score").cast("double")).alias("avg_nps"),
    F.avg(F.col("csat_score").cast("double")).alias("avg_csat"),
    
    # Quality
    F.sum(F.when(F.col("sla_breached") == "TRUE", 1).otherwise(0)).alias("sla_breached_count"),
    F.sum(F.when(F.col("category") == "COMPLAINT", 1).otherwise(0)).alias("complaint_count"),
    
    # Sentiment
    F.sum(F.when(F.col("sentiment").isin(["NEGATIVE", "VERY_NEGATIVE"]), 1).otherwise(0)).alias("negative_sentiment_count")
)

# Join with companies
training_data = companies.select("company_id", "company_name", "churn_risk_score") \
    .join(simple_features, "company_id", "left") \
    .fillna(0)

# Create binary target
training_data = training_data.withColumn(
    "is_high_churn_risk",
    F.when(F.col("churn_risk_score") > 0.7, 1).otherwise(0)
)

print(f"Training dataset: {training_data.count()} companies")
print("\nTarget distribution:")
training_data.groupBy("is_high_churn_risk").count().show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Train Simple Model

# COMMAND ----------

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve

# Convert to pandas
train_pdf = training_data.toPandas()

# Features and target
feature_cols = [
    'total_tickets', 'open_tickets', 'avg_nps', 'avg_csat',
    'sla_breached_count', 'complaint_count', 'negative_sentiment_count'
]

X = train_pdf[feature_cols].fillna(0)
y = train_pdf['is_high_churn_risk']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")

# Train model
with mlflow.start_run(run_name="simple_churn_model"):
    # Log parameters
    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)
    
    # Train
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Metrics
    accuracy = model.score(X_test, y_test)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("roc_auc", roc_auc)
    
    # Log model
    mlflow.sklearn.log_model(model, "model")
    
    print(f"✓ Model trained successfully!")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"ROC AUC: {roc_auc:.3f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Evaluate Model

# COMMAND ----------

print("=== Classification Report ===")
print(classification_report(y_test, y_pred, target_names=['Low Risk', 'High Risk']))

print("\n=== Confusion Matrix ===")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# Visualize confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Low Risk', 'High Risk'],
            yticklabels=['Low Risk', 'High Risk'])
plt.title('Confusion Matrix')
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.tight_layout()
plt.show()

# COMMAND ----------

# ROC Curve
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)

plt.figure(figsize=(10, 6))
plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {roc_auc:.3f})')
plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - Churn Prediction Model')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Feature Importance

# COMMAND ----------

# Get feature importance
importance_df = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("=== Feature Importance ===")
print(importance_df.to_string(index=False))

# Visualize
plt.figure(figsize=(10, 6))
plt.barh(importance_df['feature'], importance_df['importance'])
plt.xlabel('Importance')
plt.title('Feature Importance for Churn Prediction')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Make Predictions on All Companies

# COMMAND ----------

# Predict for all companies
all_companies_pdf = training_data.select(
    "company_id", "company_name", "churn_risk_score", *feature_cols
).toPandas()

# Fill missing values
X_all = all_companies_pdf[feature_cols].fillna(0)

# Predictions
predictions = model.predict(X_all)
prediction_proba = model.predict_proba(X_all)[:, 1]

# Add to dataframe
all_companies_pdf['predicted_churn_risk'] = predictions
all_companies_pdf['churn_probability'] = prediction_proba

# Sort by risk
all_companies_pdf = all_companies_pdf.sort_values('churn_probability', ascending=False)

print("=== Top 20 Companies at Risk of Churn ===")
print(all_companies_pdf[
    ['company_name', 'churn_probability', 'predicted_churn_risk', 
     'total_tickets', 'complaint_count', 'avg_nps']
].head(20).to_string(index=False))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Risk Distribution Analysis

# COMMAND ----------

# Create risk segments
all_companies_pdf['risk_segment'] = pd.cut(
    all_companies_pdf['churn_probability'],
    bins=[0, 0.3, 0.5, 0.7, 1.0],
    labels=['Low', 'Medium', 'High', 'Critical']
)

print("=== Companies by Risk Segment ===")
risk_distribution = all_companies_pdf['risk_segment'].value_counts().sort_index()
print(risk_distribution)

# Visualize
plt.figure(figsize=(10, 6))
risk_distribution.plot(kind='bar', color=['green', 'yellow', 'orange', 'red'])
plt.title('Distribution of Companies by Churn Risk Segment')
plt.xlabel('Risk Segment')
plt.ylabel('Number of Companies')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# COMMAND ----------

# Risk probability distribution
plt.figure(figsize=(12, 6))
plt.hist(all_companies_pdf['churn_probability'], bins=30, edgecolor='black', alpha=0.7)
plt.axvline(0.7, color='red', linestyle='--', label='High Risk Threshold (0.7)')
plt.axvline(0.5, color='orange', linestyle='--', label='Medium Risk Threshold (0.5)')
plt.xlabel('Churn Probability')
plt.ylabel('Number of Companies')
plt.title('Distribution of Churn Probability Across All Companies')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Save Predictions

# COMMAND ----------

# Convert back to Spark DataFrame
predictions_df = spark.createDataFrame(
    all_companies_pdf[['company_id', 'company_name', 'predicted_churn_risk', 'churn_probability', 'risk_segment']]
)

# Add timestamp
predictions_df = predictions_df.withColumn("prediction_timestamp", F.current_timestamp())

# Save to Delta table
predictions_table = f"{CATALOG}.{SCHEMA}.churn_predictions_example"
predictions_df.write.format("delta").mode("overwrite").saveAsTable(predictions_table)

print(f"✓ Predictions saved to: {predictions_table}")
print(f"✓ Total companies scored: {predictions_df.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11. Actionable Insights

# COMMAND ----------

# Critical companies needing immediate attention
critical_companies = all_companies_pdf[
    all_companies_pdf['risk_segment'] == 'Critical'
][['company_name', 'churn_probability', 'total_tickets', 'complaint_count', 'avg_nps']]

print("=== 🚨 CRITICAL: Companies Requiring Immediate Attention ===")
if len(critical_companies) > 0:
    print(critical_companies.to_string(index=False))
    print(f"\n📢 Total critical companies: {len(critical_companies)}")
    print("\n💡 Recommended Actions:")
    print("   1. Schedule executive-level meetings within 48 hours")
    print("   2. Review and address all open complaints immediately")
    print("   3. Offer service credits or compensation if appropriate")
    print("   4. Assign dedicated account manager")
else:
    print("✓ No companies in critical risk category")

# COMMAND ----------

# High risk companies for proactive outreach
high_risk_companies = all_companies_pdf[
    all_companies_pdf['risk_segment'] == 'High'
][['company_name', 'churn_probability', 'total_tickets', 'complaint_count', 'avg_nps']].head(10)

print("\n=== ⚠️  HIGH RISK: Companies for Proactive Outreach ===")
if len(high_risk_companies) > 0:
    print(high_risk_companies.to_string(index=False))
    print(f"\n📢 Total high risk companies: {len(high_risk_companies)}")
    print("\n💡 Recommended Actions:")
    print("   1. CSM to schedule check-in calls this week")
    print("   2. Review recent tickets for patterns")
    print("   3. Offer training or onboarding support")
    print("   4. Gather feedback on service improvements")
else:
    print("✓ No companies in high risk category")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12. Model Performance Summary

# COMMAND ----------

# Summary statistics
print("=" * 80)
print("🎯 CHURN PREDICTION MODEL - PERFORMANCE SUMMARY")
print("=" * 80)

print(f"\n📊 Model Metrics:")
print(f"   • Accuracy: {accuracy:.1%}")
print(f"   • ROC AUC Score: {roc_auc:.3f}")
print(f"   • Training Samples: {len(X_train)}")
print(f"   • Test Samples: {len(X_test)}")

print(f"\n📈 Predictions:")
print(f"   • Total Companies Scored: {len(all_companies_pdf)}")
print(f"   • Critical Risk: {len(all_companies_pdf[all_companies_pdf['risk_segment'] == 'Critical'])}")
print(f"   • High Risk: {len(all_companies_pdf[all_companies_pdf['risk_segment'] == 'High'])}")
print(f"   • Medium Risk: {len(all_companies_pdf[all_companies_pdf['risk_segment'] == 'Medium'])}")
print(f"   • Low Risk: {len(all_companies_pdf[all_companies_pdf['risk_segment'] == 'Low'])}")

print(f"\n🎯 Top Risk Factors:")
for idx, row in importance_df.head(3).iterrows():
    print(f"   {idx+1}. {row['feature']}: {row['importance']:.3f}")

print(f"\n📁 Output:")
print(f"   • Predictions Table: {predictions_table}")
print(f"   • MLflow Run: Check MLflow UI for detailed metrics")

print("\n" + "=" * 80)
print("✓ Analysis Complete!")
print("=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 💡 Next Steps
# MAGIC 
# MAGIC 1. **Improve Model**:
# MAGIC    - Use the full Feature Store with 60+ features
# MAGIC    - Run AutoML for better algorithms
# MAGIC    - Tune hyperparameters
# MAGIC 
# MAGIC 2. **Operationalize**:
# MAGIC    - Schedule daily prediction runs
# MAGIC    - Set up alerts for critical companies
# MAGIC    - Create dashboard for tracking
# MAGIC 
# MAGIC 3. **Take Action**:
# MAGIC    - Export critical companies list to CRM
# MAGIC    - Automate email alerts to CSM team
# MAGIC    - Track intervention success rates
# MAGIC 
# MAGIC 4. **Monitor**:
# MAGIC    - Track actual churn vs predictions
# MAGIC    - Update model monthly
# MAGIC    - Add new features based on business feedback
