from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
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

