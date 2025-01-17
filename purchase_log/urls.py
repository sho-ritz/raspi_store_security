from django.urls import path
from . import views

urlpatterns = [
    path('check_user/', views.check_user, name='check_user'),
    path('create_purchase_log/', views.create_purchase_log, name='create_purchase_log'),
]