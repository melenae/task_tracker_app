import json
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from django.conf import settings
from django.utils.dateparse import parse_datetime
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable
import threading
import atexit
import time
from erp_tools.issues_service import create_issue_from_1c

logger = logging.getLogger(__name__)


def headers_to_dict(headers):
    """Преобразовать Kafka headers (список кортежей) в словарь"""
    if not headers:
        return {}
    
    result = {}
    for header_key, header_value in headers:
        # header_key может быть строкой или bytes
        key = header_key.decode('utf-8') if isinstance(header_key, bytes) else header_key
        
        # header_value может быть bytes, строкой или уже словарем (если JSON)
        if isinstance(header_value, bytes):
            try:
                # Пытаемся декодировать как UTF-8
                value_str = header_value.decode('utf-8')
                # Пытаемся распарсить как JSON, если это JSON
                try:
                    value = json.loads(value_str)
                    result[key] = value
                except (json.JSONDecodeError, ValueError):
                    result[key] = value_str
            except:
                result[key] = str(header_value)
        elif isinstance(header_value, str):
            # Пытаемся распарсить как JSON
            try:
                result[key] = json.loads(header_value)
            except (json.JSONDecodeError, ValueError):
                result[key] = header_value
        else:
            result[key] = header_value
    
    return result


class KafkaService:
    """Сервис для работы с Kafka 3.7.0"""
    
    _producer: Optional[KafkaProducer] = None
    _consumer: Optional[KafkaConsumer] = None
    _consumer_thread: Optional[threading.Thread] = None
    _running = False
    
    @classmethod
    def get_producer(cls) -> Optional[KafkaProducer]:
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
            except NoBrokersAvailable as e:
                logger.warning(f"Kafka brokers not available for Producer. Producer will be None. Error: {e}")
                logger.warning("Messages will not be sent to Kafka until brokers are available.")
                cls._producer = None
            except Exception as e:
                logger.error(f"Failed to initialize Kafka Producer: {e}", exc_info=True)
                cls._producer = None
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
            
            if producer is None:
                logger.warning(f"Cannot send issue event: Kafka Producer is not available. Event: {event_type} for issue {issue_id}")
                return
            
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
            max_retries = 5
            retry_delay = 5  # секунд
            
            bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS.split(',')
            topics = [settings.KAFKA_ISSUES_TOPIC, settings.KAFKA_ISSUES_1C_TOPIC]
            
            # Базовая конфигурация Consumer
            consumer_config = {
                'bootstrap_servers': bootstrap_servers,
                'group_id': settings.KAFKA_CONSUMER_GROUP,
                'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
                'key_deserializer': lambda k: k.decode('utf-8') if k else None,
                'auto_offset_reset': 'latest',
                'enable_auto_commit': True,
                'consumer_timeout_ms': settings.KAFKA_CONSUMER_POLL_TIMEOUT_MS,
            }
            
            # Попытки подключения к Kafka
            for attempt in range(max_retries):
                try:
                    logger.info(f"Attempting to connect to Kafka brokers (attempt {attempt + 1}/{max_retries}): {bootstrap_servers}")
                    logger.info(f"Subscribing to topics: {topics}")
                    
                    consumer = KafkaConsumer(
                        *topics,
                        **consumer_config
                    )
                    
                    logger.info(f"Successfully connected to Kafka and subscribed to topics: {', '.join(topics)}")
                    cls._consumer = consumer
                    break  # Успешное подключение, выходим из цикла retry
                    
                except NoBrokersAvailable as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Kafka brokers not available (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"Failed to connect to Kafka after {max_retries} attempts. Kafka integration disabled.")
                        logger.error(f"Please ensure Kafka is running: docker-compose up -d")
                        cls._running = False
                        return
                except Exception as e:
                    logger.error(f"Error connecting to Kafka: {e}", exc_info=True)
                    if attempt < max_retries - 1:
                        logger.warning(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"Failed to connect to Kafka after {max_retries} attempts.")
                        cls._running = False
                        return
            
            # Основной цикл обработки сообщений
            if consumer:
                while cls._running:
                    try:
                        message_pack = consumer.poll(timeout_ms=settings.KAFKA_CONSUMER_POLL_TIMEOUT_MS)
                        for topic_partition, messages in message_pack.items():
                            for message in messages:
                                try:
                                    # Преобразуем headers в словарь
                                    headers_dict = headers_to_dict(message.headers)
                                    logger.info(f"Processing message from headers: {len(headers_dict)} fields")
                                    cls._process_1c_message(headers_dict)
                                except Exception as e:
                                    logger.error(f"Error processing message from 1C: {e}", exc_info=True)
                    except Exception as e:
                        if cls._running:
                            logger.error(f"Error in consumer loop: {e}", exc_info=True)
                            # При ошибке в цикле, пытаемся переподключиться
                            try:
                                consumer.close()
                            except:
                                pass
                            time.sleep(retry_delay)
                            # Пытаемся переподключиться
                            try:
                                consumer = KafkaConsumer(
                                    *topics,
                                    **consumer_config
                                )
                                cls._consumer = consumer
                                logger.info("Reconnected to Kafka")
                            except Exception as reconnect_error:
                                logger.error(f"Failed to reconnect to Kafka: {reconnect_error}")
                                cls._running = False
                                break
                            
            # Закрытие соединения
            if consumer:
                try:
                    consumer.close()
                except:
                    pass
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
    def manual_poll_messages(cls) -> Dict[str, Any]:
        """
        Ручная проверка сообщений из Kafka (однократный poll)
        Возвращает словарь с результатами обработки
        """
        result = {
            'success': False,
            'messages_processed': 0,
            'errors': []
        }

        
        try:
            bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS.split(',')
            topics = [settings.KAFKA_ISSUES_1C_TOPIC]  # Только топик от 1C
            
            # Используем уникальный group_id с UUID при каждом вызове
            # Это гарантирует, что каждый раз создается новый consumer group,
            # который будет читать все сообщения с начала (благодаря auto_offset_reset: 'earliest')
            unique_group_id = f"{settings.KAFKA_CONSUMER_GROUP}-manual-{uuid.uuid4().hex[:8]}"
            
            consumer_config = {
                'bootstrap_servers': bootstrap_servers,
                'group_id': unique_group_id,  # Уникальный group_id для каждого вызова
                'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
                'key_deserializer': lambda k: k.decode('utf-8') if k else None,
                'auto_offset_reset': 'earliest',  # Читать все сообщения с начала
                'enable_auto_commit': False,  # Не коммитить offset
                'consumer_timeout_ms': settings.KAFKA_MANUAL_POLL_TIMEOUT_MS,
            }
            
            temp_consumer = None
            try:
                logger.info("Starting manual poll for Kafka messages from topic: %s with group_id: %s", topics, unique_group_id)
                temp_consumer = KafkaConsumer(*topics, **consumer_config)
                
                # Несколько poll'ов для получения всех доступных сообщений
                message_pack = {}
                poll_attempts = 0
                max_poll_attempts = 5  # Увеличиваем количество попыток
                
                while poll_attempts < max_poll_attempts:
                    batch = temp_consumer.poll(timeout_ms=settings.KAFKA_MANUAL_POLL_BATCH_TIMEOUT_MS)
                    logger.info(f"Poll attempt {poll_attempts + 1}/{max_poll_attempts}: received {len(batch)} partitions")
                    
                    if batch:
                        message_pack.update(batch)
                        poll_attempts = 0  # Сбрасываем счетчик, если получили сообщения
                        logger.info(f"Received messages from {len(batch)} partitions, total partitions: {len(message_pack)}")
                    else:
                        poll_attempts += 1
                        logger.debug(f"No messages in batch, poll_attempts: {poll_attempts}")
                
                logger.info(f"Manual poll retrieved {len(message_pack)} message batches (partitions)")
                
                total_messages = 0
                for topic_partition, messages in message_pack.items():
                    messages_count = len(messages)
                    total_messages += messages_count
                    logger.info(f"Processing {messages_count} messages from partition {topic_partition.partition} of topic {topic_partition.topic}")
                    
                    for message in messages:
                        try:
                            logger.info(f"Processing message from {topic_partition.topic}, partition {topic_partition.partition}, offset: {message.offset}")
                            
                            # Преобразуем headers в словарь
                            headers_dict = headers_to_dict(message.headers)
                            logger.info(f"Message headers count: {len(headers_dict)}")
                            logger.info(f"Message headers preview: {json.dumps(dict(list(headers_dict.items())[:5]), ensure_ascii=False, default=str)}...")
                            logger.info(f"Message value: {message.value}")
                            
                            cls._process_1c_message(headers_dict)
                            result['messages_processed'] += 1
                            logger.info(f"Successfully processed message from {topic_partition.topic}, offset: {message.offset}")
                        except Exception as e:
                            error_msg = f"Error processing message at offset {message.offset}: {str(e)}"
                            result['errors'].append(error_msg)
                            logger.error(error_msg, exc_info=True)
                            if message.headers:
                                try:
                                    headers_dict = headers_to_dict(message.headers)
                                    logger.error(f"Message headers that caused error: {json.dumps(headers_dict, ensure_ascii=False, default=str)}")
                                except:
                                    logger.error(f"Message headers that caused error: {message.headers}")
                
                if total_messages == 0:
                    logger.warning("No messages found in Kafka topic. This could mean:")
                    logger.warning("  1. All messages were already processed")
                    logger.warning("  2. Topic is empty")
                    logger.warning("  3. Consumer group offset is at the end")
                else:
                    logger.info(f"Total messages found: {total_messages}, successfully processed: {result['messages_processed']}")
                
                result['success'] = True
                logger.info(f"Manual poll completed. Processed {result['messages_processed']} messages, errors: {len(result['errors'])}")
                
            except NoBrokersAvailable:
                result['errors'].append("Kafka brokers not available")
                logger.error("Kafka brokers not available for manual poll")
            except Exception as e:
                result['errors'].append(f"Consumer error: {str(e)}")
                logger.error(f"Error in manual poll consumer: {e}", exc_info=True)
            finally:
                if temp_consumer:
                    try:
                        temp_consumer.close()
                    except:
                        pass
                        
        except Exception as e:
            result['errors'].append(f"Unexpected error: {str(e)}")
            logger.error(f"Unexpected error in manual_poll_messages: {e}", exc_info=True)
        
        return result
    
    @classmethod
    def _process_1c_message(cls, message: Dict[str, Any]):
        """Обработать сообщение от 1С"""
        from erp_tools.models import Issues, IssueComments, Users, Companies, Services, DataBases
        
        # Детальное логирование входящего сообщения
        logger.info(f"=== Received message from Kafka ===")
        logger.info(f"Full message: {json.dumps(message, ensure_ascii=False, default=str, indent=2)}")
        
        # Проверяем формат сообщения
        # Если есть обертка с event_type и data - используем старый формат
        # Если нет - данные приходят напрямую из headers (новый формат от 1C)
        if 'event_type' in message and 'data' in message:
            # Старый формат с оберткой
            event_type = message.get('event_type')
            issue_data = message.get('data', {})
            issue_id = message.get('issue_id')
            source = message.get('source', '1c')
        else:
            # Новый формат - данные напрямую из headers
            # По умолчанию считаем это созданием заявки
            event_type = message.get('event_type', 'created')
            issue_data = message  # Все данные из headers - это и есть данные заявки
            issue_id = message.get('issue_id') or message.get('id')
            source = message.get('source', '1c')
        
        logger.info(f"Parsed fields - event_type: '{event_type}', source: '{source}', issue_id: {issue_id}")
        logger.info(f"Issue data type: {type(issue_data)}, keys: {list(issue_data.keys()) if isinstance(issue_data, dict) else 'not a dict'}")
        
        if source == 'django':
            logger.warning(f"⚠ Ignoring message from django source (this is expected for Django->1C messages)")
            return
        
        if not event_type:
            logger.error(f"✗ Message missing 'event_type' field!")
            logger.error(f"Message structure: {json.dumps(message, ensure_ascii=False, default=str)}")
            return
        
        if not issue_data or not isinstance(issue_data, dict):
            logger.warning(f"⚠ Message has empty or invalid 'data' field. event_type: {event_type}")
            logger.warning(f"issue_data value: {issue_data}")
        
        logger.info(f"→ Processing 1C message: event_type='{event_type}', issue_id={issue_id}")
        
        try:
            if event_type == 'created':
                logger.info(f"→ Calling create_issue_from_1c...")
                created_issue = create_issue_from_1c(issue_data)
                if created_issue:
                    logger.info(f"✓ Successfully created issue {created_issue.pk} from 1C")
                else:
                    logger.warning(f"⚠ create_issue_from_1c returned None (issue may already exist)")
            elif event_type == 'updated':
                if issue_id:
                    cls._update_issue_from_1c(issue_id, issue_data)
                else:
                    logger.warning(f"⚠ event_type='updated' but issue_id is missing")
            elif event_type == 'status_changed':
                if issue_id:
                    cls._update_issue_status_from_1c(issue_id, issue_data)
                else:
                    logger.warning(f"⚠ event_type='status_changed' but issue_id is missing")
            elif event_type == 'comment_added':
                if issue_id:
                    cls._add_comment_from_1c(issue_id, issue_data)
                else:
                    logger.warning(f"⚠ event_type='comment_added' but issue_id is missing")
            else:
                logger.warning(f"⚠ Unknown event type: '{event_type}'. Expected: 'created', 'updated', 'status_changed', 'comment_added'")
        except Exception as e:
            logger.error(f"✗ Error processing 1C event {event_type}: {e}", exc_info=True)
            raise  # Пробрасываем исключение дальше, чтобы оно попало в result['errors']
    
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