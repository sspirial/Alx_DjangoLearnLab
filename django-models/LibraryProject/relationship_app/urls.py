from django.urls import path

from .views import list_books, LibraryDetailView

app_name = "relationship_app"

urlpatterns = [
    path("books/", list_books, name="list_books"),
    path("libraries/<int:pk>/", LibraryDetailView.as_view(), name="library_detail"),
]
