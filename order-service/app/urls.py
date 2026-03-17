from django.urls import path
from .views import OrderAction

urlpatterns = [
    path('', OrderAction.as_view()),
    path('<int:pk>/', OrderAction.as_view()),
]