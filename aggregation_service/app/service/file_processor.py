import asyncio
import logging
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from app.domain.entities import File

logger = logging.getLogger(__name__)


class FileProcessor:
    
    def __init__(self, temp_dir: Optional[str] = None) -> None:
        self._temp_dir = temp_dir
        self._active_temp_dirs: List[str] = []
        
        logger.debug("Инициализирован FileProcessor")
    
    async def create_temp_directory(self, prefix: str = "dataset_") -> Path:
        """Создаёт временную директорию для обработки файлов"""
        temp_path = Path(tempfile.mkdtemp(prefix=prefix, dir=self._temp_dir))
        self._active_temp_dirs.append(str(temp_path))
        logger.debug(f"Создана временная директория: {temp_path}")
        return temp_path
    
    async def cleanup_temp_directory(self, temp_path: Path) -> None:
        """Удаляет временную директорию и все её содержимое"""
        try:
            if temp_path.exists():
                await asyncio.to_thread(shutil.rmtree, temp_path, ignore_errors=True)
                
                if str(temp_path) in self._active_temp_dirs:
                    self._active_temp_dirs.remove(str(temp_path))
                
                logger.debug(f"Очищена временная директория: {temp_path}")
        except Exception as e:
            logger.error(f"Ошибка при очистке временной директории {temp_path}: {e}")
    
    async def cleanup_all_temp_directories(self) -> None:
        """Удаляет все активные временные директории"""
        logger.debug(f"Очистка всех временных директорий ({len(self._active_temp_dirs)} шт.)")
        
        for temp_path_str in self._active_temp_dirs.copy():
            temp_path = Path(temp_path_str)
            await self.cleanup_temp_directory(temp_path)
        
        logger.debug("Все временные директории очищены")
    
    async def create_file_entity(
        self,
        file_name: str,
        file_size_kb: float,
        is_data: bool,
        file_hash: Optional[str] = None
    ) -> File:
        return File(
            file_name=file_name,
            file_size_kb=file_size_kb,
            is_data=is_data,
            file_hash=file_hash if is_data else None,
            file_updated_at=datetime.now()
        )
    
    def get_relative_path(self, file_path: Path, base_path: Path) -> str:
        """Получает относительный путь файла относительно базовой директории"""
        try:
            return str(file_path.relative_to(base_path))
        except ValueError:
            return file_path.name
    
    def get_pending_count(self) -> int:
        """Возвращает количество активных временных директорий"""
        return len(self._active_temp_dirs)
    
    def reset(self) -> None:
        """Сбрасывает состояние процессора файлов"""
        self._active_temp_dirs.clear()
        logger.debug("FileProcessor сброшен")