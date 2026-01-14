"""
Data Generator for Customer Support Tickets - Payment Processing Company (English Version)
Generates synthetic data for companies, customers, agents, tickets, and interactions
"""

import csv
import random
from datetime import datetime, timedelta
from faker import Faker
import uuid

# Initialize Faker for US English
fake = Faker('en_US')
Faker.seed(42)
random.seed(42)

# Configuration
NUM_COMPANIES = 100
NUM_CUSTOMERS = 300
NUM_AGENTS = 25
NUM_TICKETS = 500
AVG_INTERACTIONS_PER_TICKET = 4


def generate_ein():
    """Generate a valid-looking EIN (Employer Identification Number)"""
    return f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"


def generate_ssn():
    """Generate a valid-looking SSN"""
    return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"


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
            'tax_id': generate_ein(),
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
            'ssn': generate_ssn(),
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
    specializations = ['POS_TERMINALS', 'MOBILE_PAYMENTS', 'PAYMENT_PROCESSING', 'CHARGEBACKS', 'INTEGRATION', 'BILLING', 'GENERAL']
    
    agent_names = [
        'Sarah Johnson', 'Michael Chen', 'Emily Rodriguez', 'David Kim', 'Jennifer Martinez',
        'Robert Taylor', 'Amanda White', 'Christopher Lee', 'Jessica Brown', 'Daniel Garcia',
        'Maria Lopez', 'James Wilson', 'Michelle Anderson', 'Kevin Thomas', 'Laura Martinez',
        'Brian Jackson', 'Nicole Harris', 'Ryan Clark', 'Ashley Lewis', 'Matthew Robinson',
        'Stephanie Walker', 'Justin Hall', 'Rachel Allen', 'Andrew Young', 'Melissa King'
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
    channels = ['EMAIL', 'PHONE', 'CHAT', 'LIVE_CHAT', 'PORTAL']
    sentiments = ['POSITIVE', 'NEUTRAL', 'NEGATIVE', 'VERY_NEGATIVE']
    
    # Ticket templates for payment processing context (English)
    ticket_templates = [
        {'category': 'TECHNICAL', 'subcategory': 'TERMINAL_NOT_WORKING', 'subject': 'Payment terminal not turning on', 
         'description': 'The payment terminal model {} is not powering on. I tried charging the battery but it still does not work.'},
        {'category': 'TECHNICAL', 'subcategory': 'CONNECTION_ERROR', 'subject': 'Connection error with terminal', 
         'description': 'I am experiencing connection problems with the terminal. It shows "Communication failure" error every time I try to process a payment.'},
        {'category': 'TECHNICAL', 'subcategory': 'MOBILE_PAYMENT_ERROR', 'subject': 'Mobile payment not working', 
         'description': 'Mobile payment is not processing. Customer scanned the QR code but the payment was not approved.'},
        {'category': 'FINANCIAL', 'subcategory': 'CHARGEBACK', 'subject': 'Unauthorized chargeback on account', 
         'description': 'A chargeback of ${} was made to my account without authorization. I need to understand the reason and reverse it.'},
        {'category': 'FINANCIAL', 'subcategory': 'MISSING_PAYMENT', 'subject': 'Payment not deposited to account', 
         'description': 'I made sales on {} totaling ${} and the amount was not credited to my account.'},
        {'category': 'FINANCIAL', 'subcategory': 'WRONG_FEE', 'subject': 'Incorrect fee charged', 
         'description': 'The fee charged on transactions is different from what was contracted. I contracted {} but am being charged {}.'},
        {'category': 'COMMERCIAL', 'subcategory': 'PLAN_CHANGE', 'subject': 'Want to change service plan', 
         'description': 'I would like information about changing plans. My sales volume has increased and I need better rates.'},
        {'category': 'COMMERCIAL', 'subcategory': 'CANCELLATION', 'subject': 'Request service cancellation', 
         'description': 'I would like to cancel my contract. I am closing my store/switching to another provider.'},
        {'category': 'COMPLAINT', 'subcategory': 'POOR_SERVICE', 'subject': 'Dissatisfied with service', 
         'description': 'I am very dissatisfied with the service. I have opened {} tickets and no one has solved my problem.'},
        {'category': 'COMPLAINT', 'subcategory': 'SYSTEM_DOWN', 'subject': 'System down for hours', 
         'description': 'The system has been down since {}am and I am losing sales. I need an urgent solution!'},
        {'category': 'INFORMATION', 'subcategory': 'HOW_TO', 'subject': 'How to process a mobile payment?', 
         'description': 'I need help configuring and processing mobile payments on the terminal.'},
        {'category': 'TECHNICAL', 'subcategory': 'UPDATE_NEEDED', 'subject': 'Terminal update request', 
         'description': 'The terminal is asking for an update but I cannot do it. How do I proceed?'},
        {'category': 'FINANCIAL', 'subcategory': 'RECEIPT_ERROR', 'subject': 'Receipt not printed', 
         'description': 'I made a sale of ${} but the receipt was not printed. Customer is asking for a receipt.'},
        {'category': 'TECHNICAL', 'subcategory': 'CARD_NOT_READING', 'subject': 'Terminal not reading card', 
         'description': 'The card reader is not working. I tried cleaning it but the problem persists.'},
        {'category': 'COMPLAINT', 'subcategory': 'LONG_WAIT', 'subject': 'Too long wait time for support', 
         'description': 'I have been waiting for {} minutes to be served. This is unacceptable!'},
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
            if 'on' in description and 'totaling' in description and placeholder_count == 2:
                past_date = (created_at - timedelta(days=random.randint(1, 5))).strftime('%m/%d/%Y')
                description = description.format(past_date, round(random.uniform(500, 10000), 2))
            elif 'contracted' in description and placeholder_count == 2:
                description = description.format('2.5%', '3.5%')
            elif '$' in description:
                description = description.format(round(random.uniform(100, 5000), 2))
            elif 'tickets' in description:
                description = description.format(random.randint(2, 5))
            elif 'since' in description:
                description = description.format(random.randint(8, 18))
            elif 'minutes' in description:
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
            resolution_time = round(random.uniform(0.5, 168), 2)
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
            if random.random() < 0.7:
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
        "Hello! Thank you for contacting us. I'm already looking into your case.",
        "I understand your frustration. I will check this immediately for you.",
        "I was able to identify the problem. I will forward it to the technical team.",
        "I have applied the fix. Could you confirm if it is working now?",
        "I checked your registration and identified the inconsistency. I will correct it.",
        "This request needs to be approved by the manager. Please wait for a response within 24 hours.",
        "I sent the instructions by email. Please follow the step-by-step guide.",
        "The problem is related to your equipment. I will request a replacement.",
        "I have processed the requested refund. The amount will be credited within 2 business days.",
        "Your request has been completed successfully. Is there anything else I can help you with?",
    ]
    
    customer_responses = [
        "Thank you for the response. I will wait for the solution.",
        "But it has been 3 days since I have had this problem! I need speed!",
        "Ok, I tested it and it still has the same error. What should I do?",
        "Perfect! It worked now. Thank you very much for the support!",
        "I cannot follow these instructions. Can you do it remotely?",
        "This does not solve my problem. I want to speak with a supervisor.",
        "How long will it take? I am losing sales!",
        "Understood. I will wait for the response then.",
        "You can cancel. I already solved it another way.",
        "Excellent service! Problem solved.",
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
            is_agent = j % 2 == 1
            
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
                'message': "Ticket resolved and closed. Thank you!",
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
    print("Generating synthetic data for Customer Support Tickets (English)...\n")
    
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
    
    # Save to CSV with _en suffix
    save_to_csv(companies, 'companies_en.csv', [
        'company_id', 'company_name', 'tax_id', 'segment', 'company_size', 
        'contract_start_date', 'monthly_transaction_volume', 'status', 
        'churn_risk_score', 'created_at'
    ])
    
    save_to_csv(customers, 'customers_en.csv', [
        'customer_id', 'company_id', 'customer_name', 'email', 'ssn', 
        'birth_date', 'phone', 'role', 'created_at'
    ])
    
    save_to_csv(agents, 'agents_en.csv', [
        'agent_id', 'agent_name', 'email', 'team', 'specialization', 
        'hire_date', 'avg_csat', 'tickets_resolved', 'status', 'created_at'
    ])
    
    save_to_csv(tickets, 'tickets_en.csv', [
        'ticket_id', 'company_id', 'customer_id', 'agent_id', 'created_at', 
        'updated_at', 'closed_at', 'status', 'priority', 'category', 'subcategory', 
        'channel', 'subject', 'description', 'tags', 'resolution_time_hours', 
        'first_response_time_minutes', 'sla_breached', 'nps_score', 'csat_score', 
        'sentiment', 'escalated', 'reopened_count', 'related_ticket_ids'
    ])
    
    save_to_csv(interactions, 'ticket_interactions_en.csv', [
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
