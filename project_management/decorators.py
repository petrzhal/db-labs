from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from project_management.repositories.user_repository import UserRepository
from django.conf import settings
from functools import wraps

user_repository = UserRepository(settings.DATABASE_CONNECTION_STRING)

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_id = request.session.get('user_id')
            if not user_id:
                return redirect('login')

            user_role = user_repository.get_user_role(user_id)
            if not user_role or user_role.name not in allowed_roles:
                return HttpResponseForbidden("У вас нет доступа к этой странице")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')

        user = user_repository.get_user_by_id(user_id)
        if not user:
            request.session.flush()  
            return redirect('login')  

        return view_func(request, *args, **kwargs)
    return _wrapped_view
