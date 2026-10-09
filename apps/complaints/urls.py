from django.urls import path

from .views import ReportDetailAPIView, ReportListCreateAPIView

urlpatterns = [
    path('reports/', ReportListCreateAPIView.as_view(), name='reports-list'),
    path('reports/<int:pk>/', ReportDetailAPIView.as_view(), name='report-detail'),
]
