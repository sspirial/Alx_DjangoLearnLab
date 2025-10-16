from rest_framework import serializers
from django.contrib.auth import get_user_model
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
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 
                  'bio', 'profile_picture', 'token']
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate(self, data):
        """
        Validate that passwords match.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def validate_email(self, value):
        """
        Validate that email is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        """
        Create a new user with encrypted password and generate auth token.
        """
        # Remove password_confirm from validated_data
        validated_data.pop('password_confirm')
        
        # Extract password
        password = validated_data.pop('password')
        
        # Create user instance
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Generate token for the user
        Token.objects.create(user=user)
        
        return user

    def to_representation(self, instance):
        """
        Include token in the response.
        """
        representation = super().to_representation(instance)
        token = Token.objects.get(user=instance)
        representation['token'] = token.key
        return representation


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


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile management.
    Allows users to view and update their profile information.
    """
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'profile_picture', 
                  'followers_count', 'following_count', 'date_joined']
        read_only_fields = ['id', 'username', 'date_joined']

    def get_followers_count(self, obj):
        """
        Return the number of followers.
        """
        return obj.followers.count()

    def get_following_count(self, obj):
        """
        Return the number of users this user is following.
        """
        return obj.following.count()


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for general user data display.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'profile_picture']
        read_only_fields = ['id']
