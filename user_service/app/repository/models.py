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
        index=True,
        comment="Уникальное имя пользователя для входа",
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Хешированный пароль (bcrypt)",
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
        comment="Источник данных (kaggle, uci, huggingface)",
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
        comment="Дата обновления в источнике (NULL, если источник не отдал дату)",
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
    """Файл внутри датасета (sql/ddl.sql)."""

    __tablename__ = "files"

    file_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    dataset_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("datasets.dataset_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_kb: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    file_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_data: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    file_updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

    dataset: Mapped["DatasetORM"] = relationship("DatasetORM", back_populates="files")
    reports: Mapped[List["ReportORM"]] = relationship(
        "ReportORM",
        back_populates="file",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("dataset_id", "file_name", name="uq_files_dataset_file_name"),
        Index("idx_files_dataset_id", "dataset_id"),
    )


class ReportORM(Base):
    """Отчёт: ссылка на объект в хранилище (bucket/object_key) и файл датасета."""

    __tablename__ = "reports"

    report_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор отчёта",
    )

    file_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("files.file_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Файл датасета, для которого построен отчёт",
    )

    bucket_name: Mapped[str] = mapped_column(String(255), nullable=False)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="completed",
        index=True,
        comment="Статус отчёта в хранилище",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        comment="Дата и время последнего обновления",
    )

    file: Mapped["FileORM"] = relationship("FileORM", back_populates="reports")
    user_report_links: Mapped[List["UserReportORM"]] = relationship(
        "UserReportORM",
        back_populates="report",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('completed', 'failed')",
            name="chk_report_status",
        ),
        Index("idx_reports_file_id", "file_id"),
        Index("idx_reports_status", "status"),
        Index(
            "idx_reports_updated_at",
            "updated_at",
            postgresql_ops={"updated_at": "DESC"},
        ),
        {"comment": "Метаданные EDA-отчётов (объект в MinIO/S3)"},
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

    user: Mapped["UserORM"] = relationship("UserORM", back_populates="favorites")
    dataset: Mapped["DatasetORM"] = relationship("DatasetORM", back_populates="favorites")

    __table_args__ = (
        Index("idx_favorites_user_id", "user_id"),
        Index("idx_favorites_dataset_id", "dataset_id"),
        {"comment": "Связь пользователей с избранными датасетами"},
    )

    def __repr__(self) -> str:
        return f"<FavoriteDatasetORM(user_id={self.user_id}, dataset_id={self.dataset_id})>"


class UserReportORM(Base):
    """
    История: пользователь сохранил отчёт в историю.
    Схема users_reports(user_id, report_id) из sql/ddl.sql.
    """

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

    user: Mapped["UserORM"] = relationship("UserORM", back_populates="user_reports")
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
