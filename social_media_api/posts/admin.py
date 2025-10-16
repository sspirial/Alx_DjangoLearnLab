from django.contrib import admin

from .models import Comment, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'author', 'created_at', 'updated_at')
	list_filter = ('created_at', 'updated_at', 'author')
	search_fields = ('title', 'content', 'author__username')
	ordering = ('-created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ('id', 'post', 'author', 'created_at', 'updated_at')
	list_filter = ('created_at', 'updated_at', 'author')
	search_fields = ('content', 'author__username', 'post__title')
	ordering = ('created_at',)
