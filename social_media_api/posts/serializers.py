"""Serializers for the posts application."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import Comment, Like, Post

User = get_user_model()


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for representing likes on a post."""

    user = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'post', 'user', 'created_at')
        read_only_fields = ('id', 'post', 'user', 'created_at')


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for creating and representing comments."""

    author = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = (
            'id',
            'post',
            'author',
            'content',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')

    def validate_content(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Comment content cannot be empty.")
        return value


class PostSerializer(serializers.ModelSerializer):
    """Serializer for post CRUD operations."""

    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = (
            'id',
            'author',
            'title',
            'content',
            'created_at',
            'updated_at',
            'comments_count',
            'comments',
            'likes_count',
            'is_liked',
        )
        read_only_fields = (
            'id',
            'author',
            'created_at',
            'updated_at',
            'comments_count',
            'comments',
            'likes_count',
            'is_liked',
        )

    def validate_title(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Post title cannot be empty.")
        return value

    def validate_content(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Post content cannot be empty.")
        return value

    def get_comments_count(self, obj: Post) -> int:
        return obj.comments.count()

    def get_likes_count(self, obj: Post) -> int:
        return obj.likes.count()

    def get_is_liked(self, obj: Post) -> bool:
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.likes.filter(user=request.user).exists()
