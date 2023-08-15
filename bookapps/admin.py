from django.contrib import admin
from .models import Genre, Book, Member, Borrow

admin.site.register(Genre)
admin.site.register(Book)
admin.site.register(Member)
admin.site.register(Borrow)
