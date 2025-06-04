from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from home.models import Project
from .models import Task
from .forms import TaskForm
from django.db.models import Q
from django.views.generic.edit import UpdateView, DeleteView


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
    template_name = "tasks/task_edit.html"

    def get_success_url(self):
        return reverse_lazy("project", kwargs={"project_id": self.object.project.id})

    def get_queryset(self):
        return Task.objects.filter(
            Q(project__owner=self.request.user)
            | Q(project__members__in=[self.request.user])
        )


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "components/task_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("project", args=[self.object.project.id])

    def get_queryset(self):
        return Task.objects.filter(
            Q(project__owner=self.request.user)
            | Q(project__members__in=[self.request.user])
        )
