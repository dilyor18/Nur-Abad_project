from django.urls import path

from .views import CityListAPIView, DistrictListAPIView

urlpatterns = [
    path('cities/', CityListAPIView.as_view(), name='cities'),
    path('districts/', DistrictListAPIView.as_view(), name='districts'),
]
