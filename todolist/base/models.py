from django.db import models
from django.contrib.auth.models import User 




class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.IntegerField(choices=[(1, 'Priority 1'), (2, 'Priority 2'), (3, 'Priority 3')])
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when task is created
    completed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User who created the task

    def __str__(self):
        return self.name 
    


class Tambola(models.Model):
    min_range = models.IntegerField()
    max_range = models.IntegerField()
    generated_numbers = models.TextField(blank=True, null=True)