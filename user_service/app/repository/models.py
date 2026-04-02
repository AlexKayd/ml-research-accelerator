from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
    CheckConstraint,
    Numeric,
)
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserORM(Base):

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор пользователя",
    )

    login: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="Уникальное имя пользователя для входа",
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Хешированный пароль",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        comment="Дата и время регистрации",
    )

    favorites: Mapped[List["FavoriteDatasetORM"]] = relationship(
        "FavoriteDatasetORM",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    user_reports: Mapped[List["UserReportORM"]] = relationship(
        "UserReportORM",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<UserORM(user_id={self.user_id}, login={self.login})>"


class DatasetORM(Base):

    __tablename__ = "datasets"

    dataset_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор датасета",
    )

    source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Источник данных (kaggle, uci, hg)",
    )

    external_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Внешний идентификатор в репозитории",
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Название датасета",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Описание датасета",
    )

    tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        nullable=True,
        comment="Теги",
    )

    dataset_format: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Основной формат данных (csv, json)",
    )

    dataset_size_kb: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Суммарный размер файлов датасета, КБ",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        server_default=text("'active'"),
        index=True,
        comment="Статус датасета (active, error, deleted)",
    )

    download_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Ссылка для скачивания",
    )

    repository_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Ссылка на страницу в репозитории",
    )

    source_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата обновления в источнике",
    )

    search_vector: Mapped[Optional[object]] = mapped_column(
        TSVECTOR,
        nullable=True,
        comment="TSVECTOR для полнотекстового поиска",
    )

    files: Mapped[List["FileORM"]] = relationship(
        "FileORM",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )

    favorites: Mapped[List["FavoriteDatasetORM"]] = relationship(
        "FavoriteDatasetORM",
        back_populates="dataset",
        cascade="all, delete-orphan",
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
        Index(
            "idx_datasets_source_updated_at",
            "source_updated_at",
            postgresql_ops={"source_updated_at": "DESC"},
        ),
        {"comment": "Каталог датасетов из внешних репозиториев"},
    )

    def __repr__(self) -> str:
        return f"<DatasetORM(dataset_id={self.dataset_id}, title={self.title})>"


class FileORM(Base):

    __tablename__ = "files"

    file_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор файла",
    )

    dataset_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("datasets.dataset_id", ondelete="CASCADE"),
        nullable=False,
        comment="Уникальный идентификатор датасета",
    )

    file_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Имя файла",
    )

    file_size_kb: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Размер файла, КБ",
    )

    file_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="SHA-256 хеш файла",
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
        comment="Дата последнего обновления файла",
    )

    dataset: Mapped["DatasetORM"] = relationship(
        "DatasetORM",
        back_populates="files"
    )

    report: Mapped[Optional["ReportORM"]] = relationship(
        "ReportORM",
        back_populates="file",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("dataset_id", "file_name", name="uq_files_dataset_file_name"),
        Index("idx_files_dataset_id", "dataset_id"),
    )


class ReportORM(Base):

    __tablename__ = "reports"

    report_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор отчёта",
    )

    file_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("files.file_id"),
        nullable=False,
        unique=True,
        comment="Файл датасета",
    )

    bucket_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Bucket MinIO с HTML-отчётом",
    )

    object_key: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="Ключ объекта в MinIO",
    )

    input_file_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="SHA-256 data-файла, по которому построен отчёт",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="completed",
        server_default=text("'completed'"),
        comment="Статус отчёта",
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата последнего обновления отчёта",
    )

    processing_started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Дата перехода в processing",
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Текст ошибки последней попытки генерации",
    )

    file: Mapped["FileORM"] = relationship(
        "FileORM",
        back_populates="report",
    )

    user_report_links: Mapped[List["UserReportORM"]] = relationship(
        "UserReportORM",
        back_populates="report",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('completed', 'failed', 'processing', 'deleting')",
            name="chk_report_status",
        ),
        Index("idx_reports_status", "status"),
        Index(
            "idx_reports_updated_at",
            "updated_at",
            postgresql_ops={"updated_at": "DESC"},
        ),
        Index(
            "idx_reports_processing_started_at",
            "processing_started_at",
            postgresql_ops={"processing_started_at": "DESC"},
        ),
        {"comment": "Метаданные EDA-отчётов"},
    )

    def __repr__(self) -> str:
        return f"<ReportORM(report_id={self.report_id}, status={self.status})>"


class FavoriteDatasetORM(Base):

    __tablename__ = "favorite_datasets"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
        comment="Идентификатор пользователя",
    )

    dataset_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("datasets.dataset_id", ondelete="CASCADE"),
        primary_key=True,
        comment="Идентификатор датасета",
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
        {"comment": "Связь пользователей с избранными датасетами"},
    )

    def __repr__(self) -> str:
        return f"<FavoriteDatasetORM(user_id={self.user_id}, dataset_id={self.dataset_id})>"


class UserReportORM(Base):

    __tablename__ = "users_reports"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
        comment="Идентификатор пользователя",
    )

    report_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("reports.report_id", ondelete="CASCADE"),
        primary_key=True,
        comment="Идентификатор отчёта",
    )

    user: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="user_reports"
    )

    report: Mapped["ReportORM"] = relationship(
        "ReportORM",
        back_populates="user_report_links",
    )

    __table_args__ = (
        Index("idx_users_reports_user_id", "user_id"),
        Index("idx_users_reports_report_id", "report_id"),
        {"comment": "Связь пользователей с отчётами в истории"},
    )

    def __repr__(self) -> str:
        return f"<UserReportORM(user_id={self.user_id}, report_id={self.report_id})>"