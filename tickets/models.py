from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [('user','User'),('agent','Agent'),('admin','Admin')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

class Ticket(models.Model):
    STATUS_CHOICES = [('open','Open'),('assigned','Assigned'),('in_progress','In Progress'),('resolved','Resolved'),('closed','Closed')]
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, default='normal')
    sla_hours = models.PositiveIntegerField(default=24)
    created_by = models.ForeignKey(User, related_name='tickets_created', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name='tickets_assigned', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    version = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_breached(self):
        return timezone.now() > self.created_at + timezone.timedelta(hours=self.sla_hours)

class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Timeline(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='timeline', on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
