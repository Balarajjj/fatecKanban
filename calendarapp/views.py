from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from tasks.models import Task
from .models import UserSemester
import calendar
from datetime import date, datetime


class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = "calendarapp/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Pega ano e mês da query string, ou usa hoje se não informado
        year = self.request.GET.get("year")
        month = self.request.GET.get("month")
        today = date.today()
        context["today"] = today

        try:
            year = int(year)
        except (TypeError, ValueError):
            year = today.year

        try:
            month = int(month)
            if not (1 <= month <= 12):
                month = today.month
        except (TypeError, ValueError):
            month = today.month

        # Mapeia os meses para nomes em português (sem depender de locale)
        meses_pt = [
            "",
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro",
        ]
        month_name = meses_pt[month]

        # Busca as tasks apenas no mês/ano atuais
        tasks = Task.objects.filter(
            assigned_to=user, due_date__year=year, due_date__month=month
        )

        try:
            semester = user.current_semester
        except UserSemester.DoesNotExist:
            semester = None

        calendar_tasks_by_date = {}
        for task in tasks:
            key = task.due_date.strftime("%Y-%m-%d")
            calendar_tasks_by_date.setdefault(key, []).append(task)

        _, total_days = calendar.monthrange(year, month)
        weekday_start = date(year, month, 1).weekday()
        weekday_start = (weekday_start + 1) % 7

        days = []
        for day in range(1, total_days + 1):
            day_str = f"{year}-{month:02d}-{day:02d}"
            days.append({"day": day, "date_str": day_str})

        # Calcula mês anterior e próximo para navegação
        prev_month = month - 1
        prev_year = year
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1

        next_month = month + 1
        next_year = year
        if next_month == 13:
            next_month = 1
            next_year += 1

        context.update(
            {
                "calendar_tasks_by_date": calendar_tasks_by_date,
                "semester": semester,
                "year": year,
                "month": f"{month:02d}",
                "month_name": month_name,
                "days": days,
                "weekday_start": weekday_start,
                "prev_year": prev_year,
                "prev_month": f"{prev_month:02d}",
                "next_year": next_year,
                "next_month": f"{next_month:02d}",
            }
        )
        return context
