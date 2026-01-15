# Databricks notebook source
# MAGIC %md
# MAGIC # AutoML Churn Prediction Training
# MAGIC 
# MAGIC This notebook demonstrates how to use Databricks AutoML with the feature store
# MAGIC to train a churn prediction model.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Setup

# COMMAND ----------

from databricks import automl
from databricks.feature_store import FeatureStoreClient
from datetime import datetime
import mlflow

# Configuration
CATALOG = "main"
SCHEMA = "ticket_analytics"
TRAINING_TABLE = f"{CATALOG}.{SCHEMA}.company_churn_training_data"
EXPERIMENT_PATH = "/Users/fabio.goncalves/churn_prediction_experiments"

fs = FeatureStoreClient()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Load Training Data

# COMMAND ----------

training_df = spark.table(TRAINING_TABLE)

print(f"Training dataset shape: {training_df.count()} rows")
print(f"\nTarget distribution:")
training_df.groupBy("is_churn_risk").count().show()

display(training_df.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Run AutoML Classification

# COMMAND ----------

# Run AutoML
summary = automl.classify(
    dataset=training_df,
    target_col="is_churn_risk",
    primary_metric="f1",  # Can be: f1, precision, recall, roc_auc, accuracy
    timeout_minutes=30,
    max_trials=20,
    experiment_name=f"churn_prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Review Results

# COMMAND ----------

print("AutoML Summary:")
print("-" * 80)
print(f"Best trial run ID: {summary.best_trial.mlflow_run_id}")
print(f"Best trial metrics: {summary.best_trial.metrics}")

# Display the best model details
print("\nTo view the best model:")
print(f"MLflow Run: {summary.best_trial.mlflow_run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Load and Evaluate Best Model

# COMMAND ----------

# Load the best model
best_model_uri = f"runs:/{summary.best_trial.mlflow_run_id}/model"
best_model = mlflow.sklearn.load_model(best_model_uri)

print("Best model loaded successfully!")
print(f"Model type: {type(best_model)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Feature Importance

# COMMAND ----------

import pandas as pd
import matplotlib.pyplot as plt

# Get feature importance
try:
    if hasattr(best_model, 'feature_importances_'):
        feature_importance = best_model.feature_importances_
        feature_names = [c for c in training_df.columns if c not in ['company_id', 'company_name', 'is_churn_risk', 'feature_timestamp']]
        
        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': feature_importance
        }).sort_values('importance', ascending=False).head(20)
        
        # Plot
        plt.figure(figsize=(12, 8))
        plt.barh(importance_df['feature'], importance_df['importance'])
        plt.xlabel('Importance')
        plt.title('Top 20 Feature Importances')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()
        
        print("\nTop 10 Most Important Features:")
        print(importance_df.head(10).to_string(index=False))
    else:
        print("Model does not have feature_importances_ attribute")
except Exception as e:
    print(f"Could not extract feature importance: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Register Best Model

# COMMAND ----------

from mlflow.tracking import MlflowClient

client = MlflowClient()

# Register the model
model_name = "company_churn_prediction"
model_version = mlflow.register_model(
    model_uri=best_model_uri,
    name=model_name
)

print(f"Model registered: {model_name}")
print(f"Version: {model_version.version}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Make Predictions on New Data

# COMMAND ----------

# Load recent companies that need predictions
companies_to_score = spark.table(TRAINING_TABLE).limit(10)

# Make predictions
predictions = best_model.predict(
    companies_to_score.drop("is_churn_risk", "company_id", "company_name", "feature_timestamp").toPandas()
)

# Add predictions to dataframe
result_df = companies_to_score.select("company_id", "company_name", "is_churn_risk").toPandas()
result_df['predicted_churn_risk'] = predictions
result_df['prediction_confidence'] = best_model.predict_proba(
    companies_to_score.drop("is_churn_risk", "company_id", "company_name", "feature_timestamp").toPandas()
).max(axis=1)

print("\nSample Predictions:")
print(result_df.to_string(index=False))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Model Performance Metrics

# COMMAND ----------

from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split

# Split data for evaluation
train_pdf = training_df.toPandas()
feature_cols = [c for c in train_pdf.columns if c not in ['company_id', 'company_name', 'is_churn_risk', 'feature_timestamp', 'churn_risk_score', 'status']]

X = train_pdf[feature_cols]
y = train_pdf['is_churn_risk']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Predictions
y_pred = best_model.predict(X_test)
y_pred_proba = best_model.predict_proba(X_test)[:, 1]

# Metrics
print("Classification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print(f"\nROC AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Create Batch Inference Job

# COMMAND ----------

# Save predictions to Delta table
PREDICTIONS_TABLE = f"{CATALOG}.{SCHEMA}.company_churn_predictions"

predictions_df = spark.createDataFrame(result_df)
predictions_df = predictions_df.withColumn("prediction_timestamp", F.current_timestamp())

predictions_df.write.format("delta").mode("overwrite").saveAsTable(PREDICTIONS_TABLE)

print(f"✓ Predictions saved to: {PREDICTIONS_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC 
# MAGIC ### AutoML Training Complete! ✓
# MAGIC 
# MAGIC **What was accomplished:**
# MAGIC - Trained multiple models using AutoML
# MAGIC - Identified best performing model
# MAGIC - Analyzed feature importance
# MAGIC - Registered model in MLflow
# MAGIC - Generated predictions
# MAGIC - Saved predictions to Delta table
# MAGIC 
# MAGIC **Next Steps:**
# MAGIC 1. Review model performance in MLflow UI
# MAGIC 2. Set up automated retraining schedule
# MAGIC 3. Create real-time inference endpoint
# MAGIC 4. Integrate predictions into business workflows
# MAGIC 5. Monitor model drift and performance over time
# MAGIC 
# MAGIC **Useful Commands:**
# MAGIC ```python
# MAGIC # Load model for scoring
# MAGIC model = mlflow.sklearn.load_model(f"models:/{model_name}/latest")
# MAGIC 
# MAGIC # Get predictions
# MAGIC predictions = model.predict(new_data)
# MAGIC ```
