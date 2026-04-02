from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
    CheckConstraint,
    Boolean,
    Numeric,
)
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class DatasetORM(Base):

    __tablename__ = "datasets"
    
    dataset_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор датасета"
    )
    
    source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Источник данных (kaggle, uci)"
    )
    
    external_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Внешний идентификатор в репозитории"
    )
    
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Название датасета"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Описание датасета"
    )
    
    tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        nullable=True,
        comment="Теги/категории датасета"
    )
    
    dataset_format: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Основной формат данных (csv, json)"
    )
    
    dataset_size_kb: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Общий размер всех файлов в килобайтах"
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        server_default=text("'active'"),
        comment="Статус датасета (active, error, deleted)",
    )
    
    download_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="URL для скачивания датасета"
    )
    
    repository_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="URL страницы датасета в репозитории"
    )
    
    source_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата последнего обновления в источнике",
    )
    
    search_vector: Mapped[Optional[str]] = mapped_column(
        TSVECTOR,
        nullable=True,
        comment="TSVECTOR для полнотекстового поиска"
    )
    
    files: Mapped[List["FileORM"]] = relationship(
        "FileORM",
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_source_external_id"),
        CheckConstraint(
            "status IN ('active', 'error', 'deleted')",
            name="chk_status",
        ),
        Index("idx_datasets_search_vector", "search_vector", postgresql_using="gin"),
        Index("idx_datasets_tags", "tags", postgresql_using="gin"),
        Index("idx_datasets_dataset_size_kb", "dataset_size_kb"),
        Index("idx_datasets_dataset_format", "dataset_format"),
        Index("idx_datasets_status", "status"),
        Index("idx_datasets_source", "source"),
        Index(
            "idx_datasets_source_updated_at",
            "source_updated_at",
            postgresql_ops={"source_updated_at": "DESC"}
        ),
        {"comment": "Каталог датасетов из внешних репозиториев"}
    )
    
    def __repr__(self) -> str:
        return f"<DatasetORM(dataset_id={self.dataset_id}, title={self.title}, source={self.source})>"


class FileORM(Base):

    __tablename__ = "files"
    
    file_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор файла"
    )
    
    dataset_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("datasets.dataset_id", ondelete="CASCADE"),
        nullable=False,
    )
    
    file_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Имя файла с относительным путём"
    )
    
    file_size_kb: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Размер файла в килобайтах"
    )
    
    file_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="SHA-256 хеш файла (только для CSV/JSON)"
    )
    
    is_data: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
        comment="Флаг: является ли файл data-файлом",
    )
    
    file_updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
        comment="Дата последнего обновления файла"
    )
    
    dataset: Mapped["DatasetORM"] = relationship(
        "DatasetORM",
        back_populates="files"
    )
    
    __table_args__ = (
        UniqueConstraint("dataset_id", "file_name", name="uq_files_dataset_file_name"),
        Index("idx_files_dataset_id", "dataset_id"),
        {"comment": "Файлы в составе датасетов"}
    )
    
    def __repr__(self) -> str:
        return f"<FileORM(file_id={self.file_id}, file_name={self.file_name}, dataset_id={self.dataset_id})>"