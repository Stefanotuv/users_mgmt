
from django.urls import path
from . import views


urlpatterns = [
    path("", views.wifi_config_view, name='connect_mgmt'),
]