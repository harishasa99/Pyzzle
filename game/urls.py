from django.urls import path
from .views import generate_states, solve_with_image, upload_image


urlpatterns = [
    path('generate-states/', generate_states, name='generate_states'),  
    path('solve-with-image/', solve_with_image, name='solve_with_image'),
    path("upload-image/", upload_image, name="upload_image"),
]
