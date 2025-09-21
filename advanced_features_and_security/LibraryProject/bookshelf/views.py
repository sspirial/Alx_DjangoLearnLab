from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden
from django.urls import reverse

from .models import Book


@login_required
@permission_required('bookshelf.can_view', raise_exception=True)
def book_list(request):
	books = Book.objects.all().order_by('title')
	return render(request, 'bookshelf/book_list.html', {"books": books})


@login_required
@permission_required('bookshelf.can_view', raise_exception=True)
def book_detail(request, pk: int):
	book = get_object_or_404(Book, pk=pk)
	return render(request, 'bookshelf/book_detail.html', {"book": book})


@login_required
@permission_required('bookshelf.can_create', raise_exception=True)
def book_create(request):
	if request.method == 'POST':
		title = request.POST.get('title')
		author = request.POST.get('author')
		year = request.POST.get('publication_year')
		if title and author and year:
			Book.objects.create(title=title, author=author, publication_year=int(year))
			return redirect('bookshelf:book_list')
	return render(request, 'bookshelf/book_form.html', {"mode": "create"})


@login_required
@permission_required('bookshelf.can_edit', raise_exception=True)
def book_edit(request, pk: int):
	book = get_object_or_404(Book, pk=pk)
	if request.method == 'POST':
		title = request.POST.get('title')
		author = request.POST.get('author')
		year = request.POST.get('publication_year')
		if title and author and year:
			book.title = title
			book.author = author
			book.publication_year = int(year)
			book.save()
			return redirect('bookshelf:book_detail', pk=book.pk)
	return render(request, 'bookshelf/book_form.html', {"mode": "edit", "book": book})


@login_required
@permission_required('bookshelf.can_delete', raise_exception=True)
def book_delete(request, pk: int):
	book = get_object_or_404(Book, pk=pk)
	if request.method == 'POST':
		book.delete()
		return redirect('bookshelf:book_list')
	return render(request, 'bookshelf/book_confirm_delete.html', {"book": book})
