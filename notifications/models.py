from django.conf import settings
from django.db import models
from tasks.models import Task
from home.models import Project  # ajuste o import conforme seu app/model
from django.utils import timezone


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True
    )
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        alvo = (
            self.task.title
            if self.task
            else (self.project.name if self.project else "Geral")
        )
        return f"Notification for {self.user.username} - {alvo}"
