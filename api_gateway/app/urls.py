from django.urls import path
from .views import AIChatView, AICartView, AIHealthView, AISearchView, GatewayView

urlpatterns = [
    path('api/ai/health/', AIHealthView.as_view()),
    path('api/ai/chat/', AIChatView.as_view()),
    path('api/ai/search/', AISearchView.as_view()),
    path('api/ai/cart/', AICartView.as_view()),
    # Route: localhost:8000/api/books/
    path('api/<str:service_name>/', GatewayView.as_view()),
    path('api/<str:service_name>/<path:path>/', GatewayView.as_view()),
]
