from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from .views import list_books, LibraryDetailView, admin_view, librarian_view, member_view, add_book, edit_book, delete_book

app_name = "relationship_app"

urlpatterns = [
    path("books/", list_books, name="list_books"),
    path("books/add/", add_book, name="add_book"),
    path("books/<int:pk>/edit/", edit_book, name="edit_book"),
    path("books/<int:pk>/delete/", delete_book, name="delete_book"),
    path("libraries/<int:pk>/", LibraryDetailView.as_view(), name="library_detail"),
    # Authentication routes
    path("login/", LoginView.as_view(template_name="relationship_app/login.html",redirect_authenticated_user=True), name="login"),
    path("logout/", LogoutView.as_view(template_name="relationship_app/logout.html"), name="logout"),
    path("register/", views.register, name="register"),
    # Role-based routes
    path("admin-area/", admin_view, name="admin_view"),
    path("librarian-area/", librarian_view, name="librarian_view"),
    path("member-area/", member_view, name="member_view"),
]
