import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from django.utils.dateparse import parse_datetime
from erp_tools.models import Issues, Companies, Services, DataBases, Users, Sprints, ClientTeams
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


def create_issue_from_1c(issue_data: Dict[str, Any]) -> Optional[Issues]:
    """Создать заявку из данных 1С"""
    logger.info(f"=== create_issue_from_1c called ===")
    logger.info(f"Full issue_data: {json.dumps(issue_data, ensure_ascii=False, default=str, indent=2)}")
    
    # Маппинг полей от 1C к Django (1C использует другие названия)
    # 1C: Content -> Django: content
    # 1C: Новая -> Django: new
    # 1C: Regular -> Django: medium
    # 1C: dead_line -> Django: deadline
    
    # Обработка content (1C использует "Content" с большой буквы)
    content = issue_data.get('Content') or issue_data.get('content', '')
    name = issue_data.get('name', 'Заявка из 1С')
    
    # Маппинг статусов от 1C к Django
    status_1c = issue_data.get('status', 'Новая')
    status_mapping = {
        'Новая': 'new',
        'В работе': 'in_progress',
        'Решена': 'resolved',
        'Закрыта': 'closed',
    }
    status = status_mapping.get(status_1c, 'new')
    
    # Маппинг приоритетов от 1C к Django
    priority_1c = issue_data.get('priority', 'Regular')
    priority_mapping = {
        'Low': 'low',
        'Regular': 'medium',
        'High': 'high',
        'Critical': 'critical',
    }
    priority = priority_mapping.get(priority_1c, 'medium')
    
    # Обработка deadline (1C использует "dead_line" или "deadline")
    deadline = None
    deadline_str = issue_data.get('dead_line') or issue_data.get('deadline')
    if deadline_str and deadline_str != "0001-01-01T00:00:00":
        logger.info(f"Processing deadline: {deadline_str} (type: {type(deadline_str)})")
        if isinstance(deadline_str, str):
            deadline = parse_datetime(deadline_str)
            logger.info(f"Parsed deadline from string: {deadline}")
        elif isinstance(deadline_str, datetime):
            deadline = deadline_str
            logger.info(f"Using deadline as datetime: {deadline}")
    
    logger.info(f"Creating issue with:")
    logger.info(f"  name: '{name}'")
    logger.info(f"  content: '{content[:50]}...' (length: {len(content)})")
    logger.info(f"  status: '{status}' (from 1C: '{status_1c}')")
    logger.info(f"  priority: '{priority}' (from 1C: '{priority_1c}')")
    logger.info(f"  deadline: {deadline}")
    
    issue = Issues(
        name=name,
        content=content,
        status=status,
        priority=priority,
        deadline=deadline,
    )
    
    # Обработка external_id (если приходит от 1С)
    if issue_data.get('external_id'):
        external_id = issue_data['external_id']
        logger.info(f"Checking for existing issue with external_id: '{external_id}'")
        # Проверяем, не существует ли уже заявка с таким external_id
        existing_issue = Issues.objects.filter(external_id=external_id).first()
        if existing_issue:
            logger.warning(f"⚠ Issue with external_id '{external_id}' already exists (ID: {existing_issue.pk}). Skipping creation.")
            return existing_issue
        issue.external_id = external_id
        logger.info(f"Set external_id: '{external_id}'")
    else:
        logger.info(f"No external_id provided, will be auto-generated")
    
    # Поиск связанных объектов по ID
    if issue_data.get('company_id'):
        try:
            issue.Companies = Companies.objects.get(pk=issue_data['company_id'])
        except Companies.DoesNotExist:
            logger.warning(f"Company {issue_data['company_id']} not found")
    
    if issue_data.get('service_id'):
        try:
            issue.Services = Services.objects.get(pk=issue_data['service_id'])
        except Services.DoesNotExist:
            logger.warning(f"Service {issue_data['service_id']} not found")
    
    if issue_data.get('database_id'):
        try:
            issue.DataBases = DataBases.objects.get(pk=issue_data['database_id'])
        except DataBases.DoesNotExist:
            logger.warning(f"Database {issue_data['database_id']} not found")
    
    # Обработка user (ответственный) - может быть по id или external_id
    # 1C отправляет external_id в поле "user"
    user_external_id = issue_data.get('user') or issue_data.get('user_external_id')
    if issue_data.get('user_id'):
        try:
            issue.users = Users.objects.get(pk=issue_data['user_id'])
            logger.info(f"Found user by id: {issue_data['user_id']}")
        except Users.DoesNotExist:
            logger.warning(f"User with id {issue_data['user_id']} not found")
    elif user_external_id and user_external_id != 'null' and str(user_external_id).strip():
        try:
            issue.users = Users.objects.get(external_id=user_external_id)
            logger.info(f"Found user by external_id: {user_external_id}")
        except Users.DoesNotExist:
            logger.warning(f"User with external_id '{user_external_id}' not found")
        except Users.MultipleObjectsReturned:
            logger.warning(f"Multiple users found with external_id '{user_external_id}', using first")
            issue.users = Users.objects.filter(external_id=user_external_id).first()
    
    # Обработка supervisor - может быть по id или external_id
    # 1C отправляет external_id в поле "supervisor" (может быть "null")
    supervisor_external_id = issue_data.get('supervisor') or issue_data.get('supervisor_external_id')
    if issue_data.get('supervisor_id'):
        try:
            issue.supervisor = Users.objects.get(pk=issue_data['supervisor_id'])
            logger.info(f"Found supervisor by id: {issue_data['supervisor_id']}")
        except Users.DoesNotExist:
            logger.warning(f"Supervisor with id {issue_data['supervisor_id']} not found")
    elif supervisor_external_id and supervisor_external_id != 'null' and str(supervisor_external_id).strip():
        try:
            issue.supervisor = Users.objects.get(external_id=supervisor_external_id)
            logger.info(f"Found supervisor by external_id: {supervisor_external_id}")
        except Users.DoesNotExist:
            logger.warning(f"Supervisor with external_id '{supervisor_external_id}' not found")
        except Users.MultipleObjectsReturned:
            logger.warning(f"Multiple supervisors found with external_id '{supervisor_external_id}', using first")
            issue.supervisor = Users.objects.filter(external_id=supervisor_external_id).first()
    
    if issue_data.get('sprint_id'):
        try:
            issue.sprint = Sprints.objects.get(pk=issue_data['sprint_id'])
        except Sprints.DoesNotExist:
            logger.warning(f"Sprint {issue_data['sprint_id']} not found")
    
    if issue_data.get('parent_id'):
        try:
            issue.parent = Issues.objects.get(pk=issue_data['parent_id'])
        except Issues.DoesNotExist:
            logger.warning(f"Parent issue {issue_data['parent_id']} not found")
    
    # Обработка applicant (GenericForeignKey) - может быть по id или external_id
    # 1C отправляет external_id в поле "applicant"
    applicant_type = issue_data.get('applicant_type', 'users')  # По умолчанию users
    applicant_id = issue_data.get('applicant_id')
    applicant_external_id = issue_data.get('applicant') or issue_data.get('applicant_external_id')
    
    issue.applicant_content_type = None
    issue.applicant_object_id = None
    
    if applicant_type:
        try:
            if applicant_type == 'users' or not applicant_type:
                applicant_user = None
                if applicant_id:
                    try:
                        applicant_user = Users.objects.get(pk=applicant_id)
                        logger.info(f"Found applicant user by id: {applicant_id}")
                    except Users.DoesNotExist:
                        logger.warning(f"Applicant user with id {applicant_id} not found")
                elif applicant_external_id and applicant_external_id != 'null' and str(applicant_external_id).strip():
                    try:
                        applicant_user = Users.objects.get(external_id=applicant_external_id)
                        logger.info(f"Found applicant user by external_id: {applicant_external_id}")
                    except Users.DoesNotExist:
                        logger.warning(f"Applicant user with external_id '{applicant_external_id}' not found")
                    except Users.MultipleObjectsReturned:
                        logger.warning(f"Multiple applicant users found with external_id '{applicant_external_id}', using first")
                        applicant_user = Users.objects.filter(external_id=applicant_external_id).first()
                
                if applicant_user:
                    issue.applicant_content_type = ContentType.objects.get_for_model(Users)
                    issue.applicant_object_id = applicant_user.pk
                    
            elif applicant_type == 'clientteams':
                applicant_client = None
                if applicant_id:
                    try:
                        applicant_client = ClientTeams.objects.get(pk=applicant_id)
                        logger.info(f"Found applicant client team by id: {applicant_id}")
                    except ClientTeams.DoesNotExist:
                        logger.warning(f"Applicant client team with id {applicant_id} not found")
                elif applicant_external_id:
                    # Если у ClientTeams есть external_id, можно добавить поиск по нему
                    logger.warning(f"external_id lookup for ClientTeams not implemented yet")
                
                if applicant_client:
                    issue.applicant_content_type = ContentType.objects.get_for_model(ClientTeams)
                    issue.applicant_object_id = applicant_client.pk
        except Exception as e:
            logger.warning(f"Error setting applicant: {e}")
    
    issue._skip_kafka_event = True
    
    # Сохранение с обработкой ошибок
    try:
        logger.info(f"→ Attempting to save issue to database...")
        issue.save()
        logger.info(f"✓ Successfully created issue {issue.pk} (external_id: {issue.external_id}) from 1C")
        return issue
    except Exception as e:
        logger.error(f"✗ Error saving issue from 1C: {e}", exc_info=True)
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Issue data was: {json.dumps(issue_data, ensure_ascii=False, default=str, indent=2)}")
        # Попробуем вывести информацию о модели перед сохранением
        logger.error(f"Issue object fields before save:")
        for field in issue._meta.fields:
            try:
                value = getattr(issue, field.name, None)
                logger.error(f"  {field.name}: {value} (required: {not field.null and not field.blank})")
            except:
                pass
        raise

