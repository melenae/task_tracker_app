import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from django.conf import settings
from django.utils.dateparse import parse_datetime
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import threading
import atexit

logger = logging.getLogger(__name__)


class KafkaService:
    """Сервис для работы с Kafka 3.7.0"""
    
    _producer: Optional[KafkaProducer] = None
    _consumer: Optional[KafkaConsumer] = None
    _consumer_thread: Optional[threading.Thread] = None
    _running = False
    
    @classmethod
    def get_producer(cls) -> KafkaProducer:
        """Получить или создать Kafka Producer"""
        if cls._producer is None:
            try:
                bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS.split(',')
                
                # Базовая конфигурация Producer
                producer_config = {
                    'bootstrap_servers': bootstrap_servers,
                    'value_serializer': lambda v: json.dumps(v, ensure_ascii=False, default=str).encode('utf-8'),
                    'key_serializer': lambda k: str(k).encode('utf-8') if k else None,
                    'acks': 'all',
                    'retries': 3,
                    'max_in_flight_requests_per_connection': 1,
                }
                
                cls._producer = KafkaProducer(**producer_config)
                logger.info(f"Kafka Producer initialized with servers: {bootstrap_servers}")
            except Exception as e:
                logger.error(f"Failed to initialize Kafka Producer: {e}")
                raise
        return cls._producer
    
    
    @classmethod
    def send_issue_event(cls, event_type: str, issue_data: Dict[str, Any], issue_id: int):
        """
        Отправить событие о заявке в Kafka
        
        Args:
            event_type: Тип события ('created', 'updated', 'status_changed', 'deleted', 'comment_added')
            issue_data: Данные заявки
            issue_id: ID заявки
        """
        try:
            producer = cls.get_producer()
            
            message = {
                'event_type': event_type,
                'issue_id': issue_id,
                'timestamp': issue_data.get('date_create') or issue_data.get('updated_at'),
                'data': issue_data,
                'source': 'django',
                'version': '1.0'
            }
            
            future = producer.send(
                settings.KAFKA_ISSUES_TOPIC,
                key=str(issue_id),
                value=message
            )
            
            try:
                record_metadata = future.get(timeout=10)
                logger.info(
                    f"Message sent to topic={record_metadata.topic} "
                    f"partition={record_metadata.partition} "
                    f"offset={record_metadata.offset}"
                )
            except Exception as e:
                logger.warning(f"Could not get message confirmation: {e}")
            
            logger.info(f"Issue event sent: {event_type} for issue {issue_id}")
            
        except KafkaError as e:
            logger.error(f"Kafka error while sending issue event: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while sending issue event: {e}", exc_info=True)
    
    @classmethod
    def start_consumer(cls):
        """Запустить Kafka Consumer для получения событий от 1С"""
        if cls._running:
            logger.warning("Consumer is already running")
            return
        
        if cls._consumer_thread and cls._consumer_thread.is_alive():
            logger.warning("Consumer thread is already running")
            return
        
        def consume_messages():
            cls._running = True
            consumer = None
            try:
                bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS.split(',')
                logger.info(f"Attempting to connect to Kafka brokers: {bootstrap_servers}")
                
                # Базовая конфигурация Consumer
                consumer_config = {
                    'bootstrap_servers': bootstrap_servers,
                    'group_id': settings.KAFKA_CONSUMER_GROUP,
                    'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
                    'key_deserializer': lambda k: k.decode('utf-8') if k else None,
                    'auto_offset_reset': 'latest',
                    'enable_auto_commit': True,
                    'consumer_timeout_ms': 1000,
                }
                
                # Подписываемся на оба топика
                topics = [settings.KAFKA_ISSUES_TOPIC, settings.KAFKA_ISSUES_1C_TOPIC]
                logger.info(f"Subscribing to topics: {topics}")
                consumer = KafkaConsumer(
                    *topics,
                    **consumer_config
                )
                
                logger.info(f"Successfully connected to Kafka and subscribed to topics: {', '.join(topics)}")
                cls._consumer = consumer
                
                while cls._running:
                    try:
                        message_pack = consumer.poll(timeout_ms=1000)
                        for topic_partition, messages in message_pack.items():
                            for message in messages:
                                try:
                                    cls._process_1c_message(message.value)
                                except Exception as e:
                                    logger.error(f"Error processing message from 1C: {e}", exc_info=True)
                    except Exception as e:
                        if cls._running:
                            logger.error(f"Error in consumer loop: {e}", exc_info=True)
                            
            except Exception as e:
                logger.error(f"Error in consumer thread: {e}", exc_info=True)
            finally:
                if consumer:
                    consumer.close()
                cls._running = False
                logger.info("Kafka Consumer thread stopped")
        
        cls._consumer_thread = threading.Thread(target=consume_messages, daemon=True)
        cls._consumer_thread.start()
        logger.info("Kafka Consumer thread started")
        
        atexit.register(cls.stop_consumer)
    
    @classmethod
    def stop_consumer(cls):
        """Остановить Kafka Consumer"""
        cls._running = False
        if cls._consumer:
            cls._consumer.close()
        logger.info("Kafka Consumer stopped")
    
    @classmethod
    def _process_1c_message(cls, message: Dict[str, Any]):
        """Обработать сообщение от 1С"""
        from erp_tools.models import Issues, IssueComments, Users, Companies, Services, DataBases
        
        event_type = message.get('event_type')
        issue_data = message.get('data', {})
        issue_id = message.get('issue_id')
        source = message.get('source', '1c')
        
        if source == 'django':
            logger.debug(f"Ignoring message from django source")
            return
        
        logger.info(f"Processing 1C message: {event_type} for issue {issue_id}")
        
        try:
            if event_type == 'created':
                cls._create_issue_from_1c(issue_data)
            elif event_type == 'updated':
                if issue_id:
                    cls._update_issue_from_1c(issue_id, issue_data)
            elif event_type == 'status_changed':
                if issue_id:
                    cls._update_issue_status_from_1c(issue_id, issue_data)
            elif event_type == 'comment_added':
                if issue_id:
                    cls._add_comment_from_1c(issue_id, issue_data)
            else:
                logger.warning(f"Unknown event type: {event_type}")
        except Exception as e:
            logger.error(f"Error processing 1C event {event_type}: {e}", exc_info=True)
    
    @classmethod
    def _create_issue_from_1c(cls, issue_data: Dict[str, Any]):
        """Создать заявку из данных 1С"""
        from erp_tools.models import Issues, Companies, Services, DataBases, Users
        
        issue = Issues(
            name=issue_data.get('name', 'Заявка из 1С'),
            content=issue_data.get('content', ''),
            status=issue_data.get('status', 'new'),
            priority=issue_data.get('priority', 'medium'),
        )
        
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
        
        if issue_data.get('user_id'):
            try:
                issue.users = Users.objects.get(pk=issue_data['user_id'])
            except Users.DoesNotExist:
                logger.warning(f"User {issue_data['user_id']} not found")
        
        issue._skip_kafka_event = True
        issue.save()
        
        logger.info(f"Created issue {issue.pk} from 1C")
        return issue
    
    @classmethod
    def _update_issue_from_1c(cls, issue_id: int, issue_data: Dict[str, Any]):
        """Обновить заявку из данных 1С"""
        from erp_tools.models import Issues
        
        try:
            issue = Issues.objects.get(pk=issue_id)
            
            update_fields = []
            allowed_fields = {
                'name': 'name',
                'content': 'content',
                'priority': 'priority',
            }
            
            for field_1c, field_django in allowed_fields.items():
                if field_1c in issue_data:
                    setattr(issue, field_django, issue_data[field_1c])
                    update_fields.append(field_django)
            
            if 'deadline' in issue_data:
                deadline_value = issue_data['deadline']
                if isinstance(deadline_value, str):
                    parsed_deadline = parse_datetime(deadline_value)
                    if parsed_deadline:
                        issue.deadline = parsed_deadline
                        update_fields.append('deadline')
                elif isinstance(deadline_value, datetime):
                    issue.deadline = deadline_value
                    update_fields.append('deadline')
                elif deadline_value is None:
                    issue.deadline = None
                    update_fields.append('deadline')
            
            if update_fields:
                issue._skip_kafka_event = True
                issue.save(update_fields=update_fields)
                logger.info(f"Updated issue {issue_id} from 1C: {update_fields}")
            
        except Issues.DoesNotExist:
            logger.warning(f"Issue {issue_id} not found for update from 1C")
    
    @classmethod
    def _update_issue_status_from_1c(cls, issue_id: int, issue_data: Dict[str, Any]):
        """Обновить статус заявки из 1С"""
        from erp_tools.models import Issues
        
        try:
            issue = Issues.objects.get(pk=issue_id)
            new_status = issue_data.get('status')
            
            if new_status and new_status in dict(Issues.STATUS_CHOICES):
                old_status = issue.status
                issue.status = new_status
                issue._skip_kafka_event = True
                issue.save(update_fields=['status'])
                logger.info(f"Updated status of issue {issue_id} from {old_status} to {new_status} from 1C")
            else:
                logger.warning(f"Invalid status {new_status} for issue {issue_id}")
        except Issues.DoesNotExist:
            logger.warning(f"Issue {issue_id} not found for status update from 1C")
    
    @classmethod
    def _add_comment_from_1c(cls, issue_id: int, comment_data: Dict[str, Any]):
        """Добавить комментарий к заявке из 1С"""
        from erp_tools.models import Issues, IssueComments, Users
        
        try:
            issue = Issues.objects.get(pk=issue_id)
            
            comment = IssueComments(
                issue=issue,
                comment=comment_data.get('comment', ''),
            )
            
            if comment_data.get('user_email'):
                try:
                    comment.user = Users.objects.get(email=comment_data['user_email'])
                except Users.DoesNotExist:
                    logger.debug(f"User with email {comment_data['user_email']} not found")
            
            comment._skip_kafka_event = True
            comment.save()
            
            logger.info(f"Added comment to issue {issue_id} from 1C")
        except Issues.DoesNotExist:
            logger.warning(f"Issue {issue_id} not found for comment from 1C")
    
    @classmethod
    def close(cls):
        """Закрыть соединения с Kafka"""
        cls.stop_consumer()
        
        if cls._producer:
            cls._producer.flush()
            cls._producer.close()
            cls._producer = None
            logger.info("Kafka Producer closed")