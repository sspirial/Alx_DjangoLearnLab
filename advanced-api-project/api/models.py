from django.db import models


class Author(models.Model):
    """
    Author model representing book authors in the system.
    
    This model stores information about authors who can have multiple books.
    It establishes a one-to-many relationship with the Book model through
    a foreign key relationship, where one author can have many books.
    
    Fields:
        name: CharField storing the author's full name (max 100 characters)
    
    The model provides a clean string representation using the author's name
    and includes proper metadata for database optimization.
    """
    name = models.CharField(
        max_length=100, 
        help_text="Full name of the author"
    )
    
    class Meta:
        """
        Meta class for the Author model.
        Defines model-level options including ordering and verbose names.
        """
        ordering = ['name']  # Order authors alphabetically by name
        verbose_name = "Author"
        verbose_name_plural = "Authors"
    
    def __str__(self):
        """
        String representation of the Author model.
        Returns the author's name for easy identification in admin and debugging.
        """
        return self.name


class Book(models.Model):
    """
    Book model representing individual books in the system.
    
    This model stores detailed information about books and maintains a foreign key
    relationship with the Author model. Each book belongs to exactly one author,
    but an author can have multiple books (one-to-many relationship).
    
    Fields:
        title: CharField storing the book's title (max 200 characters)
        publication_year: IntegerField storing the year the book was published
        author: ForeignKey linking to the Author model with CASCADE deletion
    
    The foreign key relationship ensures referential integrity - if an author
    is deleted, all their books are also deleted (CASCADE behavior).
    """
    title = models.CharField(
        max_length=200, 
        help_text="Title of the book"
    )
    publication_year = models.IntegerField(
        help_text="Year the book was published"
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books',
        help_text="Author who wrote this book"
    )
    
    class Meta:
        """
        Meta class for the Book model.
        Defines model-level options including ordering and verbose names.
        """
        ordering = ['-publication_year', 'title']  # Order by publication year (newest first), then title
        verbose_name = "Book"
        verbose_name_plural = "Books"
        
        # Ensure no duplicate books by the same author with same title and year
        unique_together = ['title', 'author', 'publication_year']
    
    def __str__(self):
        """
        String representation of the Book model.
        Returns a formatted string showing title, author, and publication year.
        """
        return f"{self.title} by {self.author.name} ({self.publication_year})"
