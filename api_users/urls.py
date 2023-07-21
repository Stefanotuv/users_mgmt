from django.urls import path
from . import views
urlpatterns = [
    path("",views.getUser),
    path("add_user", views.addUser),
    path('login/', views.login_view, name='api_login'),
    path('logout/', views.logout_view, name='api_logout'),
    path('signup/', views.signup_view, name='api_signup'),
]