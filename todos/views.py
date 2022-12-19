from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import TaskForm
from .models import Task

@login_required
def get_index(request):
    context = {}
    if request.user.is_authenticated:
        context['todos'] = request.user.owned_tasks.all()
    return render(request, 'todos/index.html', context)

@login_required
def create_task(request):
    form = TaskForm()
    if request.method == "POST":
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid:
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            return redirect('index')
    return render(request, 'todos/task-form.html', {'form': form})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'todos/task-detail.html', {'task': task})
