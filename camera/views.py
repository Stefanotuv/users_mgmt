from django.shortcuts import render
from django.views import View
from django.http import StreamingHttpResponse
from django.views import View
import io
from picamera import PiCamera
import time


# Create your views here.
class CameraView(View):
    template_name = 'camera/camera.html'
    def get(self, request, *args, **kwargs):
        return StreamingHttpResponse(self.generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

    def generate_frames(self):
        camera = PiCamera()
        camera.resolution = (640, 480)  # Adjust the resolution as needed
        time.sleep(2)  # Allow time for the camera to warm up

        try:
            while True:
                stream = io.BytesIO()
                camera.capture(stream, 'jpeg')
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + stream.getvalue() + b'\r\n')
                stream.seek(0)
                stream.truncate()
        except Exception as e:
            print("Error capturing frame:", e)
        finally:
            camera.close()

