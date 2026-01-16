from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class ErpToolsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'erp_tools'
    
    def ready(self):
        # Регистрируем signals
        import erp_tools.signals
        
        # Запускаем consumer при старте приложения
        # Consumer запускается в отдельном потоке и будет пытаться подключиться с retry
        try:
            from erp_tools.kafka_service import KafkaService
            KafkaService.start_consumer()
            logger.info("Kafka consumer startup initiated (will retry if Kafka is not available)")
        except Exception as e:
            logger.warning(f"Failed to initiate Kafka consumer: {e}. Kafka integration may not work.")
            logger.warning("The application will continue to work, but Kafka messages will not be processed.")