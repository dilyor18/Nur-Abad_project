from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination

from .models import Report
from .serializers import ReportSerializer


class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReportListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = Report.objects.select_related('reporter', 'ad', 'news', 'user')
        if not self.request.user.is_staff:
            return queryset.filter(reporter=self.request.user)
        return queryset


class ReportDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Report.objects.select_related('reporter', 'ad', 'news', 'user')

    def get_object(self):
        obj = get_object_or_404(self.queryset, pk=self.kwargs['pk'])
        if not self.request.user.is_staff and obj.reporter != self.request.user:
            raise PermissionDenied('You do not have access to this report.')
        return obj

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if not request.user.is_staff and obj.reporter != request.user:
            raise PermissionDenied('Only admins can update report status.')
        return super().update(request, *args, **kwargs)
