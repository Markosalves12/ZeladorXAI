from django.contrib.auth import views as auth_views
from django.urls import path
from ai_chat import views

urlpatterns = [
    path('', views.home, name='ai-home'),
    path('login/', views.FamilyLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('ai/perguntar/', views.ask, name='ai-ask'),
    path('ai/ferramentas/', views.catalog, name='ai-catalog'),
]
