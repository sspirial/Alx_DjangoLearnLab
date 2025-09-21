from django.db import models

class Author(models.Model):
	name = models.CharField(max_length=255)

	def __str__(self):
		return self.name


class Book(models.Model):
	title = models.CharField(max_length=255)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')

	def __str__(self):
		return self.title

	class Meta:
		permissions = (
			("can_add_book", "Can add book"),
			("can_change_book", "Can change book"),
			("can_delete_book", "Can delete book"),
		)


class Library(models.Model):
	name = models.CharField(max_length=255)
	books = models.ManyToManyField(Book, related_name='libraries', blank=True)

	def __str__(self):
		return self.name


class Librarian(models.Model):
	name = models.CharField(max_length=255)
	library = models.OneToOneField(Library, on_delete=models.CASCADE, related_name='librarian')

	def __str__(self):
		return self.name