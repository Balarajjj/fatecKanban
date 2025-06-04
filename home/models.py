from django.db import models
from django.conf import settings
from django.urls import reverse


from django.db import models
from django.conf import settings


class Project(models.Model):
    STATUS_CHOICES = [
        ("PL", "Planejamento"),
        ("EA", "Em andamento"),
        ("AT", "Atrasado"),
        ("CO", "Concluído"),
    ]

    name = models.CharField(max_length=100, verbose_name="Nome do Projeto")
    description = models.TextField(blank=True, verbose_name="Descrição")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name="Responsável",
    )
    status = models.CharField(
        max_length=2, choices=STATUS_CHOICES, default="PL", verbose_name="Status"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="shared_projects",
        blank=True,
        verbose_name="Colaboradores",
    )

    # Novos campos de data
    start_date = models.DateField(null=True, blank=True, verbose_name="Data de Início")
    end_date = models.DateField(null=True, blank=True, verbose_name="Data de Conclusão")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("project-detail", kwargs={"pk": self.pk})
