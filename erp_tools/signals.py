from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from erp_tools.models import Issues, IssueComments
from erp_tools.kafka_service import KafkaService
import logging

logger = logging.getLogger(__name__)

# Глобальный словарь для хранения старого статуса заявки
_old_statuses = {}


@receiver(pre_save, sender=Issues)
def issue_pre_save(sender, instance, **kwargs):
    """Сохранить старый статус перед сохранением"""
    if instance.pk:
        try:
            old_instance = Issues.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            _old_statuses[instance.pk] = old_instance.status
        except Issues.DoesNotExist:
            instance._old_status = None
            _old_statuses.pop(instance.pk, None)
    else:
        instance._old_status = None


@receiver(post_save, sender=Issues)
def issue_post_save(sender, instance, created, **kwargs):
    """Отправить событие в Kafka при создании/обновлении заявки"""
    if hasattr(instance, '_skip_kafka_event'):
        return
    
    # Если комментарий будет создан вместе с обновлением/созданием, откладываем отправку
    if hasattr(instance, '_creating_comment_with_update') and instance._creating_comment_with_update:
        logger.info(f"Delaying issue {'create' if created else 'update'} event for issue {instance.pk} - comment will be created")
        return
    
    try:
        issue_data = {
            'id': instance.pk,
            'name': instance.name,
            'content': instance.content or '',
            'status': instance.status,
            'priority': instance.priority,
            'deadline': instance.deadline.isoformat() if instance.deadline else None,
            'date_create': instance.date_create.isoformat() if instance.date_create else None,
            'date_check': instance.date_check.isoformat() if instance.date_check else None,
            'date_start_plan': instance.date_start_plan.isoformat() if instance.date_start_plan else None,
            'date_end_plan': instance.date_end_plan.isoformat() if instance.date_end_plan else None,
            'company_id': instance.Companies_id,
            'service_id': instance.Services_id,
            'database_id': instance.DataBases_id,
            'user_id': instance.users_id,
            'supervisor_id': instance.supervisor_id,
            'applicant_type': instance.applicant_content_type.model if instance.applicant_content_type else None,
            'applicant_id': instance.applicant_object_id,
            'sprint_id': instance.sprint_id,
            'parent_id': instance.parent_id,
        }
        
        if created:
            KafkaService.send_issue_event('created', issue_data, instance.pk)
            logger.info(f"Sent 'created' event for issue {instance.pk}")
        else:
            old_status = getattr(instance, '_old_status', None)
            if old_status and old_status != instance.status:
                issue_data['old_status'] = old_status
                issue_data['new_status'] = instance.status
                # Если есть комментарий, это событие изменения статуса с комментарием
                event_type = 'status_changed_with_comment' if 'comment' in issue_data else 'status_changed'
                KafkaService.send_issue_event(event_type, issue_data, instance.pk)
                logger.info(f"Sent '{event_type}' event for issue {instance.pk}: {old_status} -> {instance.status}")
            else:
                # Если есть комментарий, это обновление с комментарием
                event_type = 'updated_with_comment' if 'comment' in issue_data else 'updated'
                KafkaService.send_issue_event(event_type, issue_data, instance.pk)
                logger.info(f"Sent '{event_type}' event for issue {instance.pk}")
                
    except Exception as e:
        logger.error(f"Error sending issue event to Kafka: {e}", exc_info=True)


@receiver(post_delete, sender=Issues)
def issue_post_delete(sender, instance, **kwargs):
    """Отправить событие в Kafka при удалении заявки"""
    try:
        issue_data = {
            'id': instance.pk,
            'name': instance.name,
        }
        KafkaService.send_issue_event('deleted', issue_data, instance.pk)
        logger.info(f"Sent 'deleted' event for issue {instance.pk}")
    except Exception as e:
        logger.error(f"Error sending delete event to Kafka: {e}", exc_info=True)


@receiver(post_save, sender=IssueComments)
def issue_comment_post_save(sender, instance, created, **kwargs):
    """Отправить событие в Kafka при добавлении комментария"""
    if created and instance.issue:
        if hasattr(instance, '_skip_kafka_event'):
            return
        
        try:
            issue = instance.issue
            
            # Проверяем, был ли комментарий создан вместе с обновлением заявки
            if hasattr(issue, '_creating_comment_with_update') and issue._creating_comment_with_update:
                # Удаляем флаг
                delattr(issue, '_creating_comment_with_update')
                
                # Отправляем объединенное сообщение об обновлении с комментарием
                # Перезагружаем issue из БД, чтобы получить актуальные данные
                issue_obj = Issues.objects.get(pk=issue.pk)
                
                # Получаем старый статус из глобального словаря
                old_status = _old_statuses.pop(issue.pk, None)
                
                issue_data = {
                    'id': issue_obj.pk,
                    'name': issue_obj.name,
                    'content': issue_obj.content or '',
                    'status': issue_obj.status,
                    'priority': issue_obj.priority,
                    'deadline': issue_obj.deadline.isoformat() if issue_obj.deadline else None,
                    'date_create': issue_obj.date_create.isoformat() if issue_obj.date_create else None,
                    'date_check': issue_obj.date_check.isoformat() if issue_obj.date_check else None,
                    'date_start_plan': issue_obj.date_start_plan.isoformat() if issue_obj.date_start_plan else None,
                    'date_end_plan': issue_obj.date_end_plan.isoformat() if issue_obj.date_end_plan else None,
                    'company_id': issue_obj.Companies_id,
                    'service_id': issue_obj.Services_id,
                    'database_id': issue_obj.DataBases_id,
                    'user_id': issue_obj.users_id,
                    'supervisor_id': issue_obj.supervisor_id,
                    'applicant_type': issue_obj.applicant_content_type.model if issue_obj.applicant_content_type else None,
                    'applicant_id': issue_obj.applicant_object_id,
                    'sprint_id': issue_obj.sprint_id,
                    'parent_id': issue_obj.parent_id,
                    'comment': {
                        'comment_id': instance.pk,
                        'comment': instance.comment or '',
                        'user_id': instance.user_id,
                        'user_name': instance.user.name if instance.user else None,
                        'date_create': instance.date_create.isoformat() if instance.date_create else None,
                    }
                }
                
                # Определяем тип события
                # Проверяем, была ли заявка только что создана (нет старого статуса и заявка создана недавно)
                from django.utils import timezone
                from datetime import timedelta
                
                is_newly_created = (
                    old_status is None and 
                    issue_obj.date_create and 
                    (timezone.now() - issue_obj.date_create) < timedelta(seconds=5)
                )
                
                if is_newly_created:
                    event_type = 'created_with_comment'
                elif old_status and old_status != issue_obj.status:
                    issue_data['old_status'] = old_status
                    issue_data['new_status'] = issue_obj.status
                    event_type = 'status_changed_with_comment'
                else:
                    event_type = 'updated_with_comment'
                
                KafkaService.send_issue_event(event_type, issue_data, issue_obj.pk)
                logger.info(f"Sent '{event_type}' event with comment for issue {issue_obj.pk}")
                return
            
            # Если комментарий создан отдельно, отправляем отдельное сообщение
            comment_data = {
                'issue_id': instance.issue.pk,
                'comment_id': instance.pk,
                'comment': instance.comment or '',
                'user_id': instance.user_id,
                'user_name': instance.user.name if instance.user else None,
                'date_create': instance.date_create.isoformat() if instance.date_create else None,
            }
            KafkaService.send_issue_event('comment_added', comment_data, instance.issue.pk)
            logger.info(f"Sent 'comment_added' event for issue {instance.issue.pk}")
        except Exception as e:
            logger.error(f"Error sending comment event to Kafka: {e}", exc_info=True)