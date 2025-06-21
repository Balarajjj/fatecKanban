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
from notifications.models import Notification  # IMPORTANTE


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

        response = super().form_valid(form)

        # Notifica se o responsável não for o criador
        assigned_user = form.instance.assigned_to
        if assigned_user and assigned_user != self.request.user:
            Notification.objects.create(
                user=assigned_user,
                task=form.instance,
                message=f"Você foi atribuído à tarefa: {form.instance.title}",
            )

        return response

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

    def form_valid(self, form):
        old_task = self.get_object()
        old_assigned_to = old_task.assigned_to
        new_assigned_to = form.cleaned_data.get("assigned_to")

        response = super().form_valid(form)

        if (
            new_assigned_to
            and new_assigned_to != old_assigned_to
            and new_assigned_to != self.request.user
        ):
            Notification.objects.create(
                user=new_assigned_to,
                task=self.object,
                message=f"Você foi atribuído à tarefa: {self.object.title}",
            )

        return response


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
