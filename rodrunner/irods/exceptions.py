"""
Custom exceptions for iRODS operations.
"""


class iRODSClientError(Exception):
    """Base exception for iRODS client errors."""
    pass


class ConnectionError(iRODSClientError):
    """Exception raised when a connection to iRODS cannot be established."""
    pass


class AuthenticationError(iRODSClientError):
    """Exception raised when authentication to iRODS fails."""
    pass


class ObjectNotFoundError(iRODSClientError):
    """Exception raised when an iRODS object is not found."""
    pass


class PermissionError(iRODSClientError):
    """Exception raised when a permission error occurs."""
    pass


class MetadataError(iRODSClientError):
    """Exception raised when a metadata operation fails."""
    pass


class QueryError(iRODSClientError):
    """Exception raised when a query operation fails."""
    pass


class UploadError(iRODSClientError):
    """Exception raised when an upload operation fails."""
    pass


class DownloadError(iRODSClientError):
    """Exception raised when a download operation fails."""
    pass
