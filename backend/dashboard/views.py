from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import RiskAlert, CompanyProfile, DailyStatistics
from .serializers import RiskAlertSerializer, CompanyProfileSerializer, DailyStatisticsSerializer
from .tasks import process_alert_batch, recalculate_company_risk


class RiskAlertViewSet(viewsets.ModelViewSet):
    queryset = RiskAlert.objects.all()
    serializer_class = RiskAlertSerializer
    
    def get_queryset(self):
        """Optimized query with select_related to avoid N+1"""
        queryset = RiskAlert.objects.all()
        
        # Apply filters
        severity = self.request.query_params.get('severity')
        status_filter = self.request.query_params.get('status')
        region = self.request.query_params.get('region')
        
        if severity:
            queryset = queryset.filter(severity=severity)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if region:
            queryset = queryset.filter(region=region)
        
        # Only fetch necessary fields for list view
        if self.action == 'list':
            queryset = queryset.only(
                'alert_id', 'company_name', 'severity', 
                'status', 'amount', 'detected_at'
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get dashboard statistics with Redis caching"""
        cache_key = 'dashboard_statistics'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Optimized aggregation query using denormalized data
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Use composite index: severity_status_date_idx
        stats = RiskAlert.objects.filter(
            detected_at__gte=thirty_days_ago
        ).aggregate(
            total=Count('id'),
            critical=Count('id', filter=Q(severity='CRITICAL')),
            high=Count('id', filter=Q(severity='HIGH')),
            pending=Count('id', filter=Q(status='PENDING')),
            total_amount=Sum('amount')
        )
        
        # Cache for 5 minutes
        cache.set(cache_key, stats, 300)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def risk_trends(self, request):
        """Get risk trends using pre-aggregated data"""
        cache_key = 'risk_trends_30d'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Use pre-aggregated DailyStatistics instead of expensive joins
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        trends = DailyStatistics.objects.filter(
            date__gte=thirty_days_ago
        ).order_by('date')
        
        serializer = DailyStatisticsSerializer(trends, many=True)
        data = serializer.data
        
        # Cache for 10 minutes
        cache.set(cache_key, data, 600)
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def top_companies(self, request):
        """Get companies with highest risk using denormalized data"""
        cache_key = 'top_risk_companies'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Use denormalized CompanyProfile instead of joining/aggregating
        # Uses risk_score_idx index
        top_companies = CompanyProfile.objects.order_by('-risk_score')[:10]
        
        serializer = CompanyProfileSerializer(top_companies, many=True)
        data = serializer.data
        
        # Cache for 15 minutes
        cache.set(cache_key, data, 900)
        
        return Response(data)
    
    @action(detail=False, methods=['post'])
    def batch_process(self, request):
        """Trigger Celery batch processing"""
        alert_ids = request.data.get('alert_ids', [])
        
        if not alert_ids:
            return Response(
                {'error': 'No alert IDs provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Trigger async Celery task
        task = process_alert_batch.delay(alert_ids)
        
        return Response({
            'task_id': task.id,
            'status': 'Processing started'
        })
