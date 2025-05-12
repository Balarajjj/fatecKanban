from django.contrib import admin
from .models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "progress")
    list_filter = ("status", "owner")
    search_fields = ("name", "description")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "priority", "assigned_to", "due_date")
    list_filter = ("status", "priority", "project")
    search_fields = ("title", "project__name")
