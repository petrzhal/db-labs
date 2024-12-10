from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
import psycopg2
from project_management.repositories.user_repository import UserRepository
from project_management.repositories.log_repository import LogRepository
from project_management.repositories.project_repository import ProjectRepository
from project_management.repositories.status_repository import StatusRepository
from project_management.repositories.task_repository import TaskRepository
from project_management.repositories.task_assignment_repository import TaskAssignmentRepository
from project_management.repositories.file_repository import FileRepository
from project_management.repositories.comment_repository import CommentRepository
from project_manager import settings
from .decorators import login_required, role_required
from .models import User, Project, File, Task
from django.contrib import messages
from datetime import datetime
from  project_management.view_models import *
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST

user_repository = UserRepository(settings.DATABASE_CONNECTION_STRING)
log_repository = LogRepository(settings.DATABASE_CONNECTION_STRING)
project_repository = ProjectRepository(settings.DATABASE_CONNECTION_STRING)
status_repository = StatusRepository(settings.DATABASE_CONNECTION_STRING)
task_repository = TaskRepository(settings.DATABASE_CONNECTION_STRING)
task_assignment_repository = TaskAssignmentRepository(settings.DATABASE_CONNECTION_STRING)
file_repository = FileRepository(settings.DATABASE_CONNECTION_STRING)
comment_repository = CommentRepository(settings.DATABASE_CONNECTION_STRING)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = user_repository.get_user_by_username(username)

        if user and check_password(password, user.password):
            request.session['user_id'] = user.id
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Неправильное имя пользователя или пароль'})

    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        phone = request.POST.get('phone', None)
        address = request.POST.get('address', None)
        birthday = request.POST.get('birthday', None)
        
        existing_user = user_repository.get_user_by_username(username)
        if existing_user:
            return render(request, 'register.html', {'error': 'Пользователь с таким именем уже существует'})

        user_repository.create_user_with_profile(username, email, make_password(password), "User", phone, address, birthday)
        return render(request, 'login.html', {'error': 'Регистрация прошла успешно! Вы можете войти в систему.'})

    return render(request, 'register.html')


def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('home')


@login_required
def home(request):    
    user_id = request.session.get('user_id')
    username = user_repository.get_user_by_id(user_id).username
    role = user_repository.get_user_role(user_id).id

    logs = log_repository.get_latest_logs()
    user_tasks = task_repository.get_user_tasks(user_id)
    user_projects = project_repository.get_user_projects(user_id)

    task_view_models = []
    for task in user_tasks:
        assigned_to_users = []
        user_ids = task_assignment_repository.get_assignments_by_task_id(task.id)
        for user_id in user_ids:
            assigned_to_users.append(user_repository.get_user_by_id(user_id).username)
            
        assigned_users = set()
        for user in assigned_to_users:
            if user:
                assigned_users.add(user)
            
        priority = task_repository.get_priority_by_id(task.priority_id).name
        status = status_repository.get_status_by_id(task.status_id).name
        task_vm = TaskViewModel(
            id=task.id,
            name=task.name,
            description=task.description,
            project_id=task.project_id,
            priority=priority,
            status=status,
            due_date=task.due_date,
            assigned_to=list(assigned_users)
        )
        task_view_models.append(task_vm)
    
    context = {
        'username': username,
        'role': role,
        'logs': logs,
        'tasks': task_view_models,
        'projects': user_projects,
    }
    return render(request, 'home.html', context)



@login_required
def profile(request):
    user_id = request.session.get('user_id')
    user = user_repository.get_user_by_id(user_id)
    profile = user_repository.get_user_profile(user_id)
    context = {
        'username': user.username,
        'email': user.email,
        'phone': profile.phone,
        'address': profile.address,
        'birthday': profile.birthday,
        'role_id': user.role_id,
    }

    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    user = user_repository.get_user_by_id(request.session.get('user_id'))
    profile = user_repository.get_user_profile(user.id)

    if request.method == 'POST':
        username = request.POST.get('username', user.username)
        email = request.POST.get('email', user.email)
        phone = request.POST.get('phone', profile.phone)
        address = request.POST.get('address', profile.address)
        birthday = request.POST.get('birthday', profile.birthday)

        user_repository.update_user(
            user_id=user.id,
            username=username,
            email=email
        )
        
        user_repository.update_user_profile(
            user_id=user.id,
            phone=phone,
            address=address,
            birthday=birthday
        )

        return redirect('profile')

    context = {
        'user': user,
        'profile': profile
    }
    return render(request, 'edit_profile.html', context)

@role_required(["Admin"])
def manage_users(request):
    users = user_repository.get_all_users()
    return render(request, 'user_management.html', {'users': users})

@role_required(["Admin"])
def edit_user(request, user_id):
    user = user_repository.get_user_by_id(user_id)

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.role = int(request.POST.get("role"))
        user_repository.update_user(
            user_id=user.id,
            username=user.username,
            email=user.email,
            role_id=user.role_id
        )
        return redirect("manage_users")

    return render(request, "edit_user.html", {"user": user})


@role_required(["Admin"])
def add_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        birthday = request.POST.get("birthday")

        if user_repository.get_user_by_username(username):
            messages.error(request, "Имя пользователя уже занято.")
            return render(request, "add_user.html")
        
        if user_repository.get_user_by_email(email):
            messages.error(request, "Этот email уже используется.")
            return render(request, "add_user.html")

        try:
            user_repository.create_user_with_profile(
                username=username,
                email=email,
                password=password,
                role_name=role,
                phone=phone,
                address=address,
                birthday=birthday,
            )
            messages.success(request, f"Пользователь {username} успешно добавлен.")
            return redirect("manage_users")
        except Exception as e:
            messages.error(request, f"Ошибка при добавлении пользователя: {str(e)}")
    
    return render(request, "add_user.html")


@role_required(["Admin"])
def delete_user(request, user_id):
    try:
        user_repository.delete_user(user_id)
        messages.success(request, "Пользователь успешно удалён.")
    except Exception as e:
        messages.error(request, f"Ошибка при удалении пользователя: {str(e)}")
    return redirect("manage_users")


@login_required
def projects(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    user_id = request.session.get('user_id')
    role = user_repository.get_user_role(user_id)
    
    if role.name == "Admin":
        projects = project_repository.get_all_projects()
    else:
        projects = project_repository.get_user_projects(user_id)

    project_view_models = []
    for project in projects:        
        manager_name = user_repository.get_user_by_id(project.manager_id).username
        status = status_repository.get_status_by_id(project.status_id).name
        
        view_model = ProjectViewModel(
            id=project.id,
            name=project.name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            status=status,
            manager=manager_name
        )
        project_view_models.append(view_model)

    if search_query:
        project_view_models = [vm for vm in project_view_models if search_query.lower() in vm.name.lower()]

    if status_filter:
        if status_filter == "open":
            project_view_models = [vm for vm in project_view_models if vm.status == "Open"]
        elif status_filter == "in-progress":
            project_view_models = [vm for vm in project_view_models if vm.status == "In Progress"]
        elif status_filter == "closed":
            project_view_models = [vm for vm in project_view_models if vm.status == "Closed"]

    return render(request, 'projects.html', {
        'projects': project_view_models,
        'search_query': search_query,
        'status_filter': status_filter,
        'role_id': role.id,
        'user_id': user_id,
    })


@login_required
def project_detail(request, project_id):
    project = project_repository.get_project_by_id(project_id)
    if project is None:
        messages.error(request, 'Проект не найден.')
        return redirect('projects')

    tasks = task_repository.get_tasks_by_project(project_id)
    
    task_view_models = []
    for task in tasks:
        assigned_to_users = []
        user_ids = task_assignment_repository.get_assignments_by_task_id(task.id)
        for user_id in user_ids:
            assigned_to_users.append(user_repository.get_user_by_id(user_id).username)
            
        assigned_users = set()
        for user in assigned_to_users:
            if user:
                assigned_users.add(user)
            
        priority = task_repository.get_priority_by_id(task.priority_id).name
        status = status_repository.get_status_by_id(task.status_id).name
        task_vm = TaskViewModel(
            id=task.id,
            name=task.name,
            description=task.description,
            project_id=task.project_id,
            priority=priority,
            status=status,
            due_date=task.due_date,
            assigned_to=list(assigned_users)
        )
        task_view_models.append(task_vm)

    members = project_repository.get_project_members(project_id)
    all_users = user_repository.get_all_users()
    manager = user_repository.get_user_by_id(project.manager_id).username
    status = status_repository.get_status_by_id(project.status_id).name
    vm = ProjectDetailsViewModel(
        id=project.id,
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date,
        status=status,
        manager=manager,
        tasks=task_view_models,
        members=members,
        all_users=all_users
    )

    user_id = request.session.get('user_id')
    user_role = user_repository.get_user_role(user_id).name
    is_manager = user_role in ["Admin", "Manager"]

    return render(request, 'project_detail.html', {
        "vm": vm,
        "is_manager": is_manager,
    })


@role_required(["Admin", "Project Manager"])
@login_required
def create_project(request):
    users = user_repository.get_all_users()

    if request.method == 'POST':
        project_name = request.POST.get('name')
        project_description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        manager_id = request.POST.get('manager_id')

        if not all([project_name, start_date, end_date, manager_id]):
            messages.error(request, 'Все обязательные поля должны быть заполнены.')
            return render(request, 'create_project.html', {'users': users})

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            messages.error(request, 'Неверный формат даты. Используйте YYYY-MM-DD.')
            return render(request, 'create_project.html', {'users': users})

        status_name = "Open"
        status_id = status_repository.get_status_by_name(status_name).id
        
        project_repository.add_project(project_name, project_description, start_date, end_date, status_id, manager_id)
        messages.success(request, 'Проект успешно создан.')
        return redirect('projects')

    return render(request, 'create_project.html', {'users': users})


@role_required(["Admin", "Project Manager"])
@login_required
def edit_project(request, project_id):
    project = project_repository.get_project_by_id(project_id)
    if not project:
        messages.error(request, 'Проект не найден.')
        return redirect('projects')

    statuses = status_repository.get_all_statuses() 
    managers = user_repository.get_all_users()  

    if request.method == 'POST':
        project_name = request.POST.get('name')
        project_description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        status_name = request.POST.get('status')
        manager_id = request.POST.get('manager') 
        
        status_id = status_repository.get_status_by_name(status_name).id

        if not all([project_name, start_date, end_date, status_name, manager_id]):
            messages.error(request, 'Все обязательные поля должны быть заполнены.')
            return render(request, 'edit_project.html', {
                'project': project,
                'statuses': statuses,
                'managers': managers,
            })

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            messages.error(request, 'Неверный формат даты. Используйте YYYY-MM-DD.')
            return render(request, 'edit_project.html', {
                'project': project,
                'statuses': statuses,
                'managers': managers,
            })

        project_repository.update_project(
            project_id,
            name=project_name,
            description=project_description,
            start_date=start_date,
            end_date=end_date,
            status_id=status_id,
            manager_id=manager_id 
        )
        messages.success(request, 'Проект успешно обновлён.')
        return redirect('projects')

    return render(request, 'edit_project.html', {
        'project': project,
        'statuses': statuses,
        'managers': managers,
    })



@role_required(["Admin"])
@login_required
def delete_project(request, project_id):
    project_repository.delete_project_with_dependencies(project_id)
    messages.success(request, 'Проект успешно удалён.')
    return redirect('projects')


@login_required
@role_required(['Admin', 'Project Manager'])
def add_task(request, project_id):
    if request.method == 'POST':
        task_name = request.POST['task_name']
        task_description = request.POST['task_description']
        task_status = request.POST['task_status']
        task_priority = request.POST['priority_id']
        due_date = request.POST.get('due_date')
        uploaded_files = request.FILES.getlist('files')

        task = task_repository.create_task(
            name=task_name,
            description=task_description,
            project_id=project_id,
            priority_id=task_priority,
            status_id=task_status,
            due_date=due_date
        )

        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_path = f'media/tasks/{task}/{file_name}'

            import os
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            file = File(
                id=None,
                task_id=task,
                file_name=file_name,
                file_path=f'/media/tasks/{task}/{file_name}',
                uploaded_date=None
            )
            file_repository.add_file(file)

        messages.success(request, 'Задача успешно добавлена!')
        return redirect('project_detail', project_id=project_id)

    users = user_repository.get_all_users()
    statuses = status_repository.get_all_statuses()
    priorities = task_repository.get_all_priorities()
    attached_files = []

    vm = AddTaskViewModel(users, statuses, priorities, attached_files)

    return render(request, 'task_add.html', {'model': vm})



@login_required
def delete_file(request, file_id):
    file = TaskFileRepository.delete_file_by_id(file_id)
    if file:
        messages.success(request, 'Файл успешно удален!')
    else:
        messages.error(request, 'Файл не найден!')
    return HttpResponseRedirect(reverse('task_add'))


@login_required
@role_required(['Admin', 'Project Manager'])
def assign_task(request, project_id, task_id):
    task = task_repository.get_task_by_id(task_id)
    print(task)
    if not task:
        messages.error(request, 'Задача не найдена.')
        return redirect('project_detail', project_id=project_id)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')

        user = user_repository.get_user_by_id(user_id)
        if not user:
            messages.error(request, 'Пользователь не найден.')
            return redirect('project_detail', project_id=project_id)

        try:
            task_assignment_repository.assign_task_to_user(task_id, user_id)
            messages.success(request, f'Задача успешно назначена пользователю {user.username}.')
        except Exception as e:
            messages.error(request, f'Ошибка при назначении задачи: {str(e)}')

        return redirect('project_detail', project_id=project_id)
    
    users = user_repository.get_all_users()
    return render(request, 'assign_task.html', {
        'task': task,
        'users': users,
        'project_id': project_id,
    })



def task_details(request, task_id):
    task = task_repository.get_task_by_id(task_id)
    files = file_repository.get_files_by_task_id(task_id)
    file_data = [{"name": f.file_name, "url": f.file_path} for f in files]
    status_name = status_repository.get_status_by_id(task.status_id).name
    priority_name = task_repository.get_priority_by_id(task.priority_id).name
    all_priorities = task_repository.get_all_priorities()
    
    assigned_to_users = []
    user_ids = task_assignment_repository.get_assignments_by_task_id(task.id)
    for user_id in user_ids:
        assigned_to_users.append(user_repository.get_user_by_id(user_id).username)
        
    assigned_users = set()
    for user in assigned_to_users:
        if user:
            assigned_users.add(user)
    
    vm = TaskDetailsViewModel(
        id=task.id,
        name=task.name,
        description=task.description,
        status=status_name,  
        priority=priority_name,
        all_priorities=[p.name for p in all_priorities],
        due_date=task.due_date.strftime("%Y-%m-%d"),
        files=file_data,
        assigned_to=list(assigned_users)
    )
        
    return JsonResponse(vm.__dict__)


from django.shortcuts import redirect
from django.http import JsonResponse

@require_POST
def task_edit(request, task_id):
    name = request.POST.get('name')
    description = request.POST.get('description')
    status_id = request.POST.get('status') 
    priority_id = request.POST.get('priority')
    due_date = request.POST.get('due_date')
    
    task = task_repository.get_task_by_id(task_id)
    if not task:
        return JsonResponse({'success': False, 'message': 'Task not found.'}, status=404)

    task.name = name
    task.description = description
    task.status_id = status_id
    task.priority_id = priority_id
    task.due_date = due_date
    
    status_id = status_repository.get_status_by_name(task.status_id).id
    priority_id = task_repository.get_priority_by_name(task.priority_id).id

    if task_repository.update_task(task.id, task.name, task.description, priority_id, status_id, task.due_date):
        if 'new_files' in request.FILES:
            for uploaded_file in request.FILES.getlist('new_files'):
                file_name = uploaded_file.name
                file_path = f'media/tasks/{task.id}/{file_name}'

                import os
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, 'wb') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                file_instance = File(   
                    id=None,
                    task_id=task, 
                    file_name=file_name,
                    file_path=f'/media/tasks/{task.id}/{file_name}',
                    uploaded_date=None 
                )
                file_repository.add_file(file_instance)

        return redirect('project_detail', project_id=task.project_id) 
    else:
        return JsonResponse({'success': False, 'message': 'Failed to update task.'}, status=500)


@login_required
@role_required(['Admin', 'Project Manager'])
def delete_task(request, task_id):
    task = task_repository.get_task_by_id(task_id)

    if task is None:
        messages.error(request, 'Задача не найдена.')
        return redirect('projects')

    project_id = task.project_id
    task_repository.delete_task(task_id)
    messages.success(request, 'Задача успешно удалена.')
    return redirect('project_detail', project_id=project_id)


@login_required
def comments(request, task_id):
    user_id = request.session.get('user_id')
    task = task_repository.get_task_by_id(task_id)
    raw_comments = comment_repository.get_comments_by_task_id(task_id)

    comments = [
        CommentViewModel(
            user=user_repository.get_user_by_id(comment.user_id),
            text=comment.text,  
            publication_date=comment.publication_date 
        ) for comment in raw_comments
    ]

    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        if comment_text:
            comment_repository.add_comment(task_id, user_id, comment_text)
            return redirect('comments', task_id=task.id)

    context = {
        'task': task,
        'comments': comments,
        'project_id': task.project_id,
    }
    return render(request, 'comments.html', context)


@role_required(['Admin'])
def logs(request):
    logs = log_repository.get_all_logs()
    
    context = {
        'logs': logs,
    }
    
    return render(request, 'logs.html', context)