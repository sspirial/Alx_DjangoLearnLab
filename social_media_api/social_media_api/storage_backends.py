"""Custom storage backends for AWS S3."""

import importlib
import os
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from storages.backends.s3boto3 import S3Boto3Storage as _BaseS3Boto3Storage
else:  # pragma: no cover - executed at runtime
    try:
        _BaseS3Boto3Storage: Type = getattr(importlib.import_module('storages.backends.s3boto3'), 'S3Boto3Storage')
    except ModuleNotFoundError:
        _BaseS3Boto3Storage = type('S3Boto3Storage', (object,), {})


class StaticStorage(_BaseS3Boto3Storage):
    """Store collected static files under the configured static location."""

    location = os.getenv('AWS_S3_STATIC_LOCATION', 'static')
    default_acl = 'public-read'


class MediaStorage(_BaseS3Boto3Storage):
    """Store user uploaded media files under the configured media location."""

    location = os.getenv('AWS_S3_MEDIA_LOCATION', 'media')
    file_overwrite = os.getenv('AWS_S3_FILE_OVERWRITE', 'False').strip().lower() in {'true', '1', 'yes', 'on'}
    default_acl = None
