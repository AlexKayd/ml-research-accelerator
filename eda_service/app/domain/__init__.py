from app.domain.entities import Report, FileInfo, DatasetInfo, DatasetChangeEvent
from app.domain.interfaces import IReportRepository, IFilesRepository, IReportStorage, IUserServiceClient
from app.domain.exceptions import (
    DomainException,
    DatabaseError,
    InvalidReportError,
    InvalidEventError,
    ReportNotFoundError,
    ReportDeletingError,
    ReportGenerationError,
    DatasetArchiveDownloadError,
    FileNotFoundInArchiveError,
    StorageError,
    UserServiceUnavailableError,
    UserServiceReportAttachFailedError,
)
from app.domain.value_objects import ReportStatus, EDAEventType

__all__ = [
    'Report',
    'FileInfo',
    'DatasetInfo',
    'DatasetChangeEvent',

    'IReportRepository',
    'IFilesRepository',
    'IReportStorage',
    'IUserServiceClient',

    'DomainException',
    'DatabaseError',
    'InvalidReportError',
    'InvalidEventError',
    'ReportNotFoundError',
    'ReportDeletingError',
    'ReportGenerationError',
    'DatasetArchiveDownloadError',
    'FileNotFoundInArchiveError',
    'StorageError',
    'UserServiceUnavailableError',
    'UserServiceReportAttachFailedError',

    'ReportStatus',
    'EDAEventType',
]