from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    UserSerializer
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Accepts POST requests with username, email, password, and optional bio/profile_picture.
    Returns user data with authentication token upon successful registration.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': UserSerializer(user).data,
            'token': Token.objects.get(user=user).key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    API endpoint for user login.
    Accepts POST requests with username and password.
    Returns user data with authentication token upon successful login.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Get or create token for user
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating user profile.
    GET: Retrieve current user's profile
    PUT/PATCH: Update current user's profile
    Requires authentication.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Return the current authenticated user.
        """
        return self.request.user


class UserLogoutView(APIView):
    """
    API endpoint for user logout.
    Deletes the user's authentication token.
    Requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Delete the user's token
            request.user.auth_token.delete()
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class FollowUserView(APIView):
    """Allow authenticated users to follow other users."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id: int):
        target_user = get_object_or_404(User, pk=user_id)

        if target_user == request.user:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.following.filter(pk=target_user.pk).exists():
            return Response(
                {
                    "detail": "Already following this user.",
                    "user": UserSerializer(target_user, context={"request": request}).data,
                },
                status=status.HTTP_200_OK,
            )

        request.user.following.add(target_user)
        return Response(
            {
                "detail": f"You are now following {target_user.username}.",
                "user": UserSerializer(target_user, context={"request": request}).data,
            },
            status=status.HTTP_201_CREATED,
        )


class UnfollowUserView(APIView):
    """Allow authenticated users to unfollow other users."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id: int):
        target_user = get_object_or_404(User, pk=user_id)

        if target_user == request.user:
            return Response(
                {"detail": "You cannot unfollow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.following.filter(pk=target_user.pk).exists():
            return Response(
                {
                    "detail": "You are not following this user.",
                    "user": UserSerializer(target_user, context={"request": request}).data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.following.remove(target_user)
        return Response(
            {
                "detail": f"You have unfollowed {target_user.username}.",
                "user": UserSerializer(target_user, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )

