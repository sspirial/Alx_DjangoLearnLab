from django.shortcuts import render
from rest_framework import generics
from .models import Book
from .serializers import BookSerializer

# Create your views here.

class BookList(generics.ListAPIView):
    """
    API view to retrieve a list of all books.
    Uses BookSerializer to convert Book model instances to JSON.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
