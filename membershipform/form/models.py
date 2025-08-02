from django.db import models
from django.contrib.auth.models import User

class CarletonEmail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    access_token = models.CharField(max_length=300)
    refresh_token = models.CharField(max_length=300)

class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=100)
    student_number = models.IntegerField()
    signup_date = models.DateField(auto_now=True)
    year = models.CharField(max_length=10)