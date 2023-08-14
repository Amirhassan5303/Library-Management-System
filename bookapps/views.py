from django.shortcuts import render
from .models import Category


def category(request):
    categories = Category.objects.all()
    context = {"categories": categories}
    return render(request, "bookapps/cat.html", context)


