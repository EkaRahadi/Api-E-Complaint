from django.urls import path
from . import views

urlpatterns = [
    path('complaint/', views.rawComplaint, name='raw-complaint'),
]
