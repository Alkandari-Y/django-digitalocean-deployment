from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()

# Create your models here.
class Task(models.Model):
    name = models.CharField(max_length=50)
    status = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_tasks')
    descriptions = models.TextField()
    image = models.ImageField(upload_to='uploads')
