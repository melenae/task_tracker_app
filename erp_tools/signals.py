from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from erp_tools.models import Issues, IssueComments
from erp_tools.kafka_service import KafkaService
import logging

logger = logging.getLogger(__name__)

# Глобальный словарь для отслеживания комментариев, созданных вместе с обновлением заявки
_pending_comments = {}


@receiver(pre_save, sender=Issues)
def issue_pre_save(sender, instance, **kwargs):
    """Сохранить старый статус перед сохранением"""
    if instance.pk:
        try:
            old_instance = Issues.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Issues.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Issues)
def issue_post_save(sender, instance, created, **kwargs):
    """Отправить событие в Kafka при создании/обновлении заявки"""
    if hasattr(instance, '_skip_kafka_event'):
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
            'company_id': instance.companies_id,
            'service_id': instance.services_id,
            'database_id': instance.databases_id,
            'user_id': instance.users_id,
            'supervisor_id': instance.supervisor_id,
            'applicant_type': instance.applicant_content_type.model if instance.applicant_content_type else None,
            'applicant_id': instance.applicant_object_id,
            'sprint_id': instance.sprint_id,
            'parent_id': instance.parent_id,
        }
        
        # Проверяем, есть ли ожидающий комментарий для этой заявки
        if instance.pk in _pending_comments:
            comment_info = _pending_comments.pop(instance.pk)
            issue_data['comment'] = {
                'comment_id': comment_info.get('comment_id'),
                'comment': comment_info.get('comment'),
                'user_id': comment_info.get('user_id'),
                'user_name': comment_info.get('user_name'),
                'date_create': comment_info.get('date_create'),
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
                # Сохраняем комментарий для включения в сообщение об обновлении
                _pending_comments[issue.pk] = {
                    'comment_id': instance.pk,
                    'comment': instance.comment or '',
                    'user_id': instance.user_id,
                    'user_name': instance.user.name if instance.user else None,
                    'date_create': instance.date_create.isoformat() if instance.date_create else None,
                }
                logger.info(f"Comment {instance.pk} will be included in issue update for issue {issue.pk}")
                # Удаляем флаг
                delattr(issue, '_creating_comment_with_update')
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