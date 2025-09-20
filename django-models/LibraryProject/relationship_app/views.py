from django.shortcuts import render
from django.views.generic.detail import DetailView

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
