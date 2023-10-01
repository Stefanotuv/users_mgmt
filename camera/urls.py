
from django.urls import path
from .views import CameraView


urlpatterns = [
    path("view/", CameraView.as_view(template_name='camera/camera.html'),name='camera_view'),
]