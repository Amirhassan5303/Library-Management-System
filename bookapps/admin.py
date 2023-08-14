from django.contrib import admin
from .models import Category, Book, Student, Borrow

admin.site.register(Category)
admin.site.register(Book)
admin.site.register(Student)
admin.site.register(Borrow)
