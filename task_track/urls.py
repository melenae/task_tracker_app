"""
URL configuration for task_track project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
import debug_toolbar
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from erp_tools.api_views import (
    api_login, api_logout, api_current_user, api_dashboard,
    UserViewSet, AccountViewSet, ProjectViewSet,
    IssueViewSet, IssueCommentViewSet, CompanyViewSet,
    DatabaseViewSet, ServiceViewSet, ProjectTeamViewSet,
    ClientTeamViewSet
)

# HTML views удалены - используем только React фронтенд

# API Router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'issues', IssueViewSet, basename='issue')
router.register(r'comments', IssueCommentViewSet, basename='comment')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'databases', DatabaseViewSet, basename='database')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'project-teams', ProjectTeamViewSet, basename='project-team')
router.register(r'client-teams', ClientTeamViewSet, basename='client-team')

urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints (CSRF exempt применен в api_views.py)
    path('api/login/', api_login, name='api-login'),
    path('api/logout/', api_logout, name='api-logout'),
    path('api/current-user/', api_current_user, name='api-current-user'),
    path('api/dashboard/', api_dashboard, name='api-dashboard'),
    path('api/', include(router.urls)),
    # HTML views удалены - используем только React фронтенд
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
