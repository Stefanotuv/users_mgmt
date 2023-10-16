from django.shortcuts import render

# Create your views here.


# face_recognition_app/views.py

from django.http import StreamingHttpResponse
from django.views import View
from .face_recognition import recognize_faces

class FacialRecognitionView(View):
    def get(self, request, *args, **kwargs):
        return StreamingHttpResponse(recognize_faces(), content_type='multipart/x-mixed-replace; boundary=frame')

