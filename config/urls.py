from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views import AdDetailPageView, AdminPanelView, AuthView, ChatsView, FavoritesView, HomeView, NewsPageView, ProfileView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('auth/', AuthView.as_view(), name='auth'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('favorites/', FavoritesView.as_view(), name='favorites_page'),
    path('chats/', ChatsView.as_view(), name='chats_page'),
    path('news/', NewsPageView.as_view(), name='news_page'),
    path('admin-panel/', AdminPanelView.as_view(), name='admin_panel'),
    path('ad/<int:id>/', AdDetailPageView.as_view(), name='ad_detail_page'),
    path('admin/', admin.site.urls),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.locations.urls')),
    path('api/', include('apps.ads.urls')),
    path('api/', include('apps.news.urls')),
    path('api/', include('apps.favorites.urls')),
    path('api/', include('apps.chats.urls')),
    path('api/', include('apps.complaints.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
