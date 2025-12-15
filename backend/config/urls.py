from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from dashboard.views import RiskAlertViewSet

router = DefaultRouter()
router.register(r'alerts', RiskAlertViewSet, basename='alert')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
