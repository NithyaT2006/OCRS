from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 

class Complaint(models.Model):
    STATUS_CHOICES = [
    ("Pending", "Pending"),
    ("In Progress", "In Progress"),
    ("Resolved", "Resolved"),
    ("Closed", "Closed"),
]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default="untitled")
    category = models.CharField(max_length=100)
    place = models.CharField(max_length=200,default="")
    description = models.TextField()
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    issue_date = models.DateField(null=True, blank=True)
    attachment = models.FileField(upload_to='complaint_files/', null=True, blank=True)

    def __str__(self):
        return self.title



class UserRegister(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)
    password = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)


    def __str__(self):
        return self.username
