#!/bin/bash

# Market Supervision Dashboard - Quick Setup Script

echo "=================================="
echo "Market Supervision Dashboard Setup"
echo "=================================="

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

echo "✓ Docker and Docker Compose found"

# Start services
echo ""
echo "Starting services with Docker Compose..."
docker-compose up -d

echo "Waiting for services to be ready..."
sleep 10

# Run migrations
echo ""
echo "Running database migrations..."
docker-compose exec -T backend python manage.py migrate

# Create superuser (optional)
echo ""
echo "Do you want to create a Django superuser? (y/n)"
read -r create_superuser

if [ "$create_superuser" = "y" ]; then
    docker-compose exec backend python manage.py createsuperuser
fi

# Generate sample data
echo ""
echo "Generating sample data..."
docker-compose exec -T backend python manage.py shell << EOF
from dashboard.models import RiskAlert, CompanyProfile
from django.utils import timezone
import random

companies = ['TechCorp', 'FinanceInc', 'RetailCo', 'EnergyLtd', 'PharmaGroup']
regions = ['North America', 'Europe', 'Asia', 'South America']
severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
statuses = ['PENDING', 'REVIEWING', 'RESOLVED']
violations = ['Insider Trading', 'Market Manipulation', 'False Reporting', 'Compliance Breach']

for i in range(500):
    RiskAlert.objects.create(
        alert_id=f'ALERT-{i:05d}',
        company_name=random.choice(companies),
        violation_type=random.choice(violations),
        severity=random.choice(severities),
        status=random.choice(statuses),
        amount=random.uniform(10000, 1000000),
        region=random.choice(regions),
        total_violations_count=random.randint(1, 50),
        company_risk_score=random.uniform(0, 100)
    )

print("✓ Created 500 sample risk alerts")
EOF

# Setup frontend
echo ""
echo "Setting up frontend..."
cd frontend
npm install

echo ""
echo "Building frontend..."
npm run build

cd ..

echo ""
echo "=================================="
echo "Setup Complete! 🎉"
echo "=================================="
echo ""
echo "Access the application:"
echo "  • Frontend: http://localhost:3000"
echo "  • Backend API: http://localhost:8000/api/"
echo "  • Admin Panel: http://localhost:8000/admin/"
echo ""
echo "To start development servers:"
echo "  • Backend: docker-compose up"
echo "  • Frontend: cd frontend && npm run dev"
echo ""
echo "To run load tests:"
echo "  • cd backend && locust -f load_test.py --host=http://localhost:8000"
echo ""
echo "View logs:"
echo "  • docker-compose logs -f"
echo ""
