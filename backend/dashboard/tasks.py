from celery import shared_task, group
from django.core.cache import cache
from django.db import transaction
from django.db.models import Sum, Count
from .models import RiskAlert, CompanyProfile, DailyStatistics
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_single_alert(self, alert_id):
    """
    Process individual alert with retry logic
    Retries up to 3 times with 60s delay
    """
    try:
        alert = RiskAlert.objects.get(alert_id=alert_id)
        
        # Simulate processing logic
        alert.status = 'REVIEWING'
        alert.save(update_fields=['status'])
        
        # Trigger company risk recalculation
        recalculate_company_risk.delay(alert.company_name)
        
        logger.info(f"Successfully processed alert {alert_id}")
        return {'alert_id': alert_id, 'status': 'success'}
        
    except RiskAlert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found")
        return {'alert_id': alert_id, 'status': 'not_found'}
        
    except Exception as exc:
        logger.error(f"Error processing alert {alert_id}: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def process_alert_batch(alert_ids):
    """
    Process multiple alerts in parallel using Celery group
    Enables concurrent processing of 5K+ alerts
    """
    # Create parallel task group
    job = group(process_single_alert.s(alert_id) for alert_id in alert_ids)
    
    # Execute all tasks in parallel
    result = job.apply_async()
    
    logger.info(f"Started batch processing of {len(alert_ids)} alerts")
    return {
        'total_alerts': len(alert_ids),
        'group_id': result.id
    }


@shared_task(bind=True, max_retries=3)
def recalculate_company_risk(self, company_name):
    """
    Recalculate and update denormalized company risk score
    Uses retry logic for reliability
    """
    try:
        with transaction.atomic():
            # Aggregate company violations
            company_stats = RiskAlert.objects.filter(
                company_name=company_name
            ).aggregate(
                total=Count('id'),
                total_amount=Sum('amount'),
                critical_count=Count('id', filter={'severity': 'CRITICAL'}),
                high_count=Count('id', filter={'severity': 'HIGH'})
            )
            
            # Calculate risk score
            risk_score = (
                company_stats['critical_count'] * 10 +
                company_stats['high_count'] * 5 +
                float(company_stats['total_amount'] or 0) / 100000
            )
            
            # Update denormalized CompanyProfile
            CompanyProfile.objects.update_or_create(
                company_name=company_name,
                defaults={
                    'total_violations': company_stats['total'],
                    'total_amount': company_stats['total_amount'] or 0,
                    'risk_score': risk_score,
                }
            )
            
            # Invalidate cache
            cache.delete('top_risk_companies')
            
            logger.info(f"Updated risk score for {company_name}: {risk_score}")
            return {'company': company_name, 'risk_score': risk_score}
            
    except Exception as exc:
        logger.error(f"Error calculating risk for {company_name}: {str(exc)}")
        raise self.retry(exc=exc, countdown=30)


@shared_task
def aggregate_daily_statistics():
    """
    Pre-aggregate daily statistics to avoid expensive runtime joins
    Runs via Celery beat schedule
    """
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Aggregate yesterday's data
    stats = RiskAlert.objects.filter(
        detected_at__date=yesterday
    ).aggregate(
        total=Count('id'),
        critical=Count('id', filter={'severity': 'CRITICAL'}),
        high=Count('id', filter={'severity': 'HIGH'}),
        medium=Count('id', filter={'severity': 'MEDIUM'}),
        low=Count('id', filter={'severity': 'LOW'}),
        total_amount=Sum('amount')
    )
    
    # Store in denormalized table
    DailyStatistics.objects.update_or_create(
        date=yesterday,
        defaults={
            'total_alerts': stats['total'],
            'critical_alerts': stats['critical'],
            'high_alerts': stats['high'],
            'medium_alerts': stats['medium'],
            'low_alerts': stats['low'],
            'total_amount': stats['total_amount'] or 0,
        }
    )
    
    # Invalidate related caches
    cache.delete('risk_trends_30d')
    
    logger.info(f"Aggregated statistics for {yesterday}")
    return {'date': str(yesterday), 'total_alerts': stats['total']}
