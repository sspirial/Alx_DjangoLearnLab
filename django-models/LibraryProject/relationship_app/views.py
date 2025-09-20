from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Library
from .models import Book


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
