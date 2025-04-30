from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Project(models.Model):
    STATUS_CHOICES = [
        ("PL", "Planejamento"),
        ("EA", "Em andamento"),
        ("AT", "Atrasado"),
        ("CO", "Concluído"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def progress(self):
        tasks = self.task_set.all()
        if tasks.count() == 0:
            return 0
        return int((tasks.filter(status="CO").count() / tasks.count()) * 100)


class Task(models.Model):
    STATUS_CHOICES = [
        ("TD", "To Do"),
        ("DG", "Doing"),
        ("CO", "Done"),
    ]

    title = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="TD")
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
