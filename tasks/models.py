from django.db import models
from django.conf import settings
from django.utils import timezone
from home.models import Project  # Referência ao app correto


class Task(models.Model):
    STATUS_CHOICES = [
        ("TD", "To Do"),
        ("DG", "Doing"),
        ("CO", "Done"),
    ]

    PRIORITY_CHOICES = [
        (1, "Baixa"),
        (2, "Média"),
        (3, "Alta"),
        (4, "Urgente"),
    ]

    title = models.CharField(max_length=200, verbose_name="Título")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks", verbose_name="Projeto"
    )
    status = models.CharField(
        max_length=2, choices=STATUS_CHOICES, default="TD", verbose_name="Status"
    )
    priority = models.PositiveSmallIntegerField(
        choices=PRIORITY_CHOICES, default=2, verbose_name="Prioridade"
    )
    due_date = models.DateField(null=True, blank=True, verbose_name="Data de Conclusão")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        verbose_name="Responsável",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks",
        verbose_name="Criado por",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ["priority", "-due_date"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def is_overdue(self):
        if self.due_date:
            return timezone.now().date() > self.due_date
        return False

    def get_priority_class(self):
        priority_classes = {
            1: "bg-blue-100 text-blue-800",
            2: "bg-green-100 text-green-800",
            3: "bg-yellow-100 text-yellow-800",
            4: "bg-red-100 text-red-800",
        }
        return priority_classes.get(self.priority, "")
