from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.utils import timezone
from collections import Counter
import json
from django.core.serializers.json import DjangoJSONEncoder

from .models import Project
from tasks.models import Task
from .forms import TaskForm, ProjectForm


User = get_user_model()


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
    user = request.user

    # Buscar todos os projetos onde o usuário é owner ou membro
    projetos_do_usuario = Project.objects.filter(
        Q(owner=user) | Q(members=user)
    ).distinct()

    # Buscar apenas as tarefas desses projetos
    tasks_dos_projetos = Task.objects.filter(project__in=projetos_do_usuario)

    # Tarefas ordenadas por vencimento (futuras e não concluídas)
    upcoming_tasks = (
        tasks_dos_projetos.filter(due_date__gte=timezone.now().date())
        .exclude(status="CO")
        .order_by("due_date")[:5]
    )

    # Status geral dessas tarefas
    status_counts = Counter(tasks_dos_projetos.values_list("status", flat=True))

    # Convertendo para nomes legíveis
    status_display = {
        "TD": "A Fazer",
        "DG": "Em Progresso",
        "CO": "Concluídas",
    }
    status_data = {status_display.get(k, k): v for k, v in status_counts.items()}

    # Top 3 projetos com mais tarefas (dentro dos projetos do usuário)
    top_projects = sorted(
        projetos_do_usuario, key=lambda p: p.tasks.count(), reverse=True
    )[:3]

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


@login_required
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

    # Cálculo da barra de progresso
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
        "progress": progress,
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
        response = super().form_valid(form)

        members_ids_csv = self.request.POST.get("members_ids", "")
        members_ids = members_ids_csv.split(",") if members_ids_csv else []

        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Adiciona o dono como membro
        members = User.objects.filter(id__in=members_ids)
        self.object.members.set(list(members) + [self.request.user])

        return response

    def get_success_url(self):
        return reverse_lazy("home")


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "home/project_form.html"
    success_url = reverse_lazy("home")
    MAX_MEMBERS = 10  # exemplo de limite

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)

        members_ids_str = self.request.POST.get("members_ids", "")
        if members_ids_str:
            members_ids = [int(i) for i in members_ids_str.split(",") if i.isdigit()]
            if len(members_ids) > self.MAX_MEMBERS:
                form.add_error(
                    None, f"Limite máximo de {self.MAX_MEMBERS} membros por projeto."
                )
                return self.form_invalid(form)
            self.object.members.set(members_ids)

        return response


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
@require_GET
def user_search_api(request):
    """API para buscar usuários via query string 'q'"""
    q = request.GET.get("q", "")
    results = []
    if q:
        users = (
            User.objects.filter(
                Q(username__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
            )
            .exclude(id=request.user.id)  # opcional: não mostrar o próprio usuário
            .order_by("username")[:10]
        )
        results = [
            {
                "id": user.id,
                "username": user.username,
                "full_name": f"{user.first_name} {user.last_name}".strip(),
            }
            for user in users
        ]
    return JsonResponse({"results": results})


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
