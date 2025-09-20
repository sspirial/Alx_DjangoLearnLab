from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Library
from .models import Book
from .models import UserProfile


def list_books(request):
	"""Function-based view that lists all books with their authors."""
	books = Book.objects.all()
	return render(request, "relationship_app/list_books.html", {"books": books})


class LibraryDetailView(DetailView):
	"""Class-based view to display a specific Library and its books."""
	model = Library
	template_name = "relationship_app/library_detail.html"
	context_object_name = "library"

	def get_queryset(self):
		# Prefetch books and their authors to minimize queries in the template
		return (
			super()
			.get_queryset()
			.prefetch_related("books__author")
		)


def register(request):
	"""Handle user registration using Django's built-in UserCreationForm.

	- GET: display the registration form
	- POST: validate and create the user, log them in, then redirect
	"""
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			# Log the user in after successful registration
			login(request, user)
			# Redirect to books list or home page
			return redirect("relationship_app:list_books")
	else:
		form = UserCreationForm()

	return render(request, "relationship_app/register.html", {"form": form})


# ----- Role helpers -----
def is_admin(user):
	try:
		return user.is_authenticated and user.userprofile.role == UserProfile.ROLE_ADMIN
	except UserProfile.DoesNotExist:
		return False


def is_librarian(user):
	try:
		return user.is_authenticated and user.userprofile.role == UserProfile.ROLE_LIBRARIAN
	except UserProfile.DoesNotExist:
		return False


def is_member(user):
	try:
		return user.is_authenticated and user.userprofile.role == UserProfile.ROLE_MEMBER
	except UserProfile.DoesNotExist:
		return False


# ----- Role-restricted views -----
@login_required
@user_passes_test(is_admin)
def admin_view(request):
	return render(request, "relationship_app/admin_view.html")


@login_required
@user_passes_test(is_librarian)
def librarian_view(request):
	return render(request, "relationship_app/librarian_view.html")


@login_required
@user_passes_test(is_member)
def member_view(request):
	return render(request, "relationship_app/member_view.html")
