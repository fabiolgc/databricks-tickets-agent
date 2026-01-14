"""
Data Generator for Customer Support Tickets - Payment Processing Company
Generates synthetic data for companies, customers, agents, tickets, and interactions
"""

import csv
import random
from datetime import datetime, timedelta
from faker import Faker
import uuid

# Initialize Faker for Brazilian Portuguese
fake = Faker('pt_BR')
Faker.seed(42)
random.seed(42)

# Configuration
NUM_COMPANIES = 100
NUM_CUSTOMERS = 300
NUM_AGENTS = 25
NUM_TICKETS = 500
AVG_INTERACTIONS_PER_TICKET = 4


def generate_cnpj():
    """Generate a valid-looking CNPJ"""
    return f"{random.randint(10, 99)}.{random.randint(100, 999)}.{random.randint(100, 999)}/{random.randint(1000, 9999)}-{random.randint(10, 99)}"


def generate_cpf():
    """Generate a valid-looking CPF"""
    return f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"


def generate_companies():
    """Generate company data"""
    companies = []
    segments = ['RETAIL', 'RESTAURANT', 'SERVICES', 'HEALTHCARE', 'EDUCATION', 'ECOMMERCE', 'AUTOMOTIVE', 'BEAUTY']
    sizes = ['SMALL', 'MEDIUM', 'LARGE', 'ENTERPRISE']
    statuses = ['ACTIVE'] * 85 + ['SUSPENDED'] * 10 + ['CANCELLED'] * 5
    
    for i in range(NUM_COMPANIES):
        company_id = f"COMP{str(i+1).zfill(5)}"
        contract_start = fake.date_between(start_date='-5y', end_date='-1m')
        
        companies.append({
            'company_id': company_id,
            'company_name': fake.company(),
            'cnpj': generate_cnpj(),
            'segment': random.choice(segments),
            'company_size': random.choice(sizes),
            'contract_start_date': contract_start.strftime('%Y-%m-%d'),
            'monthly_transaction_volume': round(random.uniform(5000, 5000000), 2),
            'status': random.choice(statuses),
            'churn_risk_score': round(random.uniform(0.01, 0.95), 2),
            'created_at': (contract_start - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return companies


def generate_customers(companies):
    """Generate customer data"""
    customers = []
    roles = ['OWNER', 'MANAGER', 'OPERATOR', 'FINANCIAL', 'IT_MANAGER']
    
    for i in range(NUM_CUSTOMERS):
        customer_id = f"CUST{str(i+1).zfill(5)}"
        company = random.choice(companies)
        
        customers.append({
            'customer_id': customer_id,
            'company_id': company['company_id'],
            'customer_name': fake.name(),
            'email': fake.email(),
            'cpf': generate_cpf(),
            'birth_date': fake.date_of_birth(minimum_age=25, maximum_age=65).strftime('%Y-%m-%d'),
            'phone': fake.phone_number(),
            'role': random.choice(roles),
            'created_at': company['created_at']
        })
    
    return customers


def generate_agents():
    """Generate agent data"""
    agents = []
    teams = ['L1_SUPPORT', 'L2_TECHNICAL', 'L3_SPECIALIST', 'FINANCIAL']
    specializations = ['POS_MACHINES', 'PIX', 'PAYMENTS', 'CHARGEBACKS', 'INTEGRATION', 'BILLING', 'GENERAL']
    
    agent_names = [
        'Ana Silva', 'Carlos Oliveira', 'Beatriz Santos', 'Diego Costa', 'Elena Rodrigues',
        'Fernando Lima', 'Gabriela Alves', 'Henrique Martins', 'Isabela Ferreira', 'João Pereira',
        'Karina Souza', 'Lucas Barbosa', 'Mariana Gomes', 'Nicolas Ribeiro', 'Olivia Carvalho',
        'Pedro Araújo', 'Rafaela Castro', 'Samuel Dias', 'Tatiana Mendes', 'Vinicius Rocha',
        'Wagner Teixeira', 'Yasmin Cardoso', 'Zeca Monteiro', 'Amanda Pinto', 'Bruno Cunha'
    ]
    
    for i, name in enumerate(agent_names):
        agent_id = f"AGENT{str(i+1).zfill(3)}"
        hire_date = fake.date_between(start_date='-3y', end_date='-6m')
        
        agents.append({
            'agent_id': agent_id,
            'agent_name': name,
            'email': f"{name.lower().replace(' ', '.')}@support.company.com",
            'team': random.choice(teams),
            'specialization': random.choice(specializations),
            'hire_date': hire_date.strftime('%Y-%m-%d'),
            'avg_csat': round(random.uniform(3.5, 4.9), 2),
            'tickets_resolved': random.randint(50, 1500),
            'status': 'ACTIVE',
            'created_at': hire_date.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return agents


def generate_tickets(companies, customers, agents):
    """Generate ticket data"""
    tickets = []
    
    statuses = ['OPEN', 'IN_PROGRESS', 'PENDING_CUSTOMER', 'RESOLVED', 'CLOSED']
    priorities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    channels = ['EMAIL', 'PHONE', 'CHAT', 'WHATSAPP', 'PORTAL']
    sentiments = ['POSITIVE', 'NEUTRAL', 'NEGATIVE', 'VERY_NEGATIVE']
    
    # Ticket templates for payment processing context
    ticket_templates = [
        {'category': 'TECHNICAL', 'subcategory': 'POS_NOT_WORKING', 'subject': 'Maquininha não está ligando', 
         'description': 'A maquininha de cartão modelo {} não está ligando. Tentei carregar a bateria mas não funciona.'},
        {'category': 'TECHNICAL', 'subcategory': 'CONNECTION_ERROR', 'subject': 'Erro de conexão com a máquina', 
         'description': 'Estou com problemas de conexão na maquininha. Aparece erro "Falha de comunicação" toda vez que tento processar um pagamento.'},
        {'category': 'TECHNICAL', 'subcategory': 'PIX_ERROR', 'subject': 'PIX não está funcionando', 
         'description': 'O pagamento via PIX não está processando. Cliente escaneou o QR Code mas o pagamento não foi aprovado.'},
        {'category': 'FINANCIAL', 'subcategory': 'CHARGEBACK', 'subject': 'Estorno indevido na conta', 
         'description': 'Foi realizado um estorno de R$ {} na minha conta sem autorização. Preciso entender o motivo e reverter.'},
        {'category': 'FINANCIAL', 'subcategory': 'MISSING_PAYMENT', 'subject': 'Pagamento não caiu na conta', 
         'description': 'Realizei vendas no dia {} no valor de R$ {} e o valor não foi creditado na minha conta.'},
        {'category': 'FINANCIAL', 'subcategory': 'WRONG_FEE', 'subject': 'Taxa cobrada incorretamente', 
         'description': 'A taxa cobrada nas transações está diferente do contratado. Contratei {} mas está sendo cobrado {}.'},
        {'category': 'COMMERCIAL', 'subcategory': 'PLAN_CHANGE', 'subject': 'Quero mudar de plano', 
         'description': 'Gostaria de informações sobre mudança de plano. Meu volume de vendas aumentou e preciso de condições melhores.'},
        {'category': 'COMMERCIAL', 'subcategory': 'CANCELLATION', 'subject': 'Solicitar cancelamento do serviço', 
         'description': 'Gostaria de cancelar meu contrato. Estou fechando a loja/mudando de adquirente.'},
        {'category': 'COMPLAINT', 'subcategory': 'POOR_SERVICE', 'subject': 'Insatisfação com atendimento', 
         'description': 'Estou muito insatisfeito com o atendimento. Já abri {} chamados e ninguém resolve meu problema.'},
        {'category': 'COMPLAINT', 'subcategory': 'SYSTEM_DOWN', 'subject': 'Sistema fora do ar há horas', 
         'description': 'O sistema está fora do ar desde as {}h e estou perdendo vendas. Preciso de solução urgente!'},
        {'category': 'INFORMATION', 'subcategory': 'HOW_TO', 'subject': 'Como fazer uma transação PIX?', 
         'description': 'Preciso de ajuda para configurar e processar pagamentos via PIX na maquininha.'},
        {'category': 'TECHNICAL', 'subcategory': 'UPDATE_NEEDED', 'subject': 'Solicitação de atualização da máquina', 
         'description': 'A maquininha está pedindo atualização mas não consigo fazer. Como proceder?'},
        {'category': 'FINANCIAL', 'subcategory': 'RECEIPT_ERROR', 'subject': 'Comprovante não foi emitido', 
         'description': 'Fiz uma venda de R$ {} mas o comprovante não foi impresso. Cliente está pedindo comprovante.'},
        {'category': 'TECHNICAL', 'subcategory': 'CARD_NOT_READING', 'subject': 'Máquina não lê o cartão', 
         'description': 'A leitora de cartão não está funcionando. Tentei limpar mas continua com problema.'},
        {'category': 'COMPLAINT', 'subcategory': 'LONG_WAIT', 'subject': 'Muito tempo de espera no suporte', 
         'description': 'Estou esperando há {} minutos para ser atendido. Isso é inaceitável!'},
    ]
    
    # Generate tickets concentrated in recent weeks
    today = datetime.now()
    
    for i in range(NUM_TICKETS):
        ticket_id = f"TKT{str(i+1).zfill(6)}"
        customer = random.choice(customers)
        company = next(c for c in companies if c['company_id'] == customer['company_id'])
        
        # More tickets in recent weeks
        days_ago = random.choices(
            range(1, 180), 
            weights=[100] * 14 + [50] * 30 + [20] * 60 + [5] * 75
        )[0]
        
        created_at = today - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        template = random.choice(ticket_templates)
        subject = template['subject']
        description = template['description']
        
        # Fill in placeholders in description
        placeholder_count = description.count('{}')
        if placeholder_count > 0:
            if 'dia' in description and placeholder_count == 2:
                past_date = (created_at - timedelta(days=random.randint(1, 5))).strftime('%d/%m/%Y')
                description = description.format(past_date, round(random.uniform(500, 10000), 2))
            elif 'taxa' in description.lower() and placeholder_count == 2:
                description = description.format('2.5%', '3.5%')
            elif 'R$' in description:
                description = description.format(round(random.uniform(100, 5000), 2))
            elif 'chamado' in description:
                description = description.format(random.randint(2, 5))
            elif 'horas' in description:
                description = description.format(random.randint(8, 18))
            elif 'minutos' in description:
                description = description.format(random.randint(30, 120))
            else:
                description = description.format('X900')
        
        status = random.choices(
            statuses,
            weights=[10, 15, 10, 30, 35]
        )[0]
        
        priority = random.choices(
            priorities,
            weights=[40, 35, 20, 5]
        )[0]
        
        agent = random.choice(agents) if status != 'OPEN' else None
        
        # Calculate times based on status
        resolution_time = None
        first_response_time = None
        closed_at = None
        updated_at = created_at + timedelta(hours=random.randint(1, 48))
        
        if status in ['RESOLVED', 'CLOSED']:
            resolution_time = round(random.uniform(0.5, 168), 2)  # up to 1 week
            first_response_time = random.randint(5, 240)
            closed_at = created_at + timedelta(hours=resolution_time)
        elif status in ['IN_PROGRESS', 'PENDING_CUSTOMER']:
            first_response_time = random.randint(5, 480)
        
        # SLA breach logic
        sla_hours = {'LOW': 48, 'MEDIUM': 24, 'HIGH': 8, 'CRITICAL': 4}
        sla_breached = False
        if resolution_time:
            sla_breached = resolution_time > sla_hours[priority]
        
        # NPS and CSAT for closed tickets
        nps_score = None
        csat_score = None
        if status == 'CLOSED':
            if random.random() < 0.7:  # 70% response rate
                nps_score = random.randint(0, 10)
                csat_score = round(random.uniform(1.0, 5.0), 2)
        
        # Sentiment based on category and priority
        if template['category'] == 'COMPLAINT' or priority == 'CRITICAL':
            sentiment = random.choice(['NEGATIVE', 'VERY_NEGATIVE'])
        elif template['category'] == 'INFORMATION':
            sentiment = random.choice(['POSITIVE', 'NEUTRAL'])
        else:
            sentiment = random.choice(sentiments)
        
        # Tags
        tags = [template['category'], template['subcategory']]
        if sla_breached:
            tags.append('SLA_BREACHED')
        if company['churn_risk_score'] > 0.6:
            tags.append('CHURN_RISK')
        if priority == 'CRITICAL':
            tags.append('URGENT')
        
        tickets.append({
            'ticket_id': ticket_id,
            'company_id': company['company_id'],
            'customer_id': customer['customer_id'],
            'agent_id': agent['agent_id'] if agent else '',
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'closed_at': closed_at.strftime('%Y-%m-%d %H:%M:%S') if closed_at else '',
            'status': status,
            'priority': priority,
            'category': template['category'],
            'subcategory': template['subcategory'],
            'channel': random.choice(channels),
            'subject': subject,
            'description': description,
            'tags': '|'.join(tags),
            'resolution_time_hours': resolution_time if resolution_time else '',
            'first_response_time_minutes': first_response_time if first_response_time else '',
            'sla_breached': str(sla_breached).upper(),
            'nps_score': nps_score if nps_score is not None else '',
            'csat_score': csat_score if csat_score else '',
            'sentiment': sentiment,
            'escalated': str(random.random() < 0.15).upper(),
            'reopened_count': random.choices([0, 1, 2], weights=[85, 12, 3])[0],
            'related_ticket_ids': ''
        })
    
    return tickets


def generate_interactions(tickets, customers, agents):
    """Generate ticket interaction history"""
    interactions = []
    
    agent_responses = [
        "Olá! Obrigado por entrar em contato. Já estou analisando seu caso.",
        "Entendo sua frustração. Vou verificar isso imediatamente para você.",
        "Consegui identificar o problema. Vou encaminhar para o time técnico.",
        "Já apliquei a correção. Poderia confirmar se está funcionando agora?",
        "Verifiquei seu cadastro e identifiquei a inconsistência. Vou corrigir.",
        "Essa solicitação precisa ser aprovada pelo gestor. Aguarde retorno em até 24h.",
        "Enviei as instruções por email. Por favor, siga o passo a passo.",
        "O problema está relacionado ao seu equipamento. Vou solicitar a troca.",
        "Realizei o estorno solicitado. O valor será creditado em até 2 dias úteis.",
        "Sua solicitação foi concluída com sucesso. Há mais algo em que posso ajudar?",
    ]
    
    customer_responses = [
        "Obrigado pelo retorno. Vou aguardar a solução.",
        "Mas isso já faz 3 dias que estou com problema! Preciso de agilidade!",
        "Ok, testei aqui e continua com o mesmo erro. O que fazer?",
        "Perfeito! Funcionou agora. Muito obrigado pelo suporte!",
        "Não consigo seguir essas instruções. Tem como fazer remotamente?",
        "Isso não resolve meu problema. Quero falar com um supervisor.",
        "Quanto tempo vai demorar? Estou perdendo vendas!",
        "Entendi. Vou aguardar o retorno então.",
        "Pode cancelar. Já resolvi de outra forma.",
        "Excelente atendimento! Problema resolvido.",
    ]
    
    for ticket in tickets:
        num_interactions = random.randint(2, 8)
        
        ticket_created = datetime.strptime(ticket['created_at'], '%Y-%m-%d %H:%M:%S')
        
        # First interaction is always the customer opening the ticket
        interactions.append({
            'interaction_id': f"INT{str(len(interactions)+1).zfill(8)}",
            'ticket_id': ticket['ticket_id'],
            'interaction_timestamp': ticket['created_at'],
            'author_type': 'CUSTOMER',
            'author_id': ticket['customer_id'],
            'author_name': next(c['customer_name'] for c in customers if c['customer_id'] == ticket['customer_id']),
            'message': ticket['description'],
            'interaction_type': 'COMMENT',
            'channel': ticket['channel'],
            'attachments': ''
        })
        
        # Subsequent interactions
        last_timestamp = ticket_created
        for j in range(1, num_interactions):
            is_agent = j % 2 == 1  # Alternate between agent and customer
            
            time_delta = timedelta(hours=random.uniform(0.5, 24))
            last_timestamp = last_timestamp + time_delta
            
            if is_agent and ticket['agent_id']:
                agent = next(a for a in agents if a['agent_id'] == ticket['agent_id'])
                interactions.append({
                    'interaction_id': f"INT{str(len(interactions)+1).zfill(8)}",
                    'ticket_id': ticket['ticket_id'],
                    'interaction_timestamp': last_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'author_type': 'AGENT',
                    'author_id': agent['agent_id'],
                    'author_name': agent['agent_name'],
                    'message': random.choice(agent_responses),
                    'interaction_type': 'COMMENT',
                    'channel': ticket['channel'],
                    'attachments': ''
                })
            else:
                customer = next(c for c in customers if c['customer_id'] == ticket['customer_id'])
                interactions.append({
                    'interaction_id': f"INT{str(len(interactions)+1).zfill(8)}",
                    'ticket_id': ticket['ticket_id'],
                    'interaction_timestamp': last_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'author_type': 'CUSTOMER',
                    'author_id': customer['customer_id'],
                    'author_name': customer['customer_name'],
                    'message': random.choice(customer_responses),
                    'interaction_type': 'COMMENT',
                    'channel': ticket['channel'],
                    'attachments': ''
                })
        
        # Final closure message for closed tickets
        if ticket['status'] == 'CLOSED' and ticket['agent_id']:
            agent = next(a for a in agents if a['agent_id'] == ticket['agent_id'])
            interactions.append({
                'interaction_id': f"INT{str(len(interactions)+1).zfill(8)}",
                'ticket_id': ticket['ticket_id'],
                'interaction_timestamp': ticket['closed_at'],
                'author_type': 'AGENT',
                'author_id': agent['agent_id'],
                'author_name': agent['agent_name'],
                'message': "Ticket resolvido e encerrado. Obrigado!",
                'interaction_type': 'STATUS_CHANGE',
                'channel': ticket['channel'],
                'attachments': ''
            })
    
    return interactions


def save_to_csv(data, filename, fieldnames):
    """Save data to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"✓ Generated {filename} with {len(data)} records")


def main():
    print("Generating synthetic data for Customer Support Tickets...\n")
    
    # Generate data
    print("Generating companies...")
    companies = generate_companies()
    
    print("Generating customers...")
    customers = generate_customers(companies)
    
    print("Generating agents...")
    agents = generate_agents()
    
    print("Generating tickets...")
    tickets = generate_tickets(companies, customers, agents)
    
    print("Generating interactions...")
    interactions = generate_interactions(tickets, customers, agents)
    
    print("\nSaving to CSV files...\n")
    
    # Save to CSV
    save_to_csv(companies, 'companies.csv', [
        'company_id', 'company_name', 'cnpj', 'segment', 'company_size', 
        'contract_start_date', 'monthly_transaction_volume', 'status', 
        'churn_risk_score', 'created_at'
    ])
    
    save_to_csv(customers, 'customers.csv', [
        'customer_id', 'company_id', 'customer_name', 'email', 'cpf', 
        'birth_date', 'phone', 'role', 'created_at'
    ])
    
    save_to_csv(agents, 'agents.csv', [
        'agent_id', 'agent_name', 'email', 'team', 'specialization', 
        'hire_date', 'avg_csat', 'tickets_resolved', 'status', 'created_at'
    ])
    
    save_to_csv(tickets, 'tickets.csv', [
        'ticket_id', 'company_id', 'customer_id', 'agent_id', 'created_at', 
        'updated_at', 'closed_at', 'status', 'priority', 'category', 'subcategory', 
        'channel', 'subject', 'description', 'tags', 'resolution_time_hours', 
        'first_response_time_minutes', 'sla_breached', 'nps_score', 'csat_score', 
        'sentiment', 'escalated', 'reopened_count', 'related_ticket_ids'
    ])
    
    save_to_csv(interactions, 'ticket_interactions.csv', [
        'interaction_id', 'ticket_id', 'interaction_timestamp', 'author_type', 
        'author_id', 'author_name', 'message', 'interaction_type', 'channel', 'attachments'
    ])
    
    print("\n" + "="*60)
    print("Data generation completed successfully!")
    print("="*60)
    print(f"Companies: {len(companies)}")
    print(f"Customers: {len(customers)}")
    print(f"Agents: {len(agents)}")
    print(f"Tickets: {len(tickets)}")
    print(f"Interactions: {len(interactions)}")
    print("="*60)


if __name__ == '__main__':
    main()
