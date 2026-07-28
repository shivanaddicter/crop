from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('predict/', views.predict, name='predict'),
    path('history/', views.history, name='history'),
    path('history/delete/<int:pk>/', views.delete_record, name='delete_record'),
    path('history/delete-all/', views.delete_all_history, name='delete_all_history'),
    path('export/', views.export_csv, name='export_csv'),
    path('register/', views.register, name='register'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('weather-predict/', views.weather_predict, name='weather_predict'),
    path('founder/', views.founder, name='founder'),
]