# face_recognition_app/urls.py

from django.urls import path
from .views import FacialRecognitionView

urlpatterns = [
    path('facial_recognition/', FacialRecognitionView.as_view(), name='facial_recognition'),
]
