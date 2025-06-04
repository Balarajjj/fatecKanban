from django.urls import path
from .views import (
    home_view,
    project_view,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    useful_links_view,
    dashboard_home,
)

urlpatterns = [
    path("", home_view, name="home"),
    path("projeto/novo/", ProjectCreateView.as_view(), name="project-create"),
    path("projeto/<int:project_id>/", project_view, name="project"),
    path(
        "projeto/<int:pk>/editar/", ProjectUpdateView.as_view(), name="project-update"
    ),
    path(
        "projeto/<int:pk>/excluir/", ProjectDeleteView.as_view(), name="project-delete"
    ),
    path("links/", useful_links_view, name="useful-links"),
    path("dashboard/", dashboard_home, name="dashboard_home"),
]
