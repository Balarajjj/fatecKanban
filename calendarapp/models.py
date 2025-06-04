from django.db import models
from django.conf import settings


class UserSemester(models.Model):
    SEMESTER_CHOICES = [
        ("2025.1", "2025.1"),
        ("2025.2", "2025.2"),
        ("2026.1", "2026.1"),
        # Adicione outros semestres conforme necessário
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="current_semester",
    )
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    course = models.CharField(max_length=100)
    subjects = models.ManyToManyField("calendarapp.Subject", blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.semester}"


class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
