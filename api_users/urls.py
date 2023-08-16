from django.urls import path
from . import views
urlpatterns = [
    # path("",views.getUser),
    # path("add_user", views.addUser),
    path('login/', views.UserLoginView.as_view(), name='api_login'),
    path('logout/', views.UserLogoutView.as_view(), name='api_logout'),
    path('signup/', views.UserSignupView.as_view(), name='api_signup'),
    # path('record_trip/'views.ApiTripRecord.as_view(), name='api_record_trip'),
]