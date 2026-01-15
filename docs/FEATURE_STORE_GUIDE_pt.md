# Guia: Feature Store e AutoML para Predição de Churn

## 📋 Visão Geral

Este guia demonstra como criar uma Feature Store no Databricks e usar o AutoML para treinar um modelo de predição de churn baseado em dados de tickets de suporte.

## 🎯 Objetivo

Criar um modelo de machine learning que identifique empresas com alto risco de churn baseado em:
- Volume e status de tickets
- Satisfação do cliente (NPS, CSAT)
- Tempo de resolução
- Sentimento das interações
- Tendências temporais

## 📁 Arquivos Criados

### 1. `churn_feature_store.py`
Notebook principal que cria a Feature Store com 60+ features.

**Features geradas:**
- **Volume**: total de tickets, tickets abertos/fechados, por prioridade
- **Satisfação**: NPS médio, CSAT médio, distribuição de sentimentos
- **Tempo**: tempo de resolução, tempo de primeira resposta
- **Tendências**: tickets nos últimos 30/60/90 dias
- **Qualidade**: taxa de breach de SLA, taxa de reclamações
- **Derivadas**: taxas de resolução, tickets por cliente

### 2. `automl_churn_training.py`
Notebook para treinar modelo usando Databricks AutoML.

**Funcionalidades:**
- Executa AutoML com múltiplos algoritmos
- Analisa feature importance
- Registra melhor modelo no MLflow
- Gera predições em batch

### 3. `feature_store_refresh_job.py`
Job automatizado para atualizar a Feature Store periodicamente.

**Modos de execução:**
- `full`: recalcula todas as features
- `incremental`: atualiza apenas dados recentes

## 🚀 Como Usar

### Passo 1: Preparar Ambiente

1. **Carregar dados no Databricks**:
```sql
-- Criar schema
CREATE SCHEMA IF NOT EXISTS main.ticket_analytics;

-- Carregar tabelas (ajuste os caminhos)
CREATE TABLE main.ticket_analytics.companies AS 
SELECT * FROM csv.`/path/to/companies.csv`;

CREATE TABLE main.ticket_analytics.customers AS 
SELECT * FROM csv.`/path/to/customers.csv`;

CREATE TABLE main.ticket_analytics.tickets AS 
SELECT * FROM csv.`/path/to/tickets.csv`;

CREATE TABLE main.ticket_analytics.ticket_interactions AS 
SELECT * FROM csv.`/path/to/ticket_interactions.csv`;
```

### Passo 2: Criar Feature Store

1. Abra o notebook `churn_feature_store.py` no Databricks
2. Ajuste as variáveis de configuração:
   ```python
   CATALOG = "main"
   SCHEMA = "ticket_analytics"
   ```
3. Execute todos os comandos do notebook
4. Verifique se as tabelas foram criadas:
   - `main.ticket_analytics.company_churn_features`
   - `main.ticket_analytics.company_churn_training_data`
   - `main.ticket_analytics.churn_feature_metadata`

### Passo 3: Treinar Modelo com AutoML

#### Opção A: Usando o Notebook

1. Abra `automl_churn_training.py`
2. Execute o notebook completo
3. O AutoML vai:
   - Testar múltiplos algoritmos (Random Forest, XGBoost, LightGBM, etc.)
   - Otimizar hiperparâmetros
   - Selecionar o melhor modelo
   - Registrar no MLflow

#### Opção B: Usando a UI do Databricks

1. Vá em **Machine Learning** > **AutoML**
2. Clique em **Start AutoML**
3. Configure:
   - **Tabela**: `main.ticket_analytics.company_churn_training_data`
   - **Problema**: Classification
   - **Target**: `is_churn_risk`
   - **Métrica**: F1 Score
   - **Timeout**: 30 minutos
4. Clique em **Start**

### Passo 4: Avaliar Resultados

Após o treinamento, verifique:

1. **Experimentos no MLflow**:
   - Vá em **Machine Learning** > **Experiments**
   - Encontre seu experimento de churn
   - Compare métricas dos modelos

2. **Feature Importance**:
   - No notebook AutoML, veja o gráfico de importância
   - Identifique quais features mais impactam o churn

3. **Métricas do Modelo**:
   ```
   - Accuracy: % de predições corretas
   - Precision: % de predições positivas corretas
   - Recall: % de casos positivos identificados
   - F1 Score: média harmônica de precision e recall
   - ROC AUC: capacidade de separar classes
   ```

### Passo 5: Usar o Modelo em Produção

#### Fazer Predições em Batch

```python
import mlflow

# Carregar modelo
model = mlflow.sklearn.load_model("models:/company_churn_prediction/latest")

# Carregar dados
companies_df = spark.table("main.ticket_analytics.company_churn_training_data")

# Fazer predições
predictions = model.predict(companies_df.drop("is_churn_risk").toPandas())

# Salvar resultados
result_df = companies_df.select("company_id", "company_name")
result_df = result_df.withColumn("predicted_churn_risk", predictions)
result_df.write.format("delta").mode("overwrite").saveAsTable(
    "main.ticket_analytics.company_churn_predictions"
)
```

#### Criar Endpoint de Real-Time

1. Vá em **Machine Learning** > **Models**
2. Selecione `company_churn_prediction`
3. Clique em **Serve Model**
4. Configure o endpoint:
   - **Compute**: Small (1-2 cores)
   - **Scale**: 1-5 instâncias
5. Use a API:

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
        # ... outras features
    }]
}

response = requests.post(url, headers=headers, json=data)
prediction = response.json()
```

### Passo 6: Agendar Atualização Automática

1. Vá em **Workflows** > **Jobs**
2. Clique em **Create Job**
3. Configure:
   - **Task**: `feature_store_refresh_job`
   - **Notebook**: `notebooks/feature_store_refresh_job.py`
   - **Cluster**: Shared cluster ou job cluster
   - **Schedule**: Daily às 2:00 AM
   - **Parameters**:
     ```json
     {
       "refresh_mode": "incremental",
       "lookback_days": "7"
     }
     ```
4. Salve e ative o job

## 📊 Métricas de Features

### Features Mais Importantes (típicas)

1. **tickets_last_30_days**: Atividade recente
2. **sla_breach_rate**: Qualidade do serviço
3. **avg_nps_score**: Satisfação geral
4. **tickets_complaint**: Insatisfação explícita
5. **negative_sentiment_rate**: Sentimento negativo
6. **ticket_resolution_rate**: Eficiência
7. **days_since_last_ticket**: Engajamento
8. **tickets_churn_risk_tag**: Indicador direto

### Interpretação de Predições

| Score | Risco | Ação Recomendada |
|-------|-------|------------------|
| 0.0 - 0.3 | Baixo | Manter relacionamento padrão |
| 0.3 - 0.5 | Médio | Monitorar de perto |
| 0.5 - 0.7 | Alto | Contato proativo do CSM |
| 0.7 - 1.0 | Crítico | Intervenção urgente da liderança |

## 🔍 Monitoramento e Manutenção

### 1. Monitorar Feature Drift

```python
# Comparar distribuição de features ao longo do tempo
from databricks.feature_store import FeatureStoreClient

fs = FeatureStoreClient()

# Feature atual vs histórica
current = spark.table("main.ticket_analytics.company_churn_features")
historical = spark.table("main.ticket_analytics.company_churn_features@v100")

# Comparar estatísticas
current.select("avg_nps_score").summary().show()
historical.select("avg_nps_score").summary().show()
```

### 2. Monitorar Performance do Modelo

```python
# Calcular métricas em dados recentes
from sklearn.metrics import classification_report

recent_data = spark.table("main.ticket_analytics.company_churn_predictions") \
    .filter("prediction_timestamp > current_date() - interval 7 days")

# Comparar predições vs realidade
# (necessita de label de churn real após algumas semanas)
```

### 3. Retreinar o Modelo

Retreine quando:
- Accuracy cair > 5%
- Feature drift significativo
- Novos padrões de negócio
- A cada 3-6 meses (mínimo)

## 🛠️ Troubleshooting

### Erro: "Feature table already exists"

```python
# Deletar e recriar
spark.sql("DROP TABLE IF EXISTS main.ticket_analytics.company_churn_features")
# Execute o notebook novamente
```

### Erro: "Memory error during AutoML"

- Reduza o dataset: `training_df.sample(0.5)`
- Aumente o cluster size
- Reduza `max_trials` no AutoML

### Features com muitos valores nulos

```python
# Investigar features específicas
feature_df.select("avg_nps_score").filter(col("avg_nps_score").isNull()).count()

# Adicionar mais imputação no notebook
feature_df = feature_df.fillna({"avg_nps_score": 0})
```

## 📚 Próximos Passos

1. **Enriquecer Features**:
   - Adicionar dados de faturamento
   - Incluir uso do produto
   - Histórico de pagamentos

2. **Segmentação**:
   - Criar modelos específicos por segmento
   - Diferentes thresholds por company_size

3. **Explicabilidade**:
   - Usar SHAP values
   - Criar dashboards de interpretação

4. **Integração**:
   - Alertas automáticos no Slack/Email
   - Dashboard de risco de churn
   - CRM integration

## 📞 Suporte

Para dúvidas:
- Documentação Databricks: https://docs.databricks.com/
- Feature Store: https://docs.databricks.com/machine-learning/feature-store/
- AutoML: https://docs.databricks.com/machine-learning/automl/

---

**Criado por**: Fabio Gonçalves  
**Data**: Janeiro 2026  
**Versão**: 1.0
