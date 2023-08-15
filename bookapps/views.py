from django.http import JsonResponse
from .models import Member, Book
from .serializers import BookSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view



@api_view(["GET"])
def book_detail(request, pk):
    try:
        book = Book.objects.get(id=pk)
    except Book.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    book_serializer = BookSerializer(book)
    return Response(book_serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_book(request, pk):
    try:
        book = Book.objects.get(id=pk)
    except Book.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    book_serializer = BookSerializer(book, data=request.data)
    if book_serializer.is_valid():
        book_serializer.save()
        return Response(book_serializer.data)
    return Response(book_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def delete_book(request, pk):
    try:
        book = Book.objects.get(id=pk)
    except Book.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    book.delete()
    return Response(status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def add_book(request):
    book_serializer = BookSerializer(data=request.data)
    if book_serializer.is_valid():
        book_serializer.save()
        return Response(status=status.HTTP_201_CREATED)