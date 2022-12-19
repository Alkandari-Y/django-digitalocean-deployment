from django import forms

from todos.models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ('owner',)