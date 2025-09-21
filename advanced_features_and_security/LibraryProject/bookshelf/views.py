from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.db.models import Q

from .models import Book
from .forms import BookForm, ExampleForm


@login_required
@permission_required('bookshelf.can_view', raise_exception=True)
def book_list(request):
	# Safe search using ORM filters to avoid SQL injection
	q = request.GET.get('q', '').strip()
	qs = Book.objects.all()
	if q:
		qs = qs.filter(Q(title__icontains=q) | Q(author__icontains=q))
	books = qs.order_by('title')
	return render(request, 'bookshelf/book_list.html', {"books": books, "q": q})


@login_required
@permission_required('bookshelf.can_view', raise_exception=True)
def book_detail(request, pk: int):
	book = get_object_or_404(Book, pk=pk)
	return render(request, 'bookshelf/book_detail.html', {"book": book})


@login_required
@permission_required('bookshelf.can_create', raise_exception=True)
def book_create(request):
	if request.method == 'POST':
		form = BookForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('bookshelf:book_list')
	else:
		form = BookForm()
	return render(request, 'bookshelf/book_form.html', {"mode": "create", "form": form})


@login_required
@permission_required('bookshelf.can_edit', raise_exception=True)
def book_edit(request, pk: int):
	book = get_object_or_404(Book, pk=pk)
	if request.method == 'POST':
		form = BookForm(request.POST, instance=book)
		if form.is_valid():
			form.save()
			return redirect('bookshelf:book_detail', pk=book.pk)
	else:
		form = BookForm(instance=book)
	return render(request, 'bookshelf/book_form.html', {"mode": "edit", "form": form, "book": book})


@login_required
@permission_required('bookshelf.can_delete', raise_exception=True)
def book_delete(request, pk: int):
	book = get_object_or_404(Book, pk=pk)
	if request.method == 'POST':
		book.delete()
		return redirect('bookshelf:book_list')
	return render(request, 'bookshelf/book_confirm_delete.html', {"book": book})


@login_required
def example_form(request):
	message = None
	if request.method == 'POST':
		form = ExampleForm(request.POST)
		if form.is_valid():
			# Echo sanitized data back
			message = f"You submitted: {form.cleaned_data['sample']}"
			form = ExampleForm()  # reset
	else:
		form = ExampleForm()
	return render(request, 'bookshelf/form_example.html', {"form": form, "message": message})
