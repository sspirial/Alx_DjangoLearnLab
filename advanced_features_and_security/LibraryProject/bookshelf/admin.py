from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Book, UserProfile, CustomUser

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'publication_year')
	list_filter = ('author', 'publication_year')
	search_fields = ('title', 'author')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "role")
	list_filter = ("role",)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
	fieldsets = (
		(None, {"fields": ("username", "password")}),
		("Personal info", {"fields": ("first_name", "last_name", "email", "date_of_birth", "profile_photo")}),
		("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
		("Important dates", {"fields": ("last_login", "date_joined")}),
	)

	add_fieldsets = (
		(None, {
			"classes": ("wide",),
			"fields": ("username", "email", "password1", "password2", "first_name", "last_name", "date_of_birth", "profile_photo", "is_staff", "is_superuser"),
		}),
	)

	list_display = ("username", "email", "first_name", "last_name", "is_staff", "date_of_birth")
	list_filter = ("is_staff", "is_superuser", "is_active", "groups")
	search_fields = ("username", "first_name", "last_name", "email")
