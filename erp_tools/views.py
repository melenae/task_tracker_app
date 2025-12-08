from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.timezone import localtime
from django.views.decorators.http import require_http_methods
import json

from .forms import (
    AccountCreateForm,
    AdminUserCreateForm,
    AdminUserUpdateForm,
    CompanyServiceDeskForm,
    DatabaseServiceDeskForm,
    EmailLoginForm,
    EmailRegisterForm,
    ProjectCreateForm,
    ProjectTeamCreateForm,
    ProjectTeamUpdateForm,
    ServiceCreateForm,
    IssueForm,
    ClientTeamForm,
)
from .models import (
    Accounts,
    ClientTeams,
    Companies,
    DataBases,
    IssueComments,
    Issues,
    Projects,
    ProjectTeams,
    Services,
    Users,
)

CLIENT_TEAM_ALLOWED_ROLES = {
    'ProjectManager',
    'FunctionalArchitect',
    'TechnicalArchitect',
    'Analyst',
}


def refresh_permitted_accounts(profile):
    if profile.role == "admin" or (profile.auth_user and profile.auth_user.is_superuser):
        permitted_ids = list(Accounts.objects.values_list("id", flat=True))
    else:
        permitted_ids = list(Accounts.objects.filter(user=profile).values_list("id", flat=True))

    if profile.permitted_accounts != permitted_ids:
        profile.permitted_accounts = permitted_ids
        profile.save(update_fields=["permitted_accounts"])
    return permitted_ids


def login_view(request):
    login_form = EmailLoginForm(prefix="login")
    register_form = EmailRegisterForm(prefix="register")

    if request.method == "POST":
        if "login-submit" in request.POST:
            login_form = EmailLoginForm(request.POST, prefix="login")
            register_form = EmailRegisterForm(prefix="register")

            if login_form.is_valid():
                email = login_form.cleaned_data["email"].lower()
                password = login_form.cleaned_data["password"]
                user = authenticate(request, username=email, password=password)
                if user is not None:
                    login(request, user)
                    # Получаем профиль пользователя
                    profile, _ = Users.objects.get_or_create(
                        auth_user=user,
                        defaults={
                            "name": user.username,
                            "email": user.email,
                            "role": "user",
                        },
                    )
                    refresh_permitted_accounts(profile)

                    # Все пользователи идут на /projects
                    return redirect("projects")
                messages.error(request, "Неверный email или пароль.")

        elif "register-submit" in request.POST:
            register_form = EmailRegisterForm(request.POST, prefix="register")
            login_form = EmailLoginForm(prefix="login")

            if register_form.is_valid():
                email = register_form.cleaned_data["email"].lower()
                name = register_form.cleaned_data["name"]
                password = register_form.cleaned_data["password1"]

                user = User.objects.create_user(username=email, email=email, password=password)
                profile, _ = Users.objects.update_or_create(
                    auth_user=user,
                    defaults={
                        "name": name,
                        "email": email,
                        "role": "user",
                    },
                )
                login(request, user)
                refresh_permitted_accounts(profile)

                messages.success(request, "Аккаунт создан и пользователь авторизован.")
                # Все пользователи идут на /projects
                return redirect("projects")

    context = {
        "login_form": login_form,
        "register_form": register_form,
    }
    return render(request, "auth/login.html", context)


def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из профиля.")
    return redirect("login")


@login_required(login_url="login")
def accounts_view(request):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )

    permitted_ids = refresh_permitted_accounts(profile)

    if not profile.email and request.user.email:
        profile.email = request.user.email
        profile.save()

    is_admin = profile.role == "admin" or request.user.is_superuser
    manager_queryset = Users.objects.all().order_by("name") if is_admin else Users.objects.none()

    if request.method == "POST" and not is_admin:
        messages.error(request, "Недостаточно прав для создания аккаунта.")
        return redirect("accounts")

    if request.method == "POST" and is_admin:
        action = request.POST.get("form_action")
        if action == "create_account":
            form = AccountCreateForm(
                request.POST,
                is_admin=is_admin,
                manager_queryset=manager_queryset,
            )
            user_form = AdminUserCreateForm()
            if form.is_valid():
                account = form.save(commit=False)
                account.user = form.cleaned_data.get("manager") or profile
                if account.user is None:
                    messages.error(request, "Нужно выбрать управляющего.")
                    return redirect("accounts")
                account.save()
                if account.user:
                    refresh_permitted_accounts(account.user)
                messages.success(request, "Аккаунт создан.")
                return redirect("accounts")
        elif action == "create_user":
            user_form = AdminUserCreateForm(request.POST)
            form = AccountCreateForm(is_admin=is_admin, manager_queryset=manager_queryset)
            if user_form.is_valid():
                email = user_form.cleaned_data["email"].lower()
                name = user_form.cleaned_data["name"]
                phone = user_form.cleaned_data["phone"]
                password = user_form.cleaned_data["password"]
                owner = user_form.cleaned_data.get("owner")

                user = User.objects.create_user(username=email, email=email, password=password)
                new_profile, created = Users.objects.get_or_create(
                    auth_user=user,
                    defaults={
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "role": "user",
                        "owner": owner,
                    },
                )
                if not created:
                    new_profile.name = name
                    new_profile.email = email
                    new_profile.phone = phone
                    new_profile.owner = owner
                    new_profile.save()
                refresh_permitted_accounts(new_profile)
                messages.success(request, "Пользователь успешно создан.")
                return redirect("accounts")
        else:
            form = AccountCreateForm(is_admin=is_admin, manager_queryset=manager_queryset)
            user_form = AdminUserCreateForm()
    else:
        form = AccountCreateForm(is_admin=is_admin, manager_queryset=manager_queryset) if is_admin else None
        user_form = AdminUserCreateForm() if is_admin else None

    accounts = Accounts.objects.filter(pk__in=permitted_ids).order_by("-date_create")
    context = {
        "accounts": accounts,
        "form": form,
        "is_admin": is_admin,
        "managers": manager_queryset,
        "user_form": user_form,
    }
    return render(request, "accounts/list.html", context)


@login_required(login_url="login")
def account_update_view(request, pk):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    account = get_object_or_404(Accounts, pk=pk)
    is_admin = profile.role == "admin" or request.user.is_superuser
    if not is_admin and account.user_id != profile.id:
        messages.error(request, "Недостаточно прав для редактирования аккаунта.")
        return redirect("accounts")

    manager_queryset = Users.objects.all().order_by("name") if is_admin else Users.objects.filter(pk=profile.pk)
    if request.method == "POST":
        form = AccountCreateForm(
            request.POST,
            instance=account,
            is_admin=is_admin,
            manager_queryset=manager_queryset,
        )
        if form.is_valid():
            account = form.save(commit=False)
            if is_admin:
                account.user = form.cleaned_data["manager"]
            else:
                account.user = profile
            account.save()
            if account.user:
                refresh_permitted_accounts(account.user)
            messages.success(request, "Аккаунт обновлён.")
    return redirect("accounts")


@login_required(login_url="login")
def account_delete_view(request, pk):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    account = get_object_or_404(Accounts, pk=pk)
    is_admin = profile.role == "admin" or request.user.is_superuser
    if not is_admin and account.user_id != profile.id:
        messages.error(request, "Недостаточно прав для удаления аккаунта.")
        return redirect("accounts")

    if request.method == "POST":
        account_owner = account.user
        account.delete()
        if account_owner:
            refresh_permitted_accounts(account_owner)
        messages.success(request, "Аккаунт удалён.")
    return redirect("accounts")


@login_required(login_url="login")
def users_view(request):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )

    if profile.role != "admin" and not request.user.is_superuser:
        messages.error(request, "Недостаточно прав для просмотра пользователей.")
        return redirect("accounts")

    form = AdminUserCreateForm()
    if request.method == "POST":
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].lower()
            name = form.cleaned_data["name"]
            phone = form.cleaned_data["phone"]
            password = form.cleaned_data["password"]
            owner = form.cleaned_data.get("owner")

            user = User.objects.create_user(username=email, email=email, password=password)
            new_profile, created = Users.objects.get_or_create(
                auth_user=user,
                defaults={
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "role": "user",
                    "owner": owner,
                },
            )
            if not created:
                new_profile.name = name
                new_profile.email = email
                new_profile.phone = phone
                new_profile.owner = owner
                new_profile.save()
            refresh_permitted_accounts(new_profile)

            messages.success(request, "Пользователь успешно создан.")
            return redirect("users")

    users = Users.objects.select_related("auth_user").order_by("-created_at")

    context = {
        "users": users,
        "form": form,
        "update_form": AdminUserUpdateForm(),
    }
    return render(request, "users/list.html", context)


@login_required(login_url="login")
def user_update_view(request, pk):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    if profile.role != "admin" and not request.user.is_superuser:
        messages.error(request, "Недостаточно прав.")
        return redirect("users")

    user_profile = get_object_or_404(Users, pk=pk)
    if request.method == "POST":
        form = AdminUserUpdateForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            if user_profile.auth_user:
                auth_user = user_profile.auth_user
                auth_user.email = user_profile.email or auth_user.email
                auth_user.username = user_profile.email or auth_user.username
                auth_user.save()
            messages.success(request, "Пользователь обновлён.")
    return redirect("users")


@login_required(login_url="login")
def user_delete_view(request, pk):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    if profile.role != "admin" and not request.user.is_superuser:
        messages.error(request, "Недостаточно прав.")
        return redirect("users")

    user_profile = get_object_or_404(Users, pk=pk)
    if request.method == "POST":
        if user_profile.auth_user:
            user_profile.auth_user.delete()
        else:
            user_profile.delete()
        messages.success(request, "Пользователь удалён.")
    return redirect("users")


@login_required(login_url="login")
def projects_view(request):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )

    is_admin = profile.role == "admin" or request.user.is_superuser
    
    # Для админов - все проекты с возможностью редактирования
    # Для обычных пользователей - только их проекты через ProjectTeams
    if is_admin:
        account_queryset = Accounts.objects.all().order_by("name")
        form = ProjectCreateForm(account_queryset=account_queryset)

        if request.method == "POST":
            form = ProjectCreateForm(request.POST, account_queryset=account_queryset)
            if form.is_valid():
                project = form.save()
                messages.success(request, "Проект создан.")
                return redirect("projects")

        projects = (
            Projects.objects.all()
            .select_related("owner", "manager")
            .prefetch_related("project_teams__user")
            .order_by("-created_at")
        )
        for project in projects:
            project.team_members = list(project.project_teams.all())

        user_queryset = Users.objects.all().order_by("name")
        projects_with_info = None  # Для админов не нужна информация из ProjectTeams
    else:
        projects = (
            Projects.objects.filter(project_teams__user=profile)
            .select_related("owner", "manager")
            .prefetch_related("project_teams__user")
            .order_by("-created_at")
            .distinct()
        )

        user_team_lookup = {
            team.owner_id: team
            for team in ProjectTeams.objects.filter(user=profile).select_related("owner", "user")
        }

        projects_with_info = []
        for project in projects:
            project.team_members = list(project.project_teams.all())
            user_team = user_team_lookup.get(project.id)
            if user_team:
                team_info = {
                    "role": user_team.role or "Участник",
                    "topic": user_team.topic or "",
                    "job_title": user_team.job_title or "",
                    "created_at": user_team.created_at,
                }
            else:
                team_info = {
                    "role": "Участник",
                    "topic": "",
                    "job_title": "",
                    "created_at": None,
                }
            projects_with_info.append((project, team_info))

        form = None
        user_queryset = None
        account_queryset = None

    project_payload = []
    accounts_payload = []
    project_role_choices = ProjectTeams.ROLE_CHOICES
    if account_queryset is not None:
        accounts_payload = [
            {"id": account.id, "name": account.name or account.slug}
            for account in account_queryset
        ]
    for project in projects:
        team_members = []
        member_source = getattr(project, "team_members", list(project.project_teams.all()))
        for team_member in member_source:
            team_members.append(
                {
                    "id": team_member.id,
                    "user_name": (team_member.user.name if team_member.user and team_member.user.name else ""),
                    "user_email": (team_member.user.email if team_member.user and team_member.user.email else ""),
                    "role": team_member.role or "",
                    "topic": team_member.topic or "",
                    "job_title": team_member.job_title or "",
                    "created_at": localtime(team_member.created_at).strftime("%d.%m.%Y %H:%M")
                    if team_member.created_at
                    else "",
                }
            )
        project_payload.append(
            {
                "id": project.id,
                "name": project.name,
                "description": project.description or "",
                "owner_id": project.owner_id,
                "manager_id": project.manager_id if project.manager else None,
                "manager_name": (project.manager.name if project.manager and project.manager.name else "") or (project.manager.email if project.manager and project.manager.email else ""),
                "created_at": localtime(project.created_at).strftime("%d.%m.%Y %H:%M")
                if project.created_at
                else "",
                "updated_at": localtime(project.updated_at).strftime("%d.%m.%Y %H:%M")
                if project.updated_at
                else "",
                "team_members": team_members,
            }
        )

    context = {
        "projects": projects,
        "projects_with_info": projects_with_info,
        "form": form,
        "is_admin": is_admin,
        "user_queryset": user_queryset,
        "accounts": account_queryset,
        "accounts_payload": accounts_payload,
        "project_payload": project_payload,
        "project_role_choices": project_role_choices,
    }
    return render(request, "projects/list.html", context)


@login_required(login_url="login")
def project_update_view(request, pk):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    is_admin = profile.role == "admin" or request.user.is_superuser
    if not is_admin:
        messages.error(request, "Доступ запрещён.")
        return redirect("projects")

    project = get_object_or_404(Projects, pk=pk)
    account_queryset = Accounts.objects.all().order_by("name")

    if request.method == "POST":
        form = ProjectCreateForm(
            request.POST,
            instance=project,
            account_queryset=account_queryset,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Проект обновлён.")
            return redirect("projects")
    else:
        form = ProjectCreateForm(instance=project, account_queryset=account_queryset)

    return redirect("projects")


@login_required(login_url="login")
def project_delete_view(request, pk):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    is_admin = profile.role == "admin" or request.user.is_superuser
    if not is_admin:
        messages.error(request, "Доступ запрещён.")
        return redirect("projects")

    project = get_object_or_404(Projects, pk=pk)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Проект удалён.")
    return redirect("projects")


@login_required(login_url="login")
def project_team_add_view(request, project_pk):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    is_admin = profile.role == "admin" or request.user.is_superuser
    if not is_admin:
        messages.error(request, "Доступ запрещён.")
        return redirect("projects")

    project = get_object_or_404(Projects, pk=project_pk)
    user_queryset = Users.objects.all().order_by("name")

    if request.method == "POST":
        form = ProjectTeamCreateForm(request.POST, user_queryset=user_queryset)
        if form.is_valid():
            team_member = form.save(commit=False)
            team_member.owner = project
            team_member.save()
            
            # Если роль "Руководитель проекта", устанавливаем его как manager проекта
            if team_member.role == "ProjectManager" and team_member.user:
                project.manager = team_member.user
                project.save(update_fields=["manager"])
            
            messages.success(request, "Пользователь добавлен в проект.")
            return redirect("projects")
        else:
            messages.error(request, "Ошибка при добавлении пользователя.")
    return redirect("projects")


@login_required(login_url="login")
def project_team_update_view(request, project_pk, team_pk):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    is_admin = profile.role == "admin" or request.user.is_superuser
    if not is_admin:
        messages.error(request, "Доступ запрещён.")
        return redirect("projects")

    project = get_object_or_404(Projects, pk=project_pk)
    team_member = get_object_or_404(ProjectTeams, pk=team_pk, owner=project)

    if request.method == "POST":
        form = ProjectTeamUpdateForm(request.POST, instance=team_member)
        if form.is_valid():
            team_member = form.save()
            
            # Если роль изменена на "Руководитель проекта", устанавливаем его как manager проекта
            if team_member.role == "ProjectManager" and team_member.user:
                project.manager = team_member.user
                project.save(update_fields=["manager"])
            # Если роль изменена с "Руководитель проекта" на другую, сбрасываем manager если он был этим пользователем
            elif project.manager_id == team_member.user_id and team_member.role != "ProjectManager":
                # Ищем другого ProjectManager в проекте
                other_manager = ProjectTeams.objects.filter(
                    owner=project, role="ProjectManager"
                ).exclude(pk=team_member.pk).first()
                if other_manager and other_manager.user:
                    project.manager = other_manager.user
                else:
                    project.manager = None
                project.save(update_fields=["manager"])
            
            messages.success(request, "Участник проекта обновлён.")
            return redirect("projects")
    else:
        form = ProjectTeamUpdateForm(instance=team_member)
    
    return redirect("projects")


@login_required(login_url="login")
def project_team_delete_view(request, project_pk, team_pk):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    is_admin = profile.role == "admin" or request.user.is_superuser
    if not is_admin:
        messages.error(request, "Доступ запрещён.")
        return redirect("projects")

    project = get_object_or_404(Projects, pk=project_pk)
    team_member = get_object_or_404(ProjectTeams, pk=team_pk, owner=project)

    if request.method == "POST":
        # Если удаляемый участник был manager проекта, сбрасываем manager
        if project.manager_id == team_member.user_id:
            # Ищем другого ProjectManager в проекте
            other_manager = ProjectTeams.objects.filter(
                owner=project, role="ProjectManager"
            ).exclude(pk=team_member.pk).first()
            if other_manager and other_manager.user:
                project.manager = other_manager.user
            else:
                project.manager = None
            project.save(update_fields=["manager"])
        
        team_member.delete()
        messages.success(request, "Участник удалён из проекта.")
    
    return redirect("projects")


def is_project_manager(user_profile, project):
    """Проверяет, является ли пользователь менеджером проекта"""
    if not user_profile or not project:
        return False
    return project.manager_id == user_profile.id


@login_required(login_url="login")
def project_companies_view(request, project_pk):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    project = get_object_or_404(Projects, pk=project_pk)
    is_manager = is_project_manager(profile, project) or request.user.is_superuser
    
    if not is_manager:
        messages.error(request, "Недостаточно прав для просмотра компаний.")
        return redirect("projects")
    
    from .forms import CompanyCreateForm
    
    form = CompanyCreateForm()
    if request.method == "POST":
        if not is_manager:
            messages.error(request, "Недостаточно прав для создания компании.")
            return redirect("projects")

        form = CompanyCreateForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.owner = project
            company.applicant = profile
            company.save()
            messages.success(request, "Компания создана.")
            return redirect("project-companies", project_pk=project_pk)
    
    companies = Companies.objects.filter(owner=project).order_by("-date_create")
    context = {
        "companies": companies,
        "form": form,
        "project": project,
        "can_edit": is_manager,
    }
    return render(request, "companies/list.html", context)


@login_required(login_url="login")
def project_databases_view(request, project_pk):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    project = get_object_or_404(Projects, pk=project_pk)
    is_manager = is_project_manager(profile, project) or request.user.is_superuser
    
    if not is_manager:
        messages.error(request, "Недостаточно прав для просмотра баз данных.")
        return redirect("projects")
    
    from .forms import DatabaseCreateForm
    
    form = DatabaseCreateForm()
    if request.method == "POST":
        if not is_manager:
            messages.error(request, "Недостаточно прав для создания базы данных.")
            return redirect("projects")

        form = DatabaseCreateForm(request.POST)
        if form.is_valid():
            database = form.save(commit=False)
            database.owner = project
            database.save()
            messages.success(request, "База данных создана.")
            return redirect("project-databases", project_pk=project_pk)
    
    databases = DataBases.objects.filter(owner=project).order_by("-date_create")
    context = {
        "databases": databases,
        "form": form,
        "project": project,
        "can_edit": is_manager,
    }
    return render(request, "databases/list.html", context)


@login_required(login_url="login")
def service_desk_companies_view(request):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    managed_projects = Projects.objects.filter(manager=profile)
    can_edit = request.user.is_superuser or managed_projects.exists()
    if request.user.is_superuser:
        project_queryset = Projects.objects.all().order_by("name")
    else:
        project_queryset = managed_projects.order_by("name")

    form = CompanyServiceDeskForm(project_queryset=project_queryset) if can_edit else None

    if request.method == "POST":
        if not can_edit:
            messages.error(request, "Недостаточно прав для добавления компании.")
            return redirect("companies")
        form = CompanyServiceDeskForm(request.POST, project_queryset=project_queryset)
        if form.is_valid():
            company = form.save(commit=False)
            company.applicant = profile
            company.save()
            messages.success(request, "Компания создана.")
            # Сохраняем фильтр при редиректе (из POST или GET)
            project_param = request.POST.get("filter_project") or request.GET.get("project", "")
            if project_param:
                return redirect(f"{reverse('companies')}?project={project_param}")
            return redirect("companies")

    # Получаем все проекты для фильтра
    all_projects = Projects.objects.all().order_by("name")
    
    # Фильтрация по проекту
    selected_project_id = request.GET.get("project")
    companies = Companies.objects.select_related("owner", "applicant").order_by("-date_create")
    if selected_project_id:
        try:
            selected_project_id = int(selected_project_id)
            companies = companies.filter(owner_id=selected_project_id)
        except (ValueError, TypeError):
            selected_project_id = None
    
    context = {
        "companies": companies,
        "form": form,
        "can_edit": can_edit,
        "project": None,
        "all_projects": all_projects,
        "selected_project_id": selected_project_id,
    }
    return render(request, "companies/list.html", context)


@login_required(login_url="login")
def company_client_teams_view(request, company_pk):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    company = get_object_or_404(Companies, pk=company_pk)
    project = company.owner

    can_create = request.user.is_superuser
    if not can_create and project:
        can_create = ProjectTeams.objects.filter(
            owner=project,
            user=profile,
            role__in=CLIENT_TEAM_ALLOWED_ROLES,
        ).exists()

    teams = (
        ClientTeams.objects.filter(company=company)
        .select_related("user")
        .order_by("-date_create")
    )

    if request.method == "POST":
        if not can_create:
            messages.error(request, "Недостаточно прав для добавления участника.")
            return redirect("company-client-teams", company_pk=company_pk)
        form = ClientTeamForm(request.POST)
        if form.is_valid():
            client_team = form.save(commit=False)
            client_team.company = company
            client_team.save()
            messages.success(request, "Участник рабочей группы добавлен.")
            return redirect("company-client-teams", company_pk=company_pk)
    else:
        form = ClientTeamForm()

    context = {
        "company": company,
        "project": project,
        "teams": teams,
        "form": form,
        "can_create": can_create,
        "allowed_roles": CLIENT_TEAM_ALLOWED_ROLES,
    }
    return render(request, "client_teams/list.html", context)
@login_required(login_url="login")
def service_desk_databases_view(request):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    managed_projects = Projects.objects.filter(manager=profile)
    can_edit = request.user.is_superuser or managed_projects.exists()
    if request.user.is_superuser:
        project_queryset = Projects.objects.all().order_by("name")
    else:
        project_queryset = managed_projects.order_by("name")

    form = DatabaseServiceDeskForm(project_queryset=project_queryset) if can_edit else None

    if request.method == "POST":
        if not can_edit:
            messages.error(request, "Недостаточно прав для добавления базы данных.")
            return redirect("databases")
        form = DatabaseServiceDeskForm(request.POST, project_queryset=project_queryset)
        if form.is_valid():
            database = form.save()
            messages.success(request, "База данных создана.")
            # Сохраняем фильтр при редиректе (из POST или GET)
            project_param = request.POST.get("filter_project") or request.GET.get("project", "")
            if project_param:
                return redirect(f"{reverse('databases')}?project={project_param}")
            return redirect("databases")

    # Получаем все проекты для фильтра
    all_projects = Projects.objects.all().order_by("name")
    
    # Фильтрация по проекту
    selected_project_id = request.GET.get("project")
    databases = DataBases.objects.select_related("owner").order_by("-date_create")
    if selected_project_id:
        try:
            selected_project_id = int(selected_project_id)
            databases = databases.filter(owner_id=selected_project_id)
        except (ValueError, TypeError):
            selected_project_id = None
    
    context = {
        "databases": databases,
        "form": form,
        "can_edit": can_edit,
        "project": None,
        "all_projects": all_projects,
        "selected_project_id": selected_project_id,
    }
    return render(request, "databases/list.html", context)


@login_required(login_url="login")
def services_view(request):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    managed_projects = Projects.objects.filter(manager=profile)
    managed_project_ids = list(managed_projects.values_list("id", flat=True))
    can_edit = request.user.is_superuser or bool(managed_project_ids)

    # Показываем все компании для выбора, проверка прав будет при сохранении
    company_queryset = Companies.objects.select_related("owner").order_by("name")
    user_queryset = Users.objects.all().order_by("name")

    form = ServiceCreateForm(company_queryset=company_queryset, user_queryset=user_queryset) if can_edit else None

    if request.method == "POST":
        if not can_edit:
            messages.error(request, "Недостаточно прав для добавления услуги.")
            return redirect("services")
        form = ServiceCreateForm(
            request.POST,
            company_queryset=company_queryset,
            user_queryset=user_queryset,
        )
        if form.is_valid():
            service = form.save(commit=False)
            if not request.user.is_superuser and service.company and service.company.owner_id not in managed_project_ids:
                messages.error(request, "Вы можете добавлять услуги только к своим проектам.")
            else:
                service.save()
                messages.success(request, "Услуга создана.")
                # Сохраняем фильтр при редиректе (из POST или GET)
                project_param = request.POST.get("filter_project") or request.GET.get("project", "")
                if project_param:
                    return redirect(f"{reverse('services')}?project={project_param}")
                return redirect("services")

    # Получаем все проекты для фильтра
    all_projects = Projects.objects.all().order_by("name")
    
    # Фильтрация по проекту
    selected_project_id = request.GET.get("project")
    services = (
        Services.objects.select_related("company", "company__owner", "user", "supervisor", "applicant")
        .order_by("-date_create")
    )
    if selected_project_id:
        try:
            selected_project_id = int(selected_project_id)
            services = services.filter(company__owner_id=selected_project_id)
        except (ValueError, TypeError):
            selected_project_id = None
    
    context = {
        "services": services,
        "form": form,
        "can_edit": can_edit,
        "all_projects": all_projects,
        "selected_project_id": selected_project_id,
    }
    return render(request, "services/list.html", context)


@login_required(login_url="login")
def issues_view(request):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    issues = (
        Issues.objects.select_related(
            "Companies",
            "Companies__owner",
            "DataBases",
            "Services",
            "Services__company",
            "users",
            "applicant_content_type",
            "supervisor",
        ).order_by("-date_create")
    )

    all_projects = Projects.objects.all().order_by("name")
    selected_project_id = request.GET.get("project")
    if selected_project_id:
        try:
            selected_project_id = int(selected_project_id)
            issues = issues.filter(
                Q(Companies__owner_id=selected_project_id)
                | Q(DataBases__owner_id=selected_project_id)
                | Q(Services__company__owner_id=selected_project_id)
            )
        except (ValueError, TypeError):
            selected_project_id = None

    # Определяем режим отображения (table или kanban)
    view_mode = request.GET.get("view", "table")
    if view_mode not in ["table", "kanban"]:
        view_mode = "table"
    
    # Группируем заявки по статусам для канбан-доски
    issues_by_status = []
    if view_mode == "kanban":
        for status_code, status_label in Issues.STATUS_CHOICES:
            status_issues = [issue for issue in issues if issue.status == status_code]
            issues_by_status.append({
                "code": status_code,
                "label": status_label,
                "issues": status_issues,
                "count": len(status_issues)
            })
    
    context = {
        "issues": issues,
        "all_projects": all_projects,
        "selected_project_id": selected_project_id,
        "view_mode": view_mode,
        "issues_by_status": issues_by_status,
        "status_choices": Issues.STATUS_CHOICES,
    }
    return render(request, "issues/list.html", context)


@login_required(login_url="login")
def issue_create_view(request):
    return _issue_form_view(request)


@login_required(login_url="login")
def issue_detail_view(request, pk):
    issue = get_object_or_404(Issues, pk=pk)
    return _issue_form_view(request, issue)


def _issue_form_view(request, issue=None):
    profile, _ = Users.objects.get_or_create(
        auth_user=request.user,
        defaults={
            "name": request.user.username,
            "email": request.user.email,
            "role": "user",
        },
    )
    parent_queryset = Issues.objects.exclude(pk=issue.pk) if issue else Issues.objects.all()

    if request.method == "POST":
        form = IssueForm(request.POST, instance=issue, parent_queryset=parent_queryset)
        if form.is_valid():
            # Сохраняем старый статус для проверки изменения
            old_status = issue.status if issue and issue.pk else None
            
            comment_text = form.cleaned_data.get("comment", "").strip()
            
            # Если будет создан комментарий, устанавливаем флаг ДО сохранения заявки
            if comment_text and issue:
                issue._creating_comment_with_update = True
            
            issue = form.save()
            new_status = issue.status
            
            # Если статус изменился, комментарий обязателен (проверка уже в форме)
            # Создаем комментарий, если он указан
            if comment_text:
                # Для новых заявок устанавливаем флаг после создания
                if not hasattr(issue, '_creating_comment_with_update'):
                    issue._creating_comment_with_update = True
                IssueComments.objects.create(
                    issue=issue,
                    user=profile,
                    comment=comment_text,
                )
            
            # Если статус изменился, но комментарий не был указан (не должно произойти из-за валидации)
            if old_status and new_status != old_status and not comment_text:
                messages.warning(request, "Статус изменен, но комментарий не был добавлен.")
            
            messages.success(request, "Заявка сохранена.")
            return redirect("issue-detail", pk=issue.pk)
    else:
        form = IssueForm(instance=issue, parent_queryset=parent_queryset)

    context = {
        "form": form,
        "issue": issue,
        "comments": IssueComments.objects.filter(issue=issue).select_related("user") if issue else [],
    }
    return render(request, "issues/detail.html", context)


@login_required(login_url="login")
@require_http_methods(["POST"])
def issue_update_status_view(request, pk):
    """AJAX endpoint для обновления статуса заявки через drag and drop"""
    try:
        issue = get_object_or_404(Issues, pk=pk)
        profile, _ = Users.objects.get_or_create(
            auth_user=request.user,
            defaults={
                "name": request.user.username,
                "email": request.user.email,
                "role": "user",
            },
        )
        
        data = json.loads(request.body)
        new_status = data.get("status")
        comment_text = data.get("comment", "").strip()
        
        if not new_status:
            return JsonResponse({"success": False, "error": "Статус не указан"}, status=400)
        
        # Проверяем, что статус валидный
        valid_statuses = [choice[0] for choice in Issues.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return JsonResponse({"success": False, "error": "Недопустимый статус"}, status=400)
        
        old_status = issue.status
        
        # Если статус не изменился, возвращаем успех
        if old_status == new_status:
            return JsonResponse({"success": True})
        
        # Проверяем, что комментарий указан (обязателен при изменении статуса)
        if not comment_text:
            return JsonResponse({"success": False, "error": "Комментарий обязателен при изменении статуса"}, status=400)
        
        # Обновляем статус
        issue.status = new_status
        # Устанавливаем флаг ДО сохранения, чтобы issue_post_save отложил отправку
        issue._creating_comment_with_update = True
        issue.save()
        
        # Создаем комментарий с указанным текстом
        try:
            status_labels = dict(Issues.STATUS_CHOICES)
            old_label = status_labels.get(old_status, old_status)
            new_label = status_labels.get(new_status, new_status)
            
            # Формируем полный текст комментария
            full_comment = f"Статус изменен с '{old_label}' на '{new_label}' через канбан-доску.\n{comment_text}"
            
            IssueComments.objects.create(
                issue=issue,
                user=profile,
                comment=full_comment,
            )
        except Exception as comment_error:
            # Если не удалось создать комментарий, это не критично - статус уже обновлен
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Не удалось создать комментарий для заявки {issue.pk}: {comment_error}")
        
        return JsonResponse({"success": True})
        
    except json.JSONDecodeError as e:
        return JsonResponse({"success": False, "error": "Неверный формат данных: " + str(e)}, status=400)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка при обновлении статуса заявки {pk}: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": "Внутренняя ошибка сервера: " + str(e)}, status=500)


