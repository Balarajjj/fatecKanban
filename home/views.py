from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Task


@login_required
def home_view(request):
    projects = Project.objects.filter(owner=request.user).order_by("-updated_at")
    return render(request, "home/index.html", {"projects": projects})


@login_required
def project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    tasks = {
        "TD": project.task_set.filter(status="TD"),
        "DG": project.task_set.filter(status="DG"),
        "CO": project.task_set.filter(status="CO"),
    }
    return render(request, "home/projects.html", {"project": project, "tasks": tasks})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        messages.error(request, "Usuário ou senha incorretos")
    return render(request, "registration/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")
