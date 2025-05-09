from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from .models import Project, Task
from .forms import TaskForm


@login_required
def home_view(request):
    """View para listar projetos do usuário (owner ou member)"""
    projects = (
        Project.objects.filter(Q(owner=request.user) | Q(members__in=[request.user]))
        .distinct()
        .order_by("-updated_at")
    )

    return render(request, "home/index.html", {"projects": projects, "section": "home"})


@login_required
def project_view(request, project_id):
    """View detalhada do projeto com quadro Kanban"""
    project = get_object_or_404(
        Project.objects.prefetch_related("tasks", "members"),
        Q(id=project_id) & (Q(owner=request.user) | Q(members__in=[request.user])),
    )

    tasks = {
        "TD": project.tasks.filter(status="TD").order_by("-priority", "due_date"),
        "DG": project.tasks.filter(status="DG").order_by("-priority", "due_date"),
        "CO": project.tasks.filter(status="CO").order_by("-updated_at")[:20],
    }

    return render(
        request,
        "home/projects.html",
        {"project": project, "tasks": tasks, "section": "project"},
    )


class TaskCreateView(CreateView):
    """View baseada em classe para criação de tarefas"""

    model = Task
    form_class = TaskForm
    template_name = "components/task_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "project-detail", kwargs={"project_id": self.kwargs["project_id"]}
        )

    def form_valid(self, form):
        form.instance.project_id = self.kwargs["project_id"]
        form.instance.created_by = self.request.user
        if not form.instance.assigned_to:
            form.instance.assigned_to = form.instance.project.owner
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_id"])
        return context


@login_required
def update_task_status(request, task_id):
    """View para atualização de status via AJAX"""
    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        task = get_object_or_404(Task, id=task_id, project__owner=request.user)
        new_status = request.POST.get("status")

        if new_status in dict(Task.STATUS_CHOICES).keys():
            task.status = new_status
            task.save()
            return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)


def login_view(request):
    """View de login personalizada"""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get("next", "home")
            return redirect(next_url)

        messages.error(request, "Credenciais inválidas. Tente novamente.")

    return render(request, "registration/login.html", {"section": "login"})


def logout_view(request):
    """View de logout"""
    logout(request)
    messages.success(request, "Você foi desconectado com sucesso.")
    return redirect("login")
