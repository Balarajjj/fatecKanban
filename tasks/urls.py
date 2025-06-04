from django.urls import path
from .views import TaskCreateView
from tasks.views import TaskUpdateView, TaskDeleteView

urlpatterns = [
    path("task/<int:pk>/editar/", TaskUpdateView.as_view(), name="task-update"),
    path("task/<int:pk>/excluir/", TaskDeleteView.as_view(), name="task-delete"),
    path("criar/<int:project_id>/", TaskCreateView.as_view(), name="task-create"),
]
