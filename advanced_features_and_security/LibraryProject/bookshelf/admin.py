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
	fieldsets = UserAdmin.fieldsets + (
		("Additional Info", {"fields": ("date_of_birth", "profile_photo")}),
	)
	add_fieldsets = UserAdmin.add_fieldsets
	list_display = ("username", "email", "first_name", "last_name", "is_staff", "date_of_birth")
