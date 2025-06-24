from django import forms
from .models import Task


from django import forms
from tasks.models import Task


class TaskEditForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "due_date", "priority", "assigned_to"]
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
                },
                format="%Y-%m-%d",  # importante para carregar valor inicial
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

        # Aqui garantimos que as datas e valores do modelo sejam usados no form
        if self.instance and self.instance.pk:
            self.fields["due_date"].initial = self.instance.due_date
            self.fields["priority"].initial = self.instance.priority
            self.fields["title"].initial = self.instance.title
            self.fields["assigned_to"].initial = self.instance.assigned_to


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "status", "priority", "due_date", "assigned_to"]
        widgets = {
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
