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
from django.urls import include,path

from erp_tools.views import (
    account_delete_view,
    account_update_view,
    accounts_view,
    login_view,
    logout_view,
    project_companies_view,
    project_databases_view,
    project_delete_view,
    project_team_add_view,
    project_team_delete_view,
    project_team_update_view,
    project_update_view,
    projects_view,
    service_desk_companies_view,
    service_desk_databases_view,
    services_view,
    issues_view,
    company_client_teams_view,
    issue_detail_view,
    issue_create_view,
    issue_update_status_view,
    user_delete_view,
    user_update_view,
    users_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('accounts/', accounts_view, name='accounts'),
    path('accounts/<int:pk>/update/', account_update_view, name='account-update'),
    path('accounts/<int:pk>/delete/', account_delete_view, name='account-delete'),
    path('users/', users_view, name='users'),
    path('users/<int:pk>/update/', user_update_view, name='user-update'),
    path('users/<int:pk>/delete/', user_delete_view, name='user-delete'),
    path('projects/', projects_view, name='projects'),
    path('projects/<int:pk>/update/', project_update_view, name='project-update'),
    path('projects/<int:pk>/delete/', project_delete_view, name='project-delete'),
    path('projects/<int:project_pk>/team/add/', project_team_add_view, name='project-team-add'),
    path('projects/<int:project_pk>/team/<int:team_pk>/update/', project_team_update_view, name='project-team-update'),
    path('projects/<int:project_pk>/team/<int:team_pk>/delete/', project_team_delete_view, name='project-team-delete'),
    path('projects/<int:project_pk>/companies/', project_companies_view, name='project-companies'),
    path('projects/<int:project_pk>/databases/', project_databases_view, name='project-databases'),
    path('companies/', service_desk_companies_view, name='companies'),
    path('databases/', service_desk_databases_view, name='databases'),
    path('services/', services_view, name='services'),
    path('issues/', issues_view, name='issues'),
    path('issues/create/', issue_create_view, name='issue-create'),
    path('issues/<int:pk>/', issue_detail_view, name='issue-detail'),
    path('companies/<int:company_pk>/client-teams/', company_client_teams_view, name='company-client-teams'),
    path('issues/<int:pk>/update-status/', issue_update_status_view, name='issue-update-status'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
