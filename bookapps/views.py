from .models import Member, Book
from .serializers import BookSerializer
from rest_framework.response import Response
from rest_framework import status, generics, filters
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filter
from django.http import HttpResponse, JsonResponse




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
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def add_book(request):
    book_serializer = BookSerializer(data=request.data)
    if book_serializer.is_valid():
        book_serializer.save()
        return Response(status=status.HTTP_201_CREATED)


# class BookFilter(filter.FilterSet):
#     title = filter.CharFilter(field_name="title", lookup_expr="iexact")


class CustomBookPagination(PageNumberPagination):
    page_size = 3


class BookListAPIView(generics.ListAPIView):

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["genre"]
    search_fields = ["title", "description"]
    ordering_fields = ["price"]
    pagination_class = CustomBookPagination





