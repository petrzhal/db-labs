from project_management.repositories.user_repository import UserRepository
from project_manager import settings

user_repository = UserRepository(settings.DATABASE_CONNECTION_STRING)

def user_context(request):
    user = user_repository.get_user_by_id(request.session.get('user_id'))
    if not user:
        return []
    return {
        'user_id': user.id,
        'username': user.username,
        'role_id': user.role_id if hasattr(user, "role_id") else None,
    }