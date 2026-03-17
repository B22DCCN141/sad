from django.urls import path
from .views import CartAction

urlpatterns = [
    path('carts/', CartAction.as_view()),
    path('carts/<int:customer_id>/', CartAction.as_view()),
    path('carts/<int:customer_id>/items/<int:book_id>/', CartAction.as_view()),
]