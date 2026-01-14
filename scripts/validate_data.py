"""
Data Validation Script
Validates the generated CSV files and produces statistics report
"""

import csv
from collections import Counter
from datetime import datetime

def read_csv(filename):
    """Read CSV file and return rows"""
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def validate_data():
    """Validate all generated data and produce report"""
    
    print("="*70)
    print("DATA VALIDATION REPORT")
    print("="*70)
    print()
    
    # Load all data
    companies = read_csv('companies.csv')
    customers = read_csv('customers.csv')
    agents = read_csv('agents.csv')
    tickets = read_csv('tickets.csv')
    interactions = read_csv('ticket_interactions.csv')
    
    # Basic counts
    print("📊 RECORD COUNTS")
    print("-" * 70)
    print(f"Companies:           {len(companies):>6}")
    print(f"Customers:           {len(customers):>6}")
    print(f"Agents:              {len(agents):>6}")
    print(f"Tickets:             {len(tickets):>6}")
    print(f"Ticket Interactions: {len(interactions):>6}")
    print()
    
    # Ticket statistics
    print("🎫 TICKET STATISTICS")
    print("-" * 70)
    
    statuses = Counter(t['status'] for t in tickets)
    print("Status Distribution:")
    for status, count in statuses.most_common():
        pct = count * 100.0 / len(tickets)
        print(f"  {status:20} {count:>4} ({pct:>5.1f}%)")
    print()
    
    priorities = Counter(t['priority'] for t in tickets)
    print("Priority Distribution:")
    for priority, count in priorities.most_common():
        pct = count * 100.0 / len(tickets)
        print(f"  {priority:20} {count:>4} ({pct:>5.1f}%)")
    print()
    
    categories = Counter(t['category'] for t in tickets)
    print("Category Distribution:")
    for category, count in categories.most_common():
        pct = count * 100.0 / len(tickets)
        print(f"  {category:20} {count:>4} ({pct:>5.1f}%)")
    print()
    
    channels = Counter(t['channel'] for t in tickets)
    print("Channel Distribution:")
    for channel, count in channels.most_common():
        pct = count * 100.0 / len(tickets)
        print(f"  {channel:20} {count:>4} ({pct:>5.1f}%)")
    print()
    
    # Calculate averages
    closed_tickets = [t for t in tickets if t['status'] in ['RESOLVED', 'CLOSED']]
    if closed_tickets:
        avg_resolution = sum(float(t['resolution_time_hours']) for t in closed_tickets 
                           if t['resolution_time_hours']) / len(closed_tickets)
        print(f"Average Resolution Time: {avg_resolution:.2f} hours")
        
        tickets_with_csat = [t for t in tickets if t['csat_score']]
        if tickets_with_csat:
            avg_csat = sum(float(t['csat_score']) for t in tickets_with_csat) / len(tickets_with_csat)
            print(f"Average CSAT Score:      {avg_csat:.2f} / 5.0")
        
        tickets_with_nps = [t for t in tickets if t['nps_score']]
        if tickets_with_nps:
            avg_nps = sum(float(t['nps_score']) for t in tickets_with_nps) / len(tickets_with_nps)
            print(f"Average NPS Score:       {avg_nps:.1f} / 10")
    
    sla_breached = sum(1 for t in tickets if t['sla_breached'] == 'TRUE')
    print(f"SLA Breaches:            {sla_breached} ({sla_breached*100.0/len(tickets):.1f}%)")
    print()
    
    # Company statistics
    print("🏢 COMPANY STATISTICS")
    print("-" * 70)
    
    segments = Counter(c['segment'] for c in companies)
    print("Segment Distribution:")
    for segment, count in segments.most_common():
        pct = count * 100.0 / len(companies)
        print(f"  {segment:20} {count:>4} ({pct:>5.1f}%)")
    print()
    
    high_churn = sum(1 for c in companies if float(c['churn_risk_score']) > 0.6)
    print(f"High Churn Risk (>0.6):  {high_churn} companies ({high_churn*100.0/len(companies):.1f}%)")
    print()
    
    # Agent statistics
    print("👥 AGENT STATISTICS")
    print("-" * 70)
    
    teams = Counter(a['team'] for a in agents)
    print("Team Distribution:")
    for team, count in teams.most_common():
        print(f"  {team:20} {count:>4} agents")
    print()
    
    # Ticket assignment
    assigned_tickets = sum(1 for t in tickets if t['agent_id'])
    print(f"Tickets Assigned:        {assigned_tickets} ({assigned_tickets*100.0/len(tickets):.1f}%)")
    print(f"Tickets Unassigned:      {len(tickets)-assigned_tickets}")
    print()
    
    # Interaction statistics
    print("💬 INTERACTION STATISTICS")
    print("-" * 70)
    
    avg_interactions = len(interactions) / len(tickets)
    print(f"Average Interactions per Ticket: {avg_interactions:.1f}")
    
    author_types = Counter(i['author_type'] for i in interactions)
    print("\nInteraction Author Types:")
    for author_type, count in author_types.most_common():
        pct = count * 100.0 / len(interactions)
        print(f"  {author_type:20} {count:>5} ({pct:>5.1f}%)")
    print()
    
    # Data quality checks
    print("✅ DATA QUALITY CHECKS")
    print("-" * 70)
    
    # Check foreign keys
    company_ids = set(c['company_id'] for c in companies)
    customer_company_ids = set(c['company_id'] for c in customers)
    ticket_company_ids = set(t['company_id'] for t in tickets)
    
    invalid_customer_fk = len(customer_company_ids - company_ids)
    invalid_ticket_fk = len(ticket_company_ids - company_ids)
    
    print(f"✓ Company FK in customers:  {'OK' if invalid_customer_fk == 0 else f'ERROR: {invalid_customer_fk} invalid'}")
    print(f"✓ Company FK in tickets:    {'OK' if invalid_ticket_fk == 0 else f'ERROR: {invalid_ticket_fk} invalid'}")
    
    # Check required fields
    tickets_no_subject = sum(1 for t in tickets if not t['subject'])
    tickets_no_desc = sum(1 for t in tickets if not t['description'])
    
    print(f"✓ Tickets with subject:     {'OK' if tickets_no_subject == 0 else f'ERROR: {tickets_no_subject} missing'}")
    print(f"✓ Tickets with description: {'OK' if tickets_no_desc == 0 else f'ERROR: {tickets_no_desc} missing'}")
    
    # Check date consistency
    date_errors = 0
    for ticket in tickets:
        if ticket['closed_at']:
            created = datetime.strptime(ticket['created_at'], '%Y-%m-%d %H:%M:%S')
            closed = datetime.strptime(ticket['closed_at'], '%Y-%m-%d %H:%M:%S')
            if closed < created:
                date_errors += 1
    
    print(f"✓ Date consistency:         {'OK' if date_errors == 0 else f'ERROR: {date_errors} tickets'}")
    print()
    
    # Summary
    print("="*70)
    print("VALIDATION COMPLETE")
    print("="*70)
    print(f"Total Records: {len(companies) + len(customers) + len(agents) + len(tickets) + len(interactions)}")
    print(f"Status: {'✅ ALL CHECKS PASSED' if invalid_customer_fk == 0 and invalid_ticket_fk == 0 and date_errors == 0 else '⚠️ SOME ISSUES FOUND'}")
    print("="*70)

if __name__ == '__main__':
    validate_data()
