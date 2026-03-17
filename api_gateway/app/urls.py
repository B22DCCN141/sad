from django.urls import path
from .views import GatewayView

urlpatterns = [
    # Route: localhost:8000/api/books/
    path('api/<str:service_name>/', GatewayView.as_view()),
    path('api/<str:service_name>/<path:path>/', GatewayView.as_view()),
]