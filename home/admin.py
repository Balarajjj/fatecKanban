from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "get_progress")
    list_filter = ("status", "owner")
    search_fields = ("name", "description")

    def get_progress(self, obj):
        return f"{obj.progress}%"  # Usa a @property do modelo

    get_progress.short_description = "Progresso"
