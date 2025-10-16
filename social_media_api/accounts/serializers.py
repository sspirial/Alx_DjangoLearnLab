from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles password validation and user creation with token generation.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password_confirm',
            'bio', 'profile_picture', 'token'
        ]
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        """
        Create a new user with encrypted password and generate auth token.
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        Token.objects.get_or_create(user=user)
        return user

    def to_representation(self, instance):
        """
        Include token in the response.
        """
        data = super().to_representation(instance)
        token, _ = Token.objects.get_or_create(user=instance)
        data['token'] = token.key
        return data


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates credentials and returns user data with token.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, 
        write_only=True,
        style={'input_type': 'password'}
    )
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        """
        Validate user credentials and retrieve auth token.
        """
        username = attrs.get("username")
        password = attrs.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        token, _ = Token.objects.get_or_create(user=user)
        attrs["user"] = user
        attrs["token"] = token.key
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile management.
    Allows users to view and update their profile information.
    """
    followers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "bio", "profile_picture", "followers")
        read_only_fields = ("id", "username", "email", "followers")


class UserSerializer(serializers.ModelSerializer):
    """Lightweight serializer for embedding user details in responses."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'bio', 'profile_picture')
        read_only_fields = ('id', 'username', 'email', 'bio', 'profile_picture')
