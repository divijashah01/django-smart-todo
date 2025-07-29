# models.py
from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Subject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default="#b19cd9")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def task_count(self):
        return self.tasks.count()

class Task(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    due_time = models.TimeField()
    ideal_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_due_today(self):
        return self.due_date == date.today()
    
class PlannerTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planner_tasks')
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    due_time = models.TimeField(null=True, blank=True)
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # New repeat fields
    repeat_enabled = models.BooleanField(default=False)
    repeat_type = models.CharField(max_length=10, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], blank=True, null=True)
    repeat_until = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_due_today(self):
        return self.due_date == date.today()
    
class UserStatistics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='statistics')
    longest_streak = models.IntegerField(default=0)
    last_streak_update = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Statistics"