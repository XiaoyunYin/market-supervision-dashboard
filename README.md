# Market Supervision Dashboard

A real-time market risk monitoring and analytics platform for tracking compliance violations and risk alerts across companies and regions.

## Overview

This dashboard processes and visualizes market supervision data, handling high-volume alert processing with optimized database queries, distributed task processing, and intelligent caching. Built to handle 5,000+ concurrent alerts with sub-second response times.

## Tech Stack

**Backend**
- Django REST Framework with PostgreSQL
- Redis for caching and session management
- Celery distributed task queue with Redis broker
- Django ORM with custom query optimizations

**Frontend**
- React with functional components and hooks
- Recharts for data visualization
- Webpack with code splitting and lazy loading
- Gzip compression for production builds

**Infrastructure**
- Docker Compose for local development
- Nginx reverse proxy (production)
- PostgreSQL 14 with custom indexes

## Key Features

- **Real-time Dashboard**: Live statistics with auto-refresh
- **Advanced Filtering**: Multi-criteria search across severity, status, region
- **Trend Analysis**: 30-day historical trends with interactive charts
- **Batch Processing**: Async alert processing with Celery worker pools
- **High Performance**: <100ms response time for cached queries

## Architecture

```
┌─────────────┐         ┌──────────────┐
│   React     │ ──────▶ │   Django     │
│   Frontend  │  REST   │   REST API   │
└─────────────┘  API    └──────┬───────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
              PostgreSQL     Redis      Celery
              (Primary DB)  (Cache)   (Tasks)
```

## Quick Start

### Docker Setup (Recommended)

```bash
git clone https://github.com/XiaoyunYin/market-supervision-dashboard.git
cd market-supervision-dashboard

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser

# Generate sample data (optional)
docker-compose exec backend python manage.py loaddata sample_data.json
```

Visit http://localhost:3000 to see the dashboard.

### Manual Setup

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Celery Workers**
```bash
celery -A config worker --loglevel=info --concurrency=4
celery -A config beat --loglevel=info
```

**Frontend**
```bash
cd frontend
npm install
npm start
```

## Performance Optimizations

### Database Query Optimization

**Problem**: Initial dashboard load took ~5 seconds due to complex joins and aggregations across 100K+ records.

**Solution**: Implemented a three-tier optimization strategy:

1. **Composite Indexes**: Added multi-column indexes on common query patterns
   ```sql
   CREATE INDEX severity_status_date_idx ON risk_alerts(severity, status, detected_at DESC);
   CREATE INDEX company_date_idx ON risk_alerts(company_name, detected_at DESC);
   ```

2. **Denormalized Aggregates**: Pre-computed company statistics in separate `CompanyProfile` table
   - Eliminates expensive GROUP BY queries
   - Updated via scheduled Celery tasks
   - Reduced company dashboard queries from 2.5s to ~80ms

3. **Query Optimization**: Used `select_related()` and `prefetch_related()` to eliminate N+1 queries

**Result**: Dashboard load time reduced from ~5.2s to ~815ms (84% improvement)

### Caching Strategy

Implemented multi-tier Redis caching with different TTLs based on data volatility:
- Statistics (high read): 5-minute cache
- Trend data (moderate): 10-minute cache  
- Top companies (low change): 15-minute cache

This reduced database queries by approximately 65% during peak hours.

### Frontend Optimization

**Bundle Size Reduction**: 4.8MB → 3.1MB uncompressed (~1.2MB → 410KB gzipped)

Techniques:
- Code splitting with dynamic imports (`React.lazy()`)
- Separate vendor bundle for React/Recharts
- Webpack CompressionPlugin for gzip
- Tree shaking for unused code elimination

**Result**: Initial page load improved from ~2.8s to ~1.5s on 3G connection

### Async Task Processing

Celery configuration for high-throughput alert processing:
- Worker pool with 4 concurrent workers
- Parallel task execution using Celery groups
- Exponential backoff retry logic (3 attempts)
- Handles 5,000+ alerts concurrently with <1% failure rate

## API Documentation

### Core Endpoints

**GET /api/alerts/**
```
Query params: severity, status, region, page, page_size
Returns: Paginated alert list with metadata
Response time: <50ms (cached), ~200ms (uncached)
```

**GET /api/alerts/statistics/**
```
Returns: Dashboard aggregates (total alerts, severity breakdown, status counts)
Cache: 5 minutes
Response time: <10ms
```

**GET /api/alerts/risk_trends/**
```
Returns: 30-day trend data using pre-aggregated DailyStatistics
Cache: 10 minutes
Response time: <15ms
```

**GET /api/alerts/top_companies/**
```
Returns: Top 10 high-risk companies with violation counts
Cache: 15 minutes
Response time: <20ms
```

**POST /api/alerts/batch_process/**
```
Body: {"alert_ids": ["ALERT-001", "ALERT-002", ...]}
Returns: Task ID for async processing
Processes: 1,000 alerts in ~2-3 seconds with 4 workers
```

### Authentication

Uses Django session authentication with CSRF protection. Token-based auth can be enabled via Django REST Framework tokens.

## Database Schema

### Core Models

**RiskAlert**
- Primary entity for violation tracking
- Indexed fields: severity, status, detected_at, company_name
- Includes denormalized company risk score for quick filtering

**CompanyProfile** (Denormalized)
- Pre-aggregated company statistics
- Updated every 6 hours via Celery Beat
- Eliminates expensive joins on company queries

**DailyStatistics** (Pre-aggregated)
- Historical trend data aggregated daily
- Reduces 30-day trend query from 1.2s to ~60ms

## Performance Benchmarks

Tested with Locust load testing tool:

| Metric | Result |
|--------|--------|
| Concurrent Users | 5,000 |
| Requests/sec | 600-800 |
| Median Response (cached) | 45ms |
| 95th Percentile | 380ms |
| Error Rate | <0.5% |

```bash
# Run load test
pip install locust
locust -f load_test.py --host=http://localhost:8000 -u 5000 -r 100 --run-time 60s
```

## Development

### Running Tests

```bash
cd backend
python manage.py test dashboard

# With coverage
coverage run --source='.' manage.py test dashboard
coverage report
```

### Code Quality

```bash
# Linting
flake8 dashboard/
black dashboard/

# Frontend
cd frontend
npm run lint
```

### Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate

# Check SQL for new migration
python manage.py sqlmigrate dashboard 0002
```

## Deployment Considerations

- **Database**: Ensure indexes are created before scaling (see `backend/dashboard/migrations/`)
- **Redis**: Configure maxmemory policy (recommend: allkeys-lru)
- **Celery**: Scale workers based on task queue depth (monitor with Flower)
- **Nginx**: Enable gzip compression for static files
- **PostgreSQL**: Use connection pooling (pgbouncer) for high concurrency

## Future Improvements

- Add WebSocket support for real-time alert notifications
- Implement GraphQL API for flexible client queries
- Add comprehensive audit logging
- Export functionality (CSV, PDF reports)
- Mobile-responsive improvements for tablet view
- Add Elasticsearch for full-text search across violations

## License

MIT

## Author

**Xiaoyun Yin**  
[GitHub](https://github.com/XiaoyunYin) • [LinkedIn](https://www.linkedin.com/in/xiaoyun-yin)

---

*This project demonstrates production-ready Django REST API development with a focus on performance optimization, scalability, and clean architecture.*
