from django.urls import path
from . import views

urlpatterns = [
    path("book-detail/<int:pk>/", views.book_detail, name="book-detail"),
    path("update-book/<int:pk>/", views.update_book, name="update-book"),
    path("delete-book/<int:pk>/", views.delete_book, name="delete-book"),
    path("add-book/", views.add_book, name="add_book"),
]