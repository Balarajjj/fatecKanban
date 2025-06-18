from django.utils import timezone
from tasks.models import Task


def get_task_dashboard_data(tasks_queryset):
    today = timezone.now().date()

    done = tasks_queryset.filter(status="CO").count()
    overdue = tasks_queryset.filter(due_date__lt=today, status__in=["TD", "DG"]).count()
    on_time = tasks_queryset.filter(
        due_date__gte=today, status__in=["TD", "DG"]
    ).count()

    upcoming = tasks_queryset.filter(
        due_date__gte=today, due_date__lte=today + timezone.timedelta(days=3)
    ).order_by("due_date")[:3]

    return {
        "done": done,
        "overdue": overdue,
        "on_time": on_time,
        "upcoming": upcoming,
    }
