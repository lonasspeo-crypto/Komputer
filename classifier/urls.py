from django.urls import path
from . import views

app_name = 'classifier'

urlpatterns = [
    path('', views.index, name='index'),
    path('hasil/<int:pk>/', views.hasil, name='hasil'),
    path('tentang/', views.about, name='about'),
    path('riwayat/', views.riwayat, name='riwayat'),
]
