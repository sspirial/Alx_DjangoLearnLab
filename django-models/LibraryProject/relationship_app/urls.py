from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
import views
from .views import list_books, LibraryDetailView

app_name = "relationship_app"

urlpatterns = [
    path("books/", list_books, name="list_books"),
    path("libraries/<int:pk>/", LibraryDetailView.as_view(), name="library_detail"),
    # Authentication routes
    path("login/", LoginView.as_view(template_name="relationship_app/login.html",redirect_authenticated_user=True), name="login"),
    path("logout/", LogoutView.as_view(template_name="relationship_app/logout.html"), name="logout"),
    path("register/", views.register, name="register"),
]
