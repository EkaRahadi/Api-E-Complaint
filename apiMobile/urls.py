from django.urls import path
from . import views

urlpatterns = [
    path('', views.apiOverview, name='api-overview'),
    path('login/', views.loginAdmin, name='admin-login'),
    path('admin/', views.adminListCreate, name='admin-lists'),
    path('admin/<str:pk>/', views.updateDeleteAdmin, name='admin-update'),
    path('complaint/', views.listUpdateComplaint, name='complaint-list'),
    path('complaint-kategori/<str:pk>/', views.listComplaintCategory, name='complaint-list-category'),
    path('status/', views.listStatus, name='status-list'),
    path('kategori/', views.listCategory, name='kategori_list'),
    path('complaint-create/', views.complaintCreate, name='complaint-create'),
    path('banyak-complaint/', views.banyakCompalint, name='banyak-complaint'),
    path('token-partial-update/<str:pk>/', views.tokenPartialUpdate, name='token-partial-update'),
    path('complaint-by-status/<str:pk>/', views.listComplaintStatus, name='list-complaint-by-status'),
    path('test-motif/', views.testNotif, name="test-notif")
]
