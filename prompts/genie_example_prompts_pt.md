# Databricks Genie - Example Prompts for Tickets Agent

## 📘 About Genie

Databricks Genie is an AI-powered analyst that lets you query your data using natural language. After setting up your tables, you can create a Genie Space and ask questions directly.

## 🎯 Setup Genie Space

1. In Databricks, go to **Genie** in the left menu
2. Click **Create Space**
3. Select your tables: `companies`, `customers`, `agents`, `tickets`, `ticket_interactions`
4. Name it: "Customer Support Tickets Analysis"
5. Add description: "AI agent for analyzing customer support tickets from a payment processing company"

## 💬 Example Prompts - Portuguese

### Análise Executiva

```
Mostre um resumo dos tickets da última semana
```

```
Quantos tickets críticos temos abertos agora?
```

```
Qual a satisfação média dos clientes este mês?
```

```
Mostre a taxa de resolução de tickets por prioridade
```

### Identificação de Problemas

```
Quais são os 5 problemas mais comuns neste mês?
```

```
Mostre as categorias de ticket com pior CSAT
```

```
Quais subcategorias têm mais tickets críticos?
```

```
Liste os tickets que violaram SLA esta semana
```

### Análise de Churn

```
Quais empresas estão em alto risco de churn?
```

```
Mostre empresas com mais de 5 reclamações no último mês
```

```
Liste clientes com NPS baixo (detratores) esta semana
```

```
Quais empresas têm muitos tickets urgentes sem resolver?
```

### Performance do Time

```
Qual agente tem melhor CSAT médio?
```

```
Mostre o tempo médio de resolução por agente
```

```
Qual time tem mais violações de SLA?
```

```
Liste os agentes com mais tickets resolvidos este mês
```

### Análise Temporal

```
Mostre a tendência de tickets nos últimos 3 meses
```

```
Compare o volume de tickets desta semana com a semana passada
```

```
Qual dia da semana tem mais tickets abertos?
```

```
Mostre a evolução do NPS nos últimos 60 dias
```

### Análise por Canal

```
Qual canal tem o melhor tempo de resposta?
```

```
Compare a satisfação entre os canais de atendimento
```

```
Quantos tickets chegam por WhatsApp vs Email?
```

### Análise de Sentimento

```
Mostre a distribuição de sentimento dos tickets este mês
```

```
Quantos tickets têm sentimento muito negativo?
```

```
Compare sentimento por categoria de ticket
```

### Análise de Empresas

```
Qual segmento de negócio abre mais tickets?
```

```
Mostre empresas grandes com baixa satisfação
```

```
Liste as 10 empresas com maior volume de transação que têm tickets abertos
```

## 💬 Example Prompts - English

### Executive Analysis

```
Show me a summary of tickets from last week
```

```
How many critical tickets are currently open?
```

```
What's the average customer satisfaction this month?
```

```
Show ticket resolution rate by priority
```

### Problem Identification

```
What are the top 5 most common issues this month?
```

```
Show ticket categories with worst CSAT scores
```

```
Which subcategories have the most critical tickets?
```

```
List tickets that breached SLA this week
```

### Churn Analysis

```
Which companies are at high risk of churn?
```

```
Show companies with more than 5 complaints last month
```

```
List customers with low NPS (detractors) this week
```

```
Which companies have many urgent unresolved tickets?
```

### Team Performance

```
Which agent has the best average CSAT?
```

```
Show average resolution time by agent
```

```
Which team has the most SLA violations?
```

```
List agents with most tickets resolved this month
```

### Trend Analysis

```
Show ticket trends over the last 3 months
```

```
Compare this week's ticket volume with last week
```

```
Which day of the week has the most tickets opened?
```

```
Show NPS evolution over the last 60 days
```

### Channel Analysis

```
Which channel has the best response time?
```

```
Compare satisfaction across support channels
```

```
How many tickets come through WhatsApp vs Email?
```

### Sentiment Analysis

```
Show sentiment distribution of tickets this month
```

```
How many tickets have very negative sentiment?
```

```
Compare sentiment by ticket category
```

### Company Analysis

```
Which business segment opens the most tickets?
```

```
Show large companies with low satisfaction
```

```
List top 10 companies by transaction volume that have open tickets
```

## 🎨 Advanced Analysis Prompts

### Cross-functional Analysis

```
Mostre empresas do segmento RETAIL com churn risk acima de 0.7 e mais de 3 tickets urgentes
```

```
Liste tickets críticos de empresas LARGE que ainda não têm agente atribuído
```

```
Qual a correlação entre tempo de resolução e satisfação do cliente?
```

### Predictive Insights

```
Quais empresas provavelmente vão cancelar baseado em tickets recentes?
```

```
Identifique padrões em tickets que levam a escalações
```

```
Mostre tickets reabertos múltiplas vezes - há um padrão?
```

### Root Cause Analysis

```
Por que temos tantos tickets de PIX esta semana?
```

```
Quais problemas técnicos estão causando mais insatisfação?
```

```
Identifique a causa raiz dos tickets com pior NPS
```

### Action-oriented Queries

```
Quais tickets críticos precisam de atenção imediata?
```

```
Recomende ações para reduzir violações de SLA
```

```
Identifique gargalos no processo de atendimento
```

```
Quais clientes devemos contactar proativamente hoje?
```

## 🧠 Tips for Better Genie Queries

### ✅ DO

- Use natural, conversational language
- Be specific about time periods
- Ask for comparisons and trends
- Request visual outputs (charts, tables)
- Combine multiple dimensions

### ❌ DON'T

- Don't use technical SQL syntax
- Avoid ambiguous terms
- Don't ask multiple unrelated questions at once
- Avoid asking for data not in the tables

## 📊 Expected Outputs

Genie can return:
- **Tables**: Structured data results
- **Charts**: Bar charts, line graphs, pie charts
- **Metrics**: Single numbers with context
- **Insights**: AI-generated observations
- **Recommendations**: Suggested actions

## 🔄 Follow-up Questions

After Genie responds, you can ask follow-ups:

```
Initial: "Mostre tickets críticos abertos"
Follow-up: "Filtre apenas os do segmento RETAIL"
Follow-up: "Mostre o histórico de interações desses tickets"
Follow-up: "Qual agente seria melhor para cada um?"
```

## 🎯 Demo Script

**Start with context:**
> "Sou um gestor de suporte ao cliente e quero entender o que está acontecendo esta semana sem ler centenas de tickets."

**Progressive discovery:**
1. "Mostre um resumo dos tickets desta semana"
2. "Quais são os principais problemas?"
3. "Mostre empresas em risco de churn"
4. "Qual a performance do time de atendimento?"
5. "Recomende 3 ações prioritárias"

**Address specific concerns:**
> "Temos muitas reclamações sobre PIX. Mostre análise detalhada."

**Proactive management:**
> "Identifique clientes que devemos contactar hoje para evitar churn."

## 🚀 Integration with AI Functions

Genie can also trigger AI functions:

```
Resuma as conversas dos 10 tickets mais complexos desta semana
```

```
Classifique automaticamente tickets não categorizados
```

```
Gere um relatório executivo em formato de apresentação
```

## 📈 Business Value Demonstration

Show how Genie saves time:

**Traditional approach:**
- Write SQL queries (20 min)
- Export to Excel (5 min)
- Create visualizations (15 min)
- Write summary (10 min)
- **Total: 50 minutes**

**With Genie:**
- Ask in natural language (30 seconds)
- Get instant results with charts
- AI-generated insights included
- **Total: 30 seconds**

**ROI: 100x faster!** ⚡

## 🎓 Teaching Genie About Your Business

Add context to your Genie Space:

**Instructions for Genie:**
```
Context: This is a payment processing company similar to Cielo in Brazil. 
Customers use POS machines to accept credit cards, debit cards, and PIX payments.

Important definitions:
- CRITICAL priority: Must be resolved in 4 hours
- HIGH priority: Must be resolved in 8 hours
- Churn risk > 0.7 is considered high risk
- CSAT >= 4.0 is considered satisfied
- NPS 9-10 = Promoter, 7-8 = Passive, 0-6 = Detractor

Business priorities:
1. Prevent churn of high-value customers
2. Maintain SLA compliance > 95%
3. Keep CSAT above 4.0
4. Resolve critical issues within SLA
```

This helps Genie understand your specific business context!

---

**Ready to ask your first question?** 🎤
