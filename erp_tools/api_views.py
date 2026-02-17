"""
API Views for React Frontend
Using Django REST Framework
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import (
    Users, Accounts, Projects, Issues, IssueComments,
    Companies, DataBases, Services, ProjectTeams, ClientTeams
)
from .serializers import (
    UserSerializer, AccountSerializer, ProjectSerializer,
    IssueSerializer, IssueCommentSerializer, CompanySerializer,
    DatabaseSerializer, ServiceSerializer, ProjectTeamSerializer,
    ClientTeamSerializer
)
# Импортируем функцию напрямую, чтобы избежать циклических импортов
def refresh_permitted_accounts(profile):
    """Обновляет список разрешенных аккаунтов для пользователя"""
    from .models import Accounts
    if profile.role == "admin" or (profile.auth_user and profile.auth_user.is_superuser):
        permitted_ids = list(Accounts.objects.values_list("id", flat=True))
    else:
        permitted_ids = list(Accounts.objects.filter(user=profile).values_list("id", flat=True))
    
    if profile.permitted_accounts != permitted_ids:
        profile.permitted_accounts = permitted_ids
        profile.save(update_fields=["permitted_accounts"])
    return permitted_ids


@csrf_exempt
@api_view(['POST'])
@permission_classes([])
def api_login(request):
    """API endpoint for user login"""
    email = request.data.get('email', '').lower()
    password = request.data.get('password', '')
    
    if not email or not password:
        return Response(
            {'error': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            # Выполняем логин ДО создания профиля, чтобы сессия была установлена
            login(request, user)
            
            # Создаем или получаем профиль пользователя (не критично для логина)
            try:
                erp_user = Users.objects.filter(auth_user=user).first()
                if not erp_user:
                    erp_user = Users.objects.create(
                        auth_user=user,
                        name=user.username or '',
                        email=user.email or '',
                        role='user',
                    )
                # Обновляем permitted_accounts в фоне (не критично)
                try:
                    refresh_permitted_accounts(erp_user)
                except Exception:
                    pass  # Игнорируем ошибки обновления permitted_accounts
            except Exception:
                pass  # Игнорируем ошибки создания профиля - логин все равно успешен
            
            return Response({
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username
                }
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        # Логируем любую другую ошибку
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Login error: {e}", exc_info=True)
        return Response(
            {'error': f'Login failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """API endpoint for user logout"""
    logout(request)
    return Response({'success': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_current_user(request):
    """Get current authenticated user"""
    try:
        erp_user = Users.objects.get(auth_user=request.user)
        # Обновляем permitted_accounts
        refresh_permitted_accounts(erp_user)
        serializer = UserSerializer(erp_user)
        return Response(serializer.data)
    except Users.DoesNotExist:
        # Создаем профиль если его нет
        erp_user = Users.objects.create(
            auth_user=request.user,
            name=request.user.username,
            email=request.user.email,
            role='user',
        )
        refresh_permitted_accounts(erp_user)
        serializer = UserSerializer(erp_user)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_dashboard(request):
    """Get dashboard statistics and data"""
    try:
        profile = Users.objects.get(auth_user=request.user)
        refresh_permitted_accounts(profile)
        permitted_ids = profile.permitted_accounts or []
        
        # Базовый queryset для задач
        if profile.role == "admin" or (profile.auth_user and profile.auth_user.is_superuser):
            issues_queryset = Issues.objects.all()
            projects_queryset = Projects.objects.all()
        elif permitted_ids:
            issues_queryset = Issues.objects.filter(
                Q(companies__owner_id__in=permitted_ids) |
                Q(databases__owner_id__in=permitted_ids) |
                Q(services__company__owner_id__in=permitted_ids) |
                Q(owner__owner_id__in=permitted_ids) |
                Q(users=profile) |
                Q(supervisor=profile)
            ).distinct()
            projects_queryset = Projects.objects.filter(
                Q(owner_id__in=permitted_ids) |
                Q(manager=profile)
            ).distinct()
        else:
            issues_queryset = Issues.objects.all()
            projects_queryset = Projects.objects.filter(manager=profile)
        
        # Статистика по задачам
        stats = {
            'total': issues_queryset.count(),
            'new': issues_queryset.filter(status='new').count(),
            'in_progress': issues_queryset.filter(status='in_progress').count(),
            'done': issues_queryset.filter(status='done').count(),
            'overdue': issues_queryset.filter(
                deadline__lt=timezone.now(),
                status__in=['new', 'in_progress', 'waiting', 'testing']
            ).count(),
        }
        
        # Мои задачи (назначенные на текущего пользователя)
        my_issues = issues_queryset.filter(users=profile).select_related(
            'companies', 'users', 'supervisor', 'owner'
        ).order_by('-date_create')[:7]
        my_issues_data = IssueSerializer(my_issues, many=True).data
        
        # Активные проекты
        active_projects = projects_queryset.select_related('owner', 'manager').order_by('-created_at')[:7]
        projects_data = []
        for project in active_projects:
            # Задачи связаны с проектом через Companies, DataBases, Services
            project_issues = issues_queryset.filter(
                Q(companies__owner=project) |
                Q(databases__owner=project) |
                Q(services__company__owner=project) |
                Q(owner=project)
            ).distinct()
            total_issues = project_issues.count()
            done_issues = project_issues.filter(status='done').count()
            projects_data.append({
                **ProjectSerializer(project).data,
                'total_issues': total_issues,
                'done_issues': done_issues,
                'progress': (done_issues / total_issues * 100) if total_issues > 0 else 0,
            })
        
        # Недавние задачи (последние измененные)
        recent_issues = issues_queryset.select_related(
            'companies', 'users', 'supervisor', 'owner'
        ).order_by('-date_create')[:7]
        recent_issues_data = IssueSerializer(recent_issues, many=True).data
        
        return Response({
            'stats': stats,
            'my_issues': my_issues_data,
            'active_projects': projects_data,
            'recent_issues': recent_issues_data,
        })
    except Users.DoesNotExist:
        return Response({
            'stats': {'total': 0, 'new': 0, 'in_progress': 0, 'done': 0, 'overdue': 0},
            'my_issues': [],
            'active_projects': [],
            'recent_issues': [],
        })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in api_dashboard: {e}", exc_info=True)
        return Response(
            {'error': f'Ошибка загрузки данных: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for Users"""
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet for Accounts"""
    queryset = Accounts.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Фильтруем аккаунты по permitted_accounts и менеджеру"""
        try:
            profile = Users.objects.get(auth_user=self.request.user)
            refresh_permitted_accounts(profile)
            permitted_ids = profile.permitted_accounts or []
            
            # Если админ или суперпользователь - показываем все
            if profile.role == "admin" or (profile.auth_user and profile.auth_user.is_superuser):
                return Accounts.objects.select_related('user').all().order_by('-date_create')
            
            # Если есть permitted_accounts - фильтруем
            if permitted_ids:
                # Показываем аккаунты где:
                # 1. аккаунт в permitted_accounts
                # 2. user (менеджер) = текущий пользователь
                return Accounts.objects.filter(
                    Q(pk__in=permitted_ids) |
                    Q(user=profile)
                ).select_related('user').distinct().order_by('-date_create')
            else:
                # Если нет permitted_accounts, показываем аккаунты где пользователь менеджер
                return Accounts.objects.filter(user=profile).select_related('user').order_by('-date_create')
        except Users.DoesNotExist:
            # Если профиля нет, показываем пустой список
            return Accounts.objects.none()


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for Projects"""
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Фильтруем проекты по permitted_accounts и менеджеру"""
        try:
            profile = Users.objects.get(auth_user=self.request.user)
            refresh_permitted_accounts(profile)
            permitted_ids = profile.permitted_accounts or []
            
            # Если админ или суперпользователь - показываем все
            if profile.role == "admin" or (profile.auth_user and profile.auth_user.is_superuser):
                return Projects.objects.select_related('owner', 'manager').order_by('-created_at')
            
            # Если есть permitted_accounts - фильтруем
            if permitted_ids:
                # Показываем проекты где:
                # 1. owner в permitted_accounts
                # 2. manager = текущий пользователь
                return Projects.objects.filter(
                    Q(owner_id__in=permitted_ids) |
                    Q(manager=profile)
                ).select_related('owner', 'manager').distinct().order_by('-created_at')
            else:
                # Если нет permitted_accounts, показываем проекты где пользователь менеджер
                return Projects.objects.filter(manager=profile).select_related('owner', 'manager').order_by('-created_at')
        except Users.DoesNotExist:
            return Projects.objects.none()


class IssueViewSet(viewsets.ModelViewSet):
    """ViewSet for Issues"""
    queryset = Issues.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """Переопределяем list для обработки ошибок"""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in IssueViewSet.list: {e}", exc_info=True)
            from rest_framework.response import Response
            from rest_framework import status
            return Response(
                {'error': f'Ошибка загрузки задач: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_queryset(self):
        """Фильтруем задачи по permitted_accounts через проекты и пользователя"""
        try:
            profile = Users.objects.get(auth_user=self.request.user)
            refresh_permitted_accounts(profile)
            permitted_ids = profile.permitted_accounts or []
            
            # Если админ или суперпользователь - показываем все
            if profile.role == "admin" or (profile.auth_user and profile.auth_user.is_superuser):
                queryset = Issues.objects.select_related(
                    'companies', 'databases', 'services', 'users', 'supervisor', 'owner'
                ).prefetch_related('comments').order_by('-date_create')
            elif permitted_ids:
                # Фильтруем задачи:
                # 1. Через связанные проекты (Companies, DataBases, Services)
                # 2. Где пользователь является исполнителем (users)
                # 3. Где пользователь является супервайзером (supervisor)
                queryset = Issues.objects.filter(
                    Q(companies__owner_id__in=permitted_ids) |
                    Q(databases__owner_id__in=permitted_ids) |
                    Q(services__company__owner_id__in=permitted_ids) |
                    Q(owner__owner_id__in=permitted_ids) |
                    Q(users=profile) |
                    Q(supervisor=profile)
                ).select_related(
                    'companies', 'databases', 'services', 'users', 'supervisor', 'owner'
                ).prefetch_related('comments').distinct().order_by('-date_create')
            else:
                # Если нет permitted_accounts, показываем все задачи (как в HTML views)
                # Пользователь может видеть задачи, где он:
                # - исполнитель
                # - супервайзер
                # - или все задачи (если система позволяет)
                queryset = Issues.objects.select_related(
                    'companies', 'databases', 'services', 'users', 'supervisor', 'owner'
                ).prefetch_related('comments').order_by('-date_create')
            
            # Дополнительная фильтрация по параметрам
            project_id = self.request.query_params.get('project', None)
            status_filter = self.request.query_params.get('status', None)
            
            if project_id:
                queryset = queryset.filter(
                    Q(companies__owner_id=project_id) |
                    Q(databases__owner_id=project_id) |
                    Q(services__company__owner_id=project_id) |
                    Q(owner_id=project_id)
                )
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            return queryset
        except Users.DoesNotExist:
            # Если профиля нет, показываем пустой список
            return Issues.objects.none()


class IssueCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Issue Comments"""
    queryset = IssueComments.objects.all()
    serializer_class = IssueCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = IssueComments.objects.all()
        issue_id = self.request.query_params.get('issue', None)
        
        if issue_id:
            queryset = queryset.filter(issue_id=issue_id)
        
        return queryset


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for Companies"""
    queryset = Companies.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Фильтруем компании по permitted_accounts и заявителю"""
        try:
            profile = Users.objects.get(auth_user=self.request.user)
            refresh_permitted_accounts(profile)
            permitted_ids = profile.permitted_accounts or []
            
            # Если админ или суперпользователь - показываем все
            if profile.role == "admin" or (profile.auth_user and profile.auth_user.is_superuser):
                return Companies.objects.select_related('owner', 'applicant').order_by('-date_create')
            
            # Если есть permitted_accounts - фильтруем
            if permitted_ids:
                # Показываем компании где:
                # 1. owner (проект) в permitted_accounts
                # 2. applicant = текущий пользователь
                return Companies.objects.filter(
                    Q(owner_id__in=permitted_ids) |
                    Q(applicant=profile)
                ).select_related('owner', 'applicant').distinct().order_by('-date_create')
            else:
                # Если нет permitted_accounts, показываем компании где пользователь заявитель
                return Companies.objects.filter(applicant=profile).select_related('owner', 'applicant').order_by('-date_create')
        except Users.DoesNotExist:
            return Companies.objects.none()


class DatabaseViewSet(viewsets.ModelViewSet):
    """ViewSet for DataBases"""
    queryset = DataBases.objects.all()
    serializer_class = DatabaseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Фильтруем базы данных по permitted_accounts"""
        try:
            profile = Users.objects.get(auth_user=self.request.user)
            refresh_permitted_accounts(profile)
            permitted_ids = profile.permitted_accounts or []
            
            # Если админ или суперпользователь - показываем все
            if profile.role == "admin" or (profile.auth_user and profile.auth_user.is_superuser):
                return DataBases.objects.select_related('owner').order_by('-date_create')
            
            # Если есть permitted_accounts - фильтруем
            if permitted_ids:
                # Показываем базы данных где owner (проект) в permitted_accounts
                return DataBases.objects.filter(owner_id__in=permitted_ids).select_related('owner').order_by('-date_create')
            else:
                # Если нет permitted_accounts, показываем все (как в HTML views)
                return DataBases.objects.select_related('owner').order_by('-date_create')
        except Users.DoesNotExist:
            return DataBases.objects.none()


class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Services"""
    queryset = Services.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Фильтруем услуги по permitted_accounts через компании и пользователя"""
        try:
            profile = Users.objects.get(auth_user=self.request.user)
            refresh_permitted_accounts(profile)
            permitted_ids = profile.permitted_accounts or []
            
            # Если админ или суперпользователь - показываем все
            if profile.role == "admin" or (profile.auth_user and profile.auth_user.is_superuser):
                return Services.objects.select_related('company', 'user', 'applicant', 'supervisor').order_by('-date_create')
            
            # Если есть permitted_accounts - фильтруем
            if permitted_ids:
                # Показываем услуги где:
                # 1. company.owner (проект) в permitted_accounts
                # 2. user (ответственный) = текущий пользователь
                # 3. applicant (заявитель) = текущий пользователь
                # 4. supervisor (контролер) = текущий пользователь
                return Services.objects.filter(
                    Q(company__owner_id__in=permitted_ids) |
                    Q(user=profile) |
                    Q(applicant=profile) |
                    Q(supervisor=profile)
                ).select_related('company', 'user', 'applicant', 'supervisor').distinct().order_by('-date_create')
            else:
                # Если нет permitted_accounts, показываем услуги где пользователь связан
                return Services.objects.filter(
                    Q(user=profile) |
                    Q(applicant=profile) |
                    Q(supervisor=profile)
                ).select_related('company', 'user', 'applicant', 'supervisor').distinct().order_by('-date_create')
        except Users.DoesNotExist:
            return Services.objects.none()


class ProjectTeamViewSet(viewsets.ModelViewSet):
    """ViewSet for Project Teams"""
    queryset = ProjectTeams.objects.all()
    serializer_class = ProjectTeamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ProjectTeams.objects.all()
        project_id = self.request.query_params.get('project', None)
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset


class ClientTeamViewSet(viewsets.ModelViewSet):
    """ViewSet for Client Teams"""
    queryset = ClientTeams.objects.all()
    serializer_class = ClientTeamSerializer
    permission_classes = [IsAuthenticated]

