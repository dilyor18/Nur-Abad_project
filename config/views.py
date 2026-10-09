from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'index.html'


class AuthView(TemplateView):
    template_name = 'auth.html'


class ProfileView(TemplateView):
    template_name = 'profile.html'


class FavoritesView(TemplateView):
    template_name = 'favorites.html'


class ChatsView(TemplateView):
    template_name = 'chats.html'


class NewsPageView(TemplateView):
    template_name = 'news.html'


class AdminPanelView(TemplateView):
    template_name = 'admin.html'


class AdDetailPageView(TemplateView):
    template_name = 'ad_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ad_id'] = self.kwargs.get('id')
        return context
