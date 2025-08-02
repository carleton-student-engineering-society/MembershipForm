from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class CarletonEmail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    access_token = models.CharField(max_length=300)
    refresh_token = models.CharField(max_length=300)

class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    student_number = models.IntegerField()
    signup_date = models.DateTimeField(auto_now=True)
    year = models.IntegerField()
    revoked = models.BooleanField(default=False)
    program = models.CharField(max_length=100)
    engineer = models.BooleanField()
    paid = models.BooleanField(default=False)

    @property
    def expired(self):
        # April 30th of next year
        cutoff = datetime(self.year + 1, 4, 30).date()
        return datetime.now().date() > cutoff or self.revoked

class MembershipUpdateHistory(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    new_name = models.CharField(max_length=100)
    new_address = models.CharField(max_length=100)
    new_student_number = models.IntegerField()
    new_revoked = models.BooleanField()
    new_program = models.CharField(max_length=100)
    new_engineer = models.BooleanField()
    new_paid = models.BooleanField()
    change_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    change_date = models.DateTimeField(auto_now=True)