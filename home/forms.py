from django import forms
from tasks.models import Task
from .models import Project


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task

        fields = ["title", "due_date", "status", "assigned_to"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm "
                    "focus:outline-none focus:ring-2 focus:ring-fatec-red focus:border-fatec-red",
                    "placeholder": "Título da tarefa",
                }
            ),
            "due_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "autocomplete": "off",
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white "
                    "focus:outline-none focus:ring-2 focus:ring-fatec-red focus:border-fatec-red",
                }
            ),
            "assigned_to": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white "
                    "focus:outline-none focus:ring-2 focus:ring-fatec-red focus:border-fatec-red"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].empty_label = "Selecione um membro"
        self.fields["assigned_to"].label = "Atribuir a"
        if project:
            self.fields["assigned_to"].queryset = project.members.all()


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "status", "members", "start_date", "end_date"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-fatecRed focus:border-fatecRed",
                    "placeholder": "Nome do projeto",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm resize-y min-h-[120px] focus:outline-none focus:ring-2 focus:ring-fatecRed focus:border-fatecRed",
                    "placeholder": "Descreva brevemente o projeto",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white focus:outline-none focus:ring-2 focus:ring-fatecRed focus:border-fatecRed"
                }
            ),
            "members": forms.SelectMultiple(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white focus:outline-none focus:ring-2 focus:ring-fatecRed focus:border-fatecRed"
                }
            ),
            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white focus:outline-none focus:ring-2 focus:ring-fatecRed focus:border-fatecRed",
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white focus:outline-none focus:ring-2 focus:ring-fatecRed focus:border-fatecRed",
                }
            ),
        }
