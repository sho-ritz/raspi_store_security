from django.urls import path
from . import views

urlpatterns = [
    path('check_user/', views.check_user, name='check_user'),
    path('create_purchase_log/', views.create_purchase_log, name='create_purchase_log'),
    path('send_to_line_group/', views.send_to_line_group, name='send_to_line_group'),
]