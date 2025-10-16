from django.contrib.auth import authenticate, get_user_model
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.services import create_notification

from .models import CustomUser
from .serializers import (
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """API endpoint for user registration."""

    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "user": UserSerializer(user, context={"request": request}).data,
                "token": Token.objects.get(user=user).key,
                "message": "User registered successfully",
            },
            status=status.HTTP_201_CREATED,
        )


class UserLoginView(APIView):
    """API endpoint for user login."""

    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        user = authenticate(username=username, password=password)

        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        token, _created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "user": UserSerializer(user, context={"request": request}).data,
                "token": token.key,
                "message": "Login successful",
            },
            status=status.HTTP_200_OK,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View and update the authenticated user's profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserLogoutView(APIView):
    """API endpoint for user logout."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as exc:  # pragma: no cover - defensive catch
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class FollowUserView(generics.GenericAPIView):
    """Allow authenticated users to follow other users."""

    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()
    lookup_url_kwarg = "user_id"
    serializer_class = UserSerializer

    def post(self, request, user_id: int):
        target_user = self.get_object()

        if target_user == request.user:
            return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.following.filter(pk=target_user.pk).exists():
            return Response(
                {
                    "detail": "Already following this user.",
                    "user": self.get_serializer(target_user, context={"request": request}).data,
                },
                status=status.HTTP_200_OK,
            )

        request.user.following.add(target_user)
        create_notification(
            recipient=target_user,
            actor=request.user,
            verb='started following you',
            metadata={'follower_id': request.user.pk},
        )
        return Response(
            {
                "detail": f"You are now following {target_user.username}.",
                "user": self.get_serializer(target_user, context={"request": request}).data,
            },
            status=status.HTTP_201_CREATED,
        )


class UnfollowUserView(generics.GenericAPIView):
    """Allow authenticated users to unfollow other users."""

    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()
    lookup_url_kwarg = "user_id"
    serializer_class = UserSerializer

    def post(self, request, user_id: int):
        target_user = self.get_object()

        if target_user == request.user:
            return Response({"detail": "You cannot unfollow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.following.filter(pk=target_user.pk).exists():
            return Response(
                {
                    "detail": "You are not following this user.",
                    "user": self.get_serializer(target_user, context={"request": request}).data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.following.remove(target_user)
        return Response(
            {
                "detail": f"You have unfollowed {target_user.username}.",
                "user": self.get_serializer(target_user, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )

