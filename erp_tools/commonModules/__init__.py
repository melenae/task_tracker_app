"""
Common modules for ERP Tools application
"""

from .cm_access_management import (
    get_users_roles,
    is_system_admin,
    get_access_to_object
)

__all__ = [
    'get_users_roles',
    'is_system_admin',
    'get_access_to_object',
]



