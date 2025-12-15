from rest_framework import serializers
from .models import RiskAlert, CompanyProfile, DailyStatistics


class RiskAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskAlert
        fields = [
            'id', 'alert_id', 'company_name', 'violation_type',
            'severity', 'status', 'amount', 'detected_at', 'region',
            'total_violations_count', 'company_risk_score', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = [
            'id', 'company_name', 'total_violations', 'total_amount',
            'risk_score', 'last_violation_date'
        ]


class DailyStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStatistics
        fields = [
            'date', 'total_alerts', 'critical_alerts', 'high_alerts',
            'medium_alerts', 'low_alerts', 'total_amount', 'avg_resolution_time'
        ]
