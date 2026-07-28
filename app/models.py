from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CropData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    temperature = models.FloatField()
    rainfall = models.FloatField()
    humidity = models.FloatField()
    result = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} → {self.result} ({self.created_at.strftime('%Y-%m-%d')})"


class UploadedCSV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='csv/')
    uploaded_at = models.DateTimeField(auto_now_add=True)