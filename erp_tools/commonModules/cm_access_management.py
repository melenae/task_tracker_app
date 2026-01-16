from typing import List, Dict, Any, Optional
from django.contrib.auth.models import User
from erp_tools.models import Users, Projects, ProjectTeams, Accounts

# Интерпретация кода 1С - ниже
def get_users_roles(project: Projects, user: Users) -> List[str]:
    """
    Получить список ролей пользователя в проекте
    
    Args:
        project: Проект
        user: Пользователь
        
    Returns:
        Список ролей пользователя в проекте
    """
    if not project or not user:
        return []
    
    roles = ProjectTeams.objects.filter(
        owner=project,
        user=user
    ).values_list('role', flat=True)
    
    return [role for role in roles if role]  # Убираем None значения


def is_system_admin(user: Users) -> bool:
    """
    Проверить, является ли пользователь администратором системы
    
    Args:
        user: Пользователь
        
    Returns:
        True если пользователь администратор или суперпользователь
    """
    if not user:
        return False
    
    # Проверяем роль в модели Users
    if user.role == 'admin':
        return True
    
    # Проверяем Django superuser
    if user.auth_user and user.auth_user.is_superuser:
        return True
    
    return False


def get_access_to_object(
    user: Users,
    project: Optional[Projects],
    object_type: str,
    reference: Optional[Any] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Получить права доступа пользователя к объекту в проекте
    
    Args:
        user: Пользователь
        project: Проект
        object_type: Тип объекта (AccessPermissions, Issues, Companies, и т.д.)
        reference: Ссылка на объект (опционально)
        params: Дополнительные параметры (опционально)
        
    Returns:
        Словарь с правами доступа:
        {
            'only_reading': bool,  # Только чтение
            'read_only': bool,      # Только просмотр (для формы)
            'can_edit': bool,       # Может редактировать
            'can_create': bool,     # Может создавать
            'can_delete': bool,     # Может удалять
            'element_permissions': {}  # Права на отдельные элементы
        }
    """
    if params is None:
        params = {}
    
    # Инициализация результата
    result = {
        'only_reading': True,
        'read_only': True,
        'can_edit': False,
        'can_create': False,
        'can_delete': False,
        'element_permissions': {}
    }
    
    # Если проект не указан, возвращаем только чтение
    if not project:
        return result
    
    # Если пользователь - администратор системы, полный доступ
    if is_system_admin(user):
        result['only_reading'] = False
        result['read_only'] = False
        result['can_edit'] = True
        result['can_create'] = True
        result['can_delete'] = True
        return result
    
    # Получаем роли пользователя в проекте
    user_roles = get_users_roles(project, user)
    
    # Обработка по типам объектов
    if object_type == "AccessPermissions":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'TechnicalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Analyst' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "Analitics":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "Accounts":
        # Если пользователь является владельцем аккаунта проекта
        if project.owner and project.owner.user == user:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "Attributes":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "Backlogs":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "ClientTeams":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
            result['can_create'] = True
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
            result['can_create'] = True
        elif 'TechnicalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
            result['can_create'] = True
        elif 'Analyst' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
            result['can_create'] = True
    
    elif object_type == "Companies":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
            result['can_create'] = True
    
    elif object_type == "ComplexServices":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
            result['can_create'] = True
    
    elif object_type == "DataBases":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
            result['can_create'] = True
    
    elif object_type == "DataSet":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'TechnicalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Analyst' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "DataUploads":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'TechnicalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Analyst' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "DevObjects":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'TechnicalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Analyst' in user_roles:
            # Только просмотр для Analyst
            pass
        elif 'Developer' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "Features":
        # Специальная логика для Features с дополнительными правами на элементы
        element_perms = {}
        
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
            element_perms['feature_status'] = {'enabled': True}
            element_perms['sprint'] = {'read_only': False}
            element_perms['FeatureIssuesHistory'] = {'read_only': False, 'visible': True}
            element_perms['initial_estimation'] = {'read_only': False}
            element_perms['dev_hours_plan'] = {'read_only': False}
            element_perms['nondev_hours_plan'] = {'read_only': False}
            element_perms['deploy_hours_plan'] = {'read_only': False}
            element_perms['reserve_hours_plan'] = {'read_only': False}
            element_perms['FeatureTechnicalSpecificationdone'] = {'enabled': True}
            
            # Логика в зависимости от статуса feature
            if reference and hasattr(reference, 'feature_status'):
                feature_status = getattr(reference, 'feature_status', None)
                if feature_status == 'not_agreed':
                    element_perms['gap'] = {'enabled': True}
                    element_perms['to_fa'] = {'enabled': True}
                elif feature_status == 'agreed_by_client':
                    element_perms['to_fa'] = {'enabled': False}
                    element_perms['fa_ok'] = {'enabled': True}
                elif feature_status == 'agreed_by_func_arch':
                    element_perms['pm_ok'] = {'enabled': True}
        
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
            element_perms['FeatureIssuesHistory'] = {'visible': True}
            
            if reference and hasattr(reference, 'feature_status'):
                feature_status = getattr(reference, 'feature_status', None)
                if feature_status == 'not_agreed':
                    element_perms['gap'] = {'enabled': True}
                    element_perms['to_fa'] = {'enabled': True}
                elif feature_status == 'agreed_by_client':
                    element_perms['to_fa'] = {'enabled': False}
                    # Дополнительная проверка ФА по данному топику
                    # if ФАПоДанномуТопику(ФормаЭл.объект, user):
                    element_perms['fa_ok'] = {'enabled': True}
        
        elif 'TechnicalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
            element_perms['FeatureIssuesHistory'] = {'visible': True}
            element_perms['FeatureTechnicalSpecificationdone'] = {'enabled': True}
        
        elif 'Analyst' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
            element_perms['FeatureIssuesHistory'] = {'visible': True}
            
            if reference and hasattr(reference, 'feature_status'):
                feature_status = getattr(reference, 'feature_status', None)
                if feature_status == 'not_agreed':
                    element_perms['to_fa'] = {'enabled': True}
                    element_perms['gap'] = {'enabled': True}
        
        elif 'Developer' in user_roles:
            element_perms['FeatureTechnicalSpecificationdone'] = {'enabled': True}
        
        elif 'Client' in user_roles:
            if reference and hasattr(reference, 'applicant'):
                applicant = getattr(reference, 'applicant', None)
                if applicant == user:
                    element_perms['to_fa'] = {'enabled': True}
        
        result['element_permissions'] = element_perms
    
    elif object_type == "FlowDiagrams":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'TechnicalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Analyst' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Tester' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "Functions":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Analyst' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "Instructions":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Analyst' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Tester' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "Issues":
        # Специальная логика для Issues
        if len(user_roles) == 0:
            # У пользователя нет прав на проект, но заявки он видит
            result['only_reading'] = True
            result['read_only'] = False
            return result
        
        # Права на редактирование для большинства ролей
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
            result['element_permissions'] = {
                'IssueComplexRoutes': {'visible': True, 'read_only': False},
                'complex_service': {'read_only': False},
                'cs_start': {'enabled': True},
            }
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'TechnicalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Analyst' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Developer' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Tester' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Clerk' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'OnlyIssues' in user_roles:
            # Специальная обработка для OnlyIssues
            # Устанавливаем разрешенных пользователей из параметров
            # (логика с permitted_users из 1С)
            if params:
                permitted_users = params.get('permitted_users', [])
                if 'applicant' in params and params['applicant']:
                    if params['applicant'] not in permitted_users:
                        permitted_users.append(params['applicant'])
                if 'user' in params and params['user']:
                    if params['user'] not in permitted_users:
                        permitted_users.append(params['user'])
                if 'supervisor' in params and params['supervisor']:
                    if params['supervisor'] not in permitted_users:
                        permitted_users.append(params['supervisor'])
                
                result['permitted_users'] = permitted_users
                
                if 'feature' in params and params['feature']:
                    permitted_features = params.get('permitted_features', [])
                    if params['feature'] not in permitted_features:
                        permitted_features.append(params['feature'])
                    result['permitted_features'] = permitted_features
    
    elif object_type == "MetadataObjects":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'TechnicalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Analyst' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Developer' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "Procedures":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Analyst' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "ProjectLogs":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Analyst' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Developer' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Client' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Tester' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Clerk' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "ProjectLogType":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "Projects":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "RoadMapChapters":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "Services":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'TechnicalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "Topics":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Analyst' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "UploadTemplates":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'FunctionalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'TechnicalArchitect' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Analyst' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Developer' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "RoadMaps":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
        elif 'Clerk' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    elif object_type == "Sprints":
        if 'ProjectManager' in user_roles:
            result['only_reading'] = False
            result['read_only'] = False
            result['can_edit'] = True
    
    return result

