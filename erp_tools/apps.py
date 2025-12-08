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
        try:
            from erp_tools.kafka_service import KafkaService
            KafkaService.start_consumer()
            logger.info("Kafka consumer started successfully")
        except Exception as e:
            logger.warning(f"Failed to start Kafka consumer: {e}. Kafka integration may not work.")