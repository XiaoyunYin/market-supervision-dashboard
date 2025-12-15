from django.db import models
from django.utils import timezone


class RiskAlert(models.Model):
    """Market supervision risk alert"""
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('REVIEWING', 'Reviewing'),
        ('RESOLVED', 'Resolved'),
    ]
    
    alert_id = models.CharField(max_length=50, unique=True, db_index=True)
    company_name = models.CharField(max_length=200)
    violation_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    detected_at = models.DateTimeField(default=timezone.now)
    region = models.CharField(max_length=50)
    
    # Denormalized aggregate fields to avoid joins
    total_violations_count = models.IntegerField(default=0)
    company_risk_score = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Composite indexes for optimized queries
        indexes = [
            models.Index(fields=['severity', 'status', 'detected_at'], name='severity_status_date_idx'),
            models.Index(fields=['company_name', 'detected_at'], name='company_date_idx'),
            models.Index(fields=['region', 'severity'], name='region_severity_idx'),
        ]
        ordering = ['-detected_at']
    
    def __str__(self):
        return f"{self.alert_id} - {self.company_name}"


class CompanyProfile(models.Model):
    """Denormalized company data for fast lookups"""
    company_name = models.CharField(max_length=200, unique=True, db_index=True)
    total_violations = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    risk_score = models.FloatField(default=0.0)
    last_violation_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['-risk_score'], name='risk_score_idx'),
        ]


class DailyStatistics(models.Model):
    """Pre-aggregated daily statistics to avoid expensive joins"""
    date = models.DateField(unique=True, db_index=True)
    total_alerts = models.IntegerField(default=0)
    critical_alerts = models.IntegerField(default=0)
    high_alerts = models.IntegerField(default=0)
    medium_alerts = models.IntegerField(default=0)
    low_alerts = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    avg_resolution_time = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['-date']
