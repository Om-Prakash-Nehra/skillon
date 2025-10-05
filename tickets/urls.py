from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('me/', views.me),
    path('health/', views.health),
    path('tickets/', views.ticket_list),
    path('tickets/create/', views.ticket_create),
    path('tickets/<int:pk>/', views.ticket_detail),
    path('tickets/<int:pk>/comments/', views.comment_create),
    path('tickets/<int:pk>/assign/', views.assign_ticket),
]
