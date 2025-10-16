"""Serializers for the notifications app."""

from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Represent notifications in API responses."""

    recipient = UserSerializer(read_only=True)
    actor = UserSerializer(read_only=True)
    target_type = serializers.SerializerMethodField()
    target_id = serializers.SerializerMethodField()
    target_repr = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            'id',
            'recipient',
            'actor',
            'verb',
            'metadata',
            'timestamp',
            'is_read',
            'target_type',
            'target_id',
            'target_repr',
        )
        read_only_fields = fields

    def get_target_type(self, obj: Notification):
        if obj.content_type:
            return obj.content_type.model
        return None

    def get_target_id(self, obj: Notification):
        return obj.object_id

    def get_target_repr(self, obj: Notification):
        if obj.target is not None:
            return str(obj.target)
        return None
