# Quick Start Guide - Databricks Tickets Agent

## 🚀 Resumo Rápido

Este projeto fornece uma base de dados completa para demonstração de agente GenAI de análise de tickets de suporte ao cliente.

### Arquivos Gerados

```
✓ 5 arquivos CSV com dados sintéticos:
  - companies.csv (100 empresas)
  - customers.csv (300 clientes)
  - agents.csv (25 agentes)
  - tickets.csv (500 tickets)
  - ticket_interactions.csv (2,649 interações)

✓ Scripts SQL:
  - ddl_tables.sql (criação das tabelas Delta)
  - load_data.sql (importação dos dados)
  - analysis_queries.sql (queries de análise)

✓ Código Python:
  - generate_data.py (gerador de dados)
  - genai_agent_example.py (notebook exemplo)
```

## 📋 Passo a Passo - 5 Minutos

### 1. Criar as Tabelas (1 min)

No Databricks SQL Editor:

```sql
-- Cole e execute o conteúdo de ddl_tables.sql
-- Isso criará 5 tabelas: companies, customers, agents, tickets, ticket_interactions
```

### 2. Upload dos CSVs (2 min)

**Opção A - Via Interface do Databricks:**
1. Acesse: Data → Add Data → Upload File
2. Faça upload de todos os 5 arquivos CSV
3. Anote o caminho onde foram salvos (ex: `/FileStore/tables/`)

**Opção B - Via Databricks CLI:**
```bash
databricks fs cp *.csv dbfs:/FileStore/tickets/ --recursive
```

### 3. Carregar os Dados (2 min)

No Databricks SQL Editor, ajuste os caminhos e execute:

```sql
-- Carrega companies
COPY INTO companies
FROM '/FileStore/tickets/companies.csv'  -- Ajuste o caminho!
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');

-- Carrega agents
COPY INTO agents
FROM '/FileStore/tickets/agents.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');

-- Carrega customers
COPY INTO customers
FROM '/FileStore/tickets/customers.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');

-- Carrega tickets
COPY INTO tickets
FROM '/FileStore/tickets/tickets.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');

-- Carrega interactions
COPY INTO ticket_interactions
FROM '/FileStore/tickets/ticket_interactions.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'false');
```

### 4. Verificar os Dados

```sql
-- Conta registros em cada tabela
SELECT 'companies' AS table_name, COUNT(*) AS records FROM companies
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'agents', COUNT(*) FROM agents
UNION ALL
SELECT 'tickets', COUNT(*) FROM tickets
UNION ALL
SELECT 'ticket_interactions', COUNT(*) FROM ticket_interactions;
```

Resultado esperado:
- companies: 100
- customers: 300
- agents: 25
- tickets: 500
- ticket_interactions: 2,649

## 🎯 Primeiras Queries - Teste Agora!

### "O que está acontecendo esta semana?"

```sql
SELECT 
    COUNT(*) AS total_tickets,
    COUNT(CASE WHEN status = 'OPEN' THEN 1 END) AS open,
    COUNT(CASE WHEN priority = 'CRITICAL' THEN 1 END) AS critical,
    ROUND(AVG(csat_score), 2) AS avg_satisfaction
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS;
```

### "Quais são os principais problemas?"

```sql
SELECT 
    category,
    subcategory,
    COUNT(*) AS total,
    ROUND(AVG(resolution_time_hours), 2) AS avg_hours
FROM tickets
WHERE created_at >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY category, subcategory
ORDER BY total DESC
LIMIT 10;
```

### "Empresas em risco de churn?"

```sql
SELECT 
    c.company_name,
    c.churn_risk_score,
    COUNT(t.ticket_id) AS recent_tickets,
    AVG(t.csat_score) AS satisfaction
FROM companies c
LEFT JOIN tickets t ON c.company_id = t.company_id
WHERE c.churn_risk_score > 0.6
    AND t.created_at >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY c.company_name, c.churn_risk_score
ORDER BY c.churn_risk_score DESC;
```

## 🤖 Exemplo de Agente GenAI

Importe o notebook `genai_agent_example.py` no Databricks e execute.

O notebook demonstra:
- ✅ Sumarização inteligente de tickets
- ✅ Análise de tendências
- ✅ Detecção de risco de churn
- ✅ Recomendação de ações
- ✅ Relatório executivo automatizado

## 📊 Casos de Uso Demonstrados

### 1. Análise Executiva
"Gere um resumo semanal dos tickets"

### 2. Identificação de Problemas
"Quais categorias têm mais reclamações?"

### 3. Risco de Churn
"Quais clientes estão insatisfeitos?"

### 4. Performance do Time
"Como está o desempenho dos agentes?"

### 5. SLA Monitoring
"Quantos tickets violaram o SLA?"

### 6. Next Best Action
"Qual a melhor solução baseada em tickets similares?"

## 🎨 Criando um Dashboard

No Databricks SQL, crie visualizações:

1. **KPIs principais**: Total de tickets, taxa de resolução, CSAT médio
2. **Gráfico de tendências**: Tickets por dia/semana
3. **Distribuição por categoria**: Gráfico de pizza
4. **SLA compliance**: Gráfico de barras por prioridade
5. **Sentiment analysis**: Timeline de sentimentos
6. **Churn risk**: Top 10 empresas em risco

## 🔐 Governança de Dados (PII)

Os campos marcados como PII nas tabelas:

**companies**: `cnpj`
**customers**: `customer_name`, `email`, `cpf`, `birth_date`, `phone`

Para aplicar máscaras no Unity Catalog:

```sql
-- Exemplo: Máscara de CPF
CREATE FUNCTION mask_cpf(cpf STRING)
RETURNS STRING
RETURN CONCAT('***.', SUBSTRING(cpf, 5, 3), '.', SUBSTRING(cpf, 9, 3), '-**');

-- Aplicar em uma view
CREATE VIEW customers_masked AS
SELECT 
    customer_id,
    customer_name,
    mask_cpf(cpf) as cpf,
    email,
    role
FROM customers;
```

## 🚨 Troubleshooting

### Erro: "Table not found"
- Verifique se executou o `ddl_tables.sql` completo
- Confirme o nome do schema/database correto

### Erro: "File not found"
- Verifique o caminho dos CSVs no DBFS
- Use `%fs ls /FileStore/tickets/` para listar arquivos

### Erro: "Foreign key violation"
- Carregue as tabelas na ordem correta:
  1. companies, agents
  2. customers
  3. tickets
  4. ticket_interactions

### Dados não aparecem
- Execute: `REFRESH TABLE nome_da_tabela`
- Verifique se o COPY INTO foi executado com sucesso

## 📚 Documentação Adicional

- **README.md**: Documentação completa do projeto
- **analysis_queries.sql**: 50+ queries prontas para análise
- **genai_agent_example.py**: Notebook completo com exemplos

## 🎓 Próximos Passos

1. ✅ **Dados carregados** → Explore as queries de análise
2. 🤖 **Teste o notebook** → Execute genai_agent_example.py
3. 📊 **Crie dashboards** → Use Databricks SQL Dashboards
4. 🧠 **Implemente AI** → Use AI Functions (ai_summarize, ai_classify)
5. 🔍 **Vector Search** → Busca semântica de tickets similares
6. 🚀 **Deploy Agente** → Databricks Model Serving + Lakehouse Apps

## 💡 Dicas para a Demonstração

1. **Comece com o problema**: "Gestor quer saber o que está acontecendo sem ler 500 tickets"
2. **Mostre dados reais**: Tickets em português, contexto de pagamentos
3. **Demonstre IA**: Sumarização, classificação, recomendações
4. **Destaque insights**: Churn risk, SLA breaches, sentiment trends
5. **Governança**: Mostre tags PII e Unity Catalog
6. **Escalabilidade**: Delta Lake, Z-ordering, otimizações

## 🤝 Suporte

Para dúvidas sobre este projeto, entre em contato com seu Arquiteto de Soluções Databricks.

---

**Tempo total de setup: ~5 minutos** ⚡
**Pronto para demonstrar!** 🎯
