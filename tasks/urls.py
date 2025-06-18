from django.urls import path
from .views import (
    TaskCreateView,
    TaskUpdateView,
    TaskDeleteView,
    TaskStatusUpdateView,  # Corrigido para a view que você tem
)

urlpatterns = [
    path("task/<int:pk>/editar/", TaskUpdateView.as_view(), name="task-update"),
    path("task/<int:pk>/excluir/", TaskDeleteView.as_view(), name="task-delete"),
    path("task/criar/<int:project_id>/", TaskCreateView.as_view(), name="task-create"),
    path("task/<int:pk>/move/", TaskStatusUpdateView.as_view(), name="task-move"),
]
