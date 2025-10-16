"""Utility helpers for producing notifications."""

from __future__ import annotations

from typing import Any, Optional

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from .models import Notification


@transaction.atomic

def create_notification(
	recipient,
	actor,
	verb: str,
	target: Optional[Any] = None,
	*,
	metadata: Optional[dict] = None,
	skip_self: bool = True,
) -> Optional[Notification]:
	"""Create a notification record.

	Parameters
	----------
	recipient: User receiving the notification.
	actor: User who triggered the notification.
	verb: Short description of the performed action (e.g. "liked your post").
	target: Optional object the action was performed on.
	metadata: Optional JSON-serialisable dictionary for extra context.
	skip_self: When ``True``, do not create notifications where ``recipient`` equals ``actor``.
	"""

	if skip_self and recipient == actor:
		return None

	content_type = None
	object_id = None
	if target is not None:
		content_type = ContentType.objects.get_for_model(target, for_concrete_model=False)
		object_id = target.pk

	return Notification.objects.create(
		recipient=recipient,
		actor=actor,
		verb=verb,
		content_type=content_type,
		object_id=object_id,
		metadata=metadata,
	)
