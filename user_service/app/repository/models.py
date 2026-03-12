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
    func
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserORM(Base):
    
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор пользователя"
    )
    
    login: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Уникальное имя пользователя для входа"
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Хешированный пароль (bcrypt)"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        comment="Дата и время регистрации"
    )
    
    favorites: Mapped[List["FavoriteDatasetORM"]] = relationship(
        "FavoriteDatasetORM",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    user_reports: Mapped[List["UserReportORM"]] = relationship(
        "UserReportORM",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<UserORM(user_id={self.user_id}, login={self.login})>"


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
        comment="Источник данных (kaggle, uci, huggingface)"
    )
    
    external_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
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
        comment="Теги"
    )
    
    file_format: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Формат файла (CSV, JSON)"
    )
    
    file_size_mb: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Размер файла в мегабайтах"
    )
    
    structure_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="single",
        comment="Тип структуры датасета (single/archive/multifile)"
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        index=True,
        comment="Статус датасета (active/deleted)"
    )
    
    download_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Ссылка для скачивания файла"
    )
    
    repository_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Ссылка на страницу в репозитории"
    )
    
    file_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment="SHA-256 хеш файла"
    )
    
    source_updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        comment="Дата обновления в источнике (из источника, не обновляется при UPDATE)"
    )
    
    search_vector: Mapped[Optional[str]] = mapped_column(
        TSVECTOR,
        nullable=True,
        comment="TSVECTOR для полнотекстового поиска"
    )
    
    reports: Mapped[List["ReportORM"]] = relationship(
        "ReportORM",
        back_populates="dataset",
        cascade="all, delete-orphan"
    )
    
    favorites: Mapped[List["FavoriteDatasetORM"]] = relationship(
        "FavoriteDatasetORM",
        back_populates="dataset",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_source_external_id"),
        Index("idx_datasets_search_vector", "search_vector", postgresql_using="gin"),
        Index("idx_datasets_tags", "tags", postgresql_using="gin"),
        Index("idx_datasets_file_size_mb", "file_size_mb"),
        Index("idx_datasets_file_format", "file_format"),
        Index("idx_datasets_source_updated_at", "source_updated_at", postgresql_ops={"source_updated_at": "DESC"}),
        {"comment": "Каталог датасетов из внешних репозиториев"}
    )
    
    def __repr__(self) -> str:
        return f"<DatasetORM(dataset_id={self.dataset_id}, title={self.title})>"


class ReportORM(Base):
    
    __tablename__ = "reports"
    
    report_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор отчёта"
    )
    
    dataset_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("datasets.dataset_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Уникальный идентификатор датасета"
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        default="processing",
        index=True,
        comment="Статус генерации отчёта"
    )
    
    content: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Содержимое отчёта в формате JSON"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        comment="Дата и время последнего обновления отчёта"
    )
    
    dataset: Mapped["DatasetORM"] = relationship(
        "DatasetORM",
        back_populates="reports"
    )
    
    user_reports: Mapped[List["UserReportORM"]] = relationship(
        "UserReportORM",
        back_populates="report",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("idx_reports_dataset_id", "dataset_id"),
        Index("idx_reports_status", "status"),
        {"comment": "Хранилище сгенерированных EDA-отчётов"}
    )
    
    def __repr__(self) -> str:
        return f"<ReportORM(report_id={self.report_id}, status={self.status})>"


class FavoriteDatasetORM(Base):
    
    __tablename__ = "favorite_datasets"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
        comment="Идентификатор пользователя"
    )
    
    dataset_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("datasets.dataset_id", ondelete="CASCADE"),
        primary_key=True,
        comment="Идентификатор датасета"
    )
    
    user: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="favorites"
    )
    
    dataset: Mapped["DatasetORM"] = relationship(
        "DatasetORM",
        back_populates="favorites"
    )
    
    __table_args__ = (
        Index("idx_favorites_user_id", "user_id"),
        Index("idx_favorites_dataset_id", "dataset_id"),
        {"comment": "Связь пользователей с избранными датасетами"}
    )
    
    def __repr__(self) -> str:
        return f"<FavoriteDatasetORM(user_id={self.user_id}, dataset_id={self.dataset_id})>"


class UserReportORM(Base):
    
    __tablename__ = "users_reports"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
        comment="Идентификатор пользователя"
    )
    
    report_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("reports.report_id", ondelete="CASCADE"),
        primary_key=True,
        comment="Идентификатор отчёта"
    )
    
    user: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="user_reports"
    )
    
    report: Mapped["ReportORM"] = relationship(
        "ReportORM",
        back_populates="user_reports"
    )
    
    __table_args__ = (
        Index("idx_users_reports_user_id", "user_id"),
        Index("idx_users_reports_report_id", "report_id"),
        {"comment": "Связь пользователей и отчётов, сохраненных в историю "}
    )
    
    def __repr__(self) -> str:
        return f"<UserReportORM(user_id={self.user_id}, report_id={self.report_id})>"