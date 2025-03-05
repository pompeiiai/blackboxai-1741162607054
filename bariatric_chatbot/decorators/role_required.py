from functools import wraps
from flask import abort, current_app
from flask_login import current_user

def role_required(roles):
    """
    Decorator to check if the current user has any of the required roles.
    
    Args:
        roles (list or str): A list of role names or a single role name
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            
            # Convert single role to list
            required_roles = roles if isinstance(roles, list) else [roles]
            
            # Check if user has any of the required roles
            if not any(current_user.has_role(role) for role in required_roles):
                abort(403)  # Forbidden
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(permissions):
    """
    Decorator to check if the current user has all required permissions.
    
    Args:
        permissions (list or str): A list of permission names or a single permission name
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            
            # Convert single permission to list
            required_permissions = permissions if isinstance(permissions, list) else [permissions]
            
            # Super admin has all permissions
            if current_user.has_role('super_admin'):
                return f(*args, **kwargs)
            
            # Check if user has all required permissions
            if not all(current_user.has_permission(perm) for perm in required_permissions):
                abort(403)  # Forbidden
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorator to check if the current user is an admin or super admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)  # Unauthorized
            
        if not (current_user.has_role('admin') or current_user.has_role('super_admin')):
            abort(403)  # Forbidden
            
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """
    Decorator to check if the current user is a super admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)  # Unauthorized
            
        if not current_user.has_role('super_admin'):
            abort(403)  # Forbidden
            
        return f(*args, **kwargs)
    return decorated_function
