from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q

import json

from .models import Task
from .forms import TaskForm
from home.models import Project


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        project = get_object_or_404(Project, id=self.kwargs["project_id"])
        form.instance.project = project
        form.instance.created_by = self.request.user
        if not form.instance.assigned_to:
            form.instance.assigned_to = project.owner
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("project", kwargs={"project_id": self.kwargs["project_id"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, id=self.kwargs["project_id"])
        return context


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def get_success_url(self):
        return reverse_lazy("project", kwargs={"project_id": self.object.project.id})

    def get_queryset(self):
        return Task.objects.filter(
            Q(project__owner=self.request.user) | Q(project__members=self.request.user)
        ).distinct()


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "components/task_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("project", kwargs={"project_id": self.object.project.id})

    def get_queryset(self):
        return Task.objects.filter(
            Q(project__owner=self.request.user) | Q(project__members=self.request.user)
        ).distinct()


class TaskStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            data = json.loads(request.body)
            new_status = data.get("new_status")

            if new_status not in ["TD", "DG", "CO"]:
                return JsonResponse({"error": "Status inválido"}, status=400)

            if (
                request.user != task.project.owner
                and request.user not in task.project.members.all()
            ):
                return JsonResponse({"error": "Sem permissão"}, status=403)

            task.status = new_status
            task.save()
            return JsonResponse({"success": True})

        except Task.DoesNotExist:
            return JsonResponse({"error": "Tarefa não encontrada"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
