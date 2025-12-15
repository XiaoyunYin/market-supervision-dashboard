from django.contrib import admin
from .models import RiskAlert, CompanyProfile, DailyStatistics


@admin.register(RiskAlert)
class RiskAlertAdmin(admin.ModelAdmin):
    list_display = ['alert_id', 'company_name', 'severity', 'status', 'amount', 'detected_at']
    list_filter = ['severity', 'status', 'region']
    search_fields = ['alert_id', 'company_name', 'violation_type']
    date_hierarchy = 'detected_at'


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'total_violations', 'risk_score', 'total_amount']
    search_fields = ['company_name']
    ordering = ['-risk_score']


@admin.register(DailyStatistics)
class DailyStatisticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_alerts', 'critical_alerts', 'high_alerts', 'total_amount']
    date_hierarchy = 'date'
