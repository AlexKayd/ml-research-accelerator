import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.config import get_settings

logger = logging.getLogger(__name__)

EDA_EVENT_TYPES = {
    'FILE_UPDATED': 'file_updated',
    'FILE_DELETED': 'file_deleted',
}


class EDANotifier:
    
    def __init__(self, celery_app: Optional[Any] = None) -> None:
        self._celery_app = celery_app
        self._pending_notifications: List[Dict[str, Any]] = []
        
        logger.debug("Инициализирован EDANotifier")
    
    def add_file_notification(
        self,
        event_type: str,
        dataset_id: int,
        file_id: Optional[int] = None,
        file_name: Optional[str] = None,
        file_hash: Optional[str] = None,
        external_id: Optional[str] = None,
        source: Optional[str] = None
    ) -> None:
        """Добавляет уведомление об изменении файла в очередь отправки"""
        notification = {
            'event_type': event_type,
            'dataset_id': dataset_id,
            'file_id': file_id,
            'file_name': file_name,
            'file_hash': file_hash,
            'external_id': external_id,
            'source': source,
            'created_at': datetime.now().isoformat()
        }
        
        self._pending_notifications.append(notification)
        
        logger.info(
            f"Добавлено уведомление EDA: {event_type} для датасета {dataset_id}, "
            f"файл {file_name or file_id}"
        )
    
    
    async def send_notifications(self) -> int:
        """Отправляет все накопленные уведомления в очередь EDA сервиса"""
        if not self._pending_notifications:
            logger.debug("Нет накопленных уведомлений для отправки в EDA")
            return 0
        
        if not self._celery_app:
            logger.warning("Celery приложение не настроено, уведомления не отправлены")
            return 0

        eda_queue = get_settings().CELERY_EDA_QUEUE
        
        sent_count = 0
        failed_notifications: List[Dict[str, Any]] = []

        for notification in list(self._pending_notifications):
            try:
                task_name = 'eda_service.tasks.process_dataset_change'

                await asyncio.to_thread(
                    self._celery_app.send_task,
                    task_name,
                    kwargs={
                        'event_type': notification['event_type'],
                        'dataset_id': notification['dataset_id'],
                        'file_id': notification.get('file_id'),
                        'file_name': notification.get('file_name'),
                        'file_hash': notification.get('file_hash'),
                        'external_id': notification.get('external_id'),
                        'source': notification.get('source')
                    },
                    queue=eda_queue,
                )
                
                sent_count += 1
                logger.debug(
                    f"Отправлено уведомление EDA: {notification['event_type']} "
                    f"для датасета {notification['dataset_id']}"
                )
                
            except Exception as e:
                logger.error(
                    f"Ошибка отправки уведомления EDA: {e}. "
                    f"Уведомление: {notification}"
                )
                failed_notifications.append(notification)

        self._pending_notifications = failed_notifications
        
        logger.info(f"Отправлено {sent_count} уведомлений в EDA сервис")
        return sent_count
    
    def clear_pending_notifications(self) -> None:
        """Очищает очередь уведомлений"""
        count = len(self._pending_notifications)
        self._pending_notifications.clear()
        logger.debug(f"Очищено {count} накопленных уведомлений EDA")
    
    def get_pending_count(self) -> int:
        """Возвращает количество накопленных уведомлений"""
        return len(self._pending_notifications)