from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Project
from tasks.models import Task
from .forms import TaskForm
from .forms import ProjectForm
from django.views.generic.edit import UpdateView
from tasks.models import Task
from django.views.generic.edit import DeleteView
from django.shortcuts import render
from django.shortcuts import render
from django.utils import timezone
from .models import Project
from collections import Counter
import json
from django.core.serializers.json import DjangoJSONEncoder


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


@login_required
def dashboard_home(request):
    # Tarefas ordenadas por vencimento (futuras e não concluídas)
    upcoming_tasks = (
        Task.objects.filter(
            due_date__gte=timezone.now().date(),
        )
        .exclude(status="CO")
        .order_by("due_date")[:5]
    )

    # Status geral
    status_counts = Counter(Task.objects.values_list("status", flat=True))

    # Convertendo para nomes legíveis
    status_display = {
        "TD": "A Fazer",
        "DG": "Em Progresso",
        "CO": "Concluídas",
    }
    status_data = {status_display.get(k, k): v for k, v in status_counts.items()}

    # Top 3 projetos com mais tarefas
    top_projects = Project.objects.all()
    top_projects = sorted(top_projects, key=lambda p: p.tasks.count(), reverse=True)[:3]

    return render(
        request,
        "home/dashboard.html",
        {
            "upcoming_tasks": upcoming_tasks,
            "status_data": status_data,
            "top_projects": top_projects,
        },
    )


@login_required
def home_view(request):
    """View para listar projetos do usuário (owner ou member)"""
    projects = (
        Project.objects.filter(Q(owner=request.user) | Q(members__in=[request.user]))
        .distinct()
        .order_by("-updated_at")
    )

    return render(request, "home/index.html", {"projects": projects, "section": "home"})


from django.shortcuts import get_object_or_404, render
from collections import Counter
from django.db.models import Q, Count
from tasks.models import Task
from .models import Project
import json
from django.core.serializers.json import DjangoJSONEncoder


def project_view(request, project_id):
    """View detalhada do projeto com quadro Kanban e dashboards"""
    project = get_object_or_404(
        Project.objects.prefetch_related("tasks", "members")
        .filter(
            Q(id=project_id) & (Q(owner=request.user) | Q(members__in=[request.user]))
        )
        .distinct()
    )

    # Quadro Kanban
    tasks = {
        "TD": project.tasks.filter(status="TD").order_by("-priority", "due_date"),
        "DG": project.tasks.filter(status="DG").order_by("-priority", "due_date"),
        "CO": project.tasks.filter(status="CO").order_by("-updated_at")[:20],
    }

    all_tasks = project.tasks.all()

    # ✅ Cálculo da barra de progresso
    total_tasks = all_tasks.count()
    completed_tasks = all_tasks.filter(status="CO").count()
    progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    # Dados para gráfico de pizza
    status_counts = Counter(all_tasks.values_list("status", flat=True))
    status_display = {
        "TD": "A Fazer",
        "DG": "Em Progresso",
        "CO": "Concluídas",
    }

    status_colors = {
        "TD": "#ef4444",
        "DG": "#facc15",
        "CO": "#10b981",
    }

    status_data = {
        "labels": [status_display.get(k, k) for k in status_counts.keys()],
        "data": list(status_counts.values()),
        "colors": [status_colors.get(k, "#999999") for k in status_counts.keys()],
    }

    collaborators_data = (
        all_tasks.values("assigned_to__first_name")
        .annotate(task_count=Count("id"))
        .order_by("-task_count")
    )

    collaborator_colors = [
        "#3b82f6",
        "#ef4444",
        "#10b981",
        "#f97316",
        "#8b5cf6",
        "#ec4899",
        "#14b8a6",
        "#f59e0b",
        "#84cc16",
        "#6366f1",
    ]

    kanban_columns = [
        ("TD", "A Fazer", "todo"),
        ("DG", "Em Progresso", "doing"),
        ("CO", "Concluído", "done"),
    ]

    task_by_collaborator = {
        "labels": [
            item["assigned_to__first_name"] or "Não atribuído"
            for item in collaborators_data
        ],
        "data": [item["task_count"] for item in collaborators_data],
        "colors": collaborator_colors[: len(collaborators_data)],
    }

    context = {
        "project": project,
        "tasks": tasks,
        "progress": progress,  # ✅ progresso para usar no HTML
        "status_data_json": json.dumps(status_data, cls=DjangoJSONEncoder),
        "task_by_collaborator_json": json.dumps(
            task_by_collaborator, cls=DjangoJSONEncoder
        ),
        "has_tasks": all_tasks.exists(),
        "kanban_columns": kanban_columns,
    }

    return render(request, "home/projects.html", context)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "home/project_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("home")


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "home/project_form.html"
    success_url = reverse_lazy("home")

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "home/project_confirm_delete.html"
    success_url = reverse_lazy("home")

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)


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


@login_required
def useful_links_view(request):
    links = [
        {"name": "FATEC São Paulo", "url": "https://www.fatecsp.br"},
        {"name": "SIGA", "url": "https://siga.cps.sp.gov.br/"},
        {"name": "Microsoft Teams", "url": "https://teams.microsoft.com/"},
        {"name": "Secretaria Virtual", "url": "https://bv.cps.sp.gov.br/"},
        {
            "name": "Fale Conosco",
            "url": "https://www.fatecsp.br/paginas/fale_conosco.php",
        },
    ]
    return render(request, "useful_links.html", {"links": links})
