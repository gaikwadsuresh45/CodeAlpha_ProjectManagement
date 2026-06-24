from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Project, Task, Comment


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    projects = Project.objects.filter(members=request.user) | Project.objects.filter(created_by=request.user)
    projects = projects.distinct()
    return render(request, 'dashboard.html', {'projects': projects})


@login_required
def create_project(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        project = Project.objects.create(
            name=name,
            description=description,
            created_by=request.user
        )
        project.members.add(request.user)
        return redirect('project_detail', pk=project.pk)
    return render(request, 'create_project.html')


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    todo_tasks = project.tasks.filter(status='todo')
    inprogress_tasks = project.tasks.filter(status='inprogress')
    done_tasks = project.tasks.filter(status='done')
    users = User.objects.all()
    return render(request, 'project_detail.html', {
        'project': project,
        'todo_tasks': todo_tasks,
        'inprogress_tasks': inprogress_tasks,
        'done_tasks': done_tasks,
        'users': users,
    })


@login_required
def create_task(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        assigned_to_id = request.POST.get('assigned_to')
        assigned_to = User.objects.get(pk=assigned_to_id) if assigned_to_id else None
        Task.objects.create(
            project=project,
            title=title,
            description=description,
            assigned_to=assigned_to,
            status='todo'
        )
        return redirect('project_detail', pk=pk)
    return redirect('project_detail', pk=pk)


@login_required
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.status = request.POST.get('status')
        task.save()
    return redirect('project_detail', pk=task.project.pk)


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Comment.objects.create(task=task, author=request.user, text=text)
    return render(request, 'task_detail.html', {'task': task})