from django.contrib import admin
from .models import CropData, UploadedCSV


@admin.register(CropData)
class CropDataAdmin(admin.ModelAdmin):
    list_display = ['user', 'temperature', 'rainfall', 'humidity', 'result', 'created_at']
    list_filter = ['result', 'created_at']
    search_fields = ['user__username', 'result']


@admin.register(UploadedCSV)
class UploadedCSVAdmin(admin.ModelAdmin):
    list_display = ['user', 'file', 'uploaded_at']
