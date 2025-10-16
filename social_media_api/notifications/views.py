"""API endpoints for notifications."""

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
	"""Return notifications for the authenticated user."""

	serializer_class = NotificationSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		return (
			Notification.objects.for_user(self.request.user)
			.order_by('is_read', '-timestamp')
			.select_related('recipient', 'actor', 'content_type')
		)

	def list(self, request, *args, **kwargs):
		unread_count = Notification.objects.for_user(request.user).unread().count()
		response = super().list(request, *args, **kwargs)
		response.data['unread_count'] = unread_count
		return response


class NotificationMarkReadView(generics.GenericAPIView):
	"""Mark a single notification as read."""

	permission_classes = [permissions.IsAuthenticated]
	serializer_class = NotificationSerializer

	def get_queryset(self):
		return Notification.objects.for_user(self.request.user)

	def post(self, request, pk: int):
		notification = get_object_or_404(self.get_queryset(), pk=pk)
		notification.mark_read()
		serializer = self.get_serializer(notification)
		return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationMarkAllReadView(APIView):
	"""Mark all notifications as read for the authenticated user."""

	permission_classes = [permissions.IsAuthenticated]

	def post(self, request):
		updated = Notification.objects.for_user(request.user).unread().update(is_read=True)
		return Response(
			{'detail': f'Marked {updated} notifications as read.'},
			status=status.HTTP_200_OK,
		)
