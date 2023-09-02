import random
import datetime

from django.utils import timezone

from .models import Member, Book, Borrow
from .serializers import BookSerializer, BorrowedBookSerializer, ReserveBookSerializer
from rest_framework.response import Response
from rest_framework import status, generics, filters, serializers
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination






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


class KavenegarSMSService:
    def send_sms(self, receiver, message):
        print(f"Sending SMS to {receiver} via Kavenegar: {message}")


class SignalSMSService:
    def send_sms(self, receiver, message):
        print(f"Sending SMS to {receiver} via Signal: {message}")


class SMSServiceCircuitBreaker:
    def __init__(self):
        self.kavenegar_service = KavenegarSMSService()
        self.signal_service = SignalSMSService()
        self.current_service = self.kavenegar_service
        self.is_current_service_available = True

    def send_sms(self, receiver, message):
        if self.is_current_service_available:
            try:
                self.current_service.send_sms(receiver, message)
            except Exception:
                self.is_current_service_available = False
                self.current_service = self.signal_service
                self.send_sms(receiver, message)
        else:
            self.current_service.send_sms(receiver, message)


class OTPThrottle:
    MAX_REQUESTS_PER_MINUTE = 5
    MAX_REQUESTS_PER_HOUR = 10

    def __init__(self):
        self.requests_per_minute = []
        self.requests_per_hour = []

    def should_allow_request(self):
        current_time = datetime.timezone.now()

        self.requests_per_hour = [req for req in self.requests_per_hour if req >= current_time - timezone.timedelta(hours=1)]

        self.requests_per_minute = [req for req in self.requests_per_minute if req >= current_time - timezone.timedelta(minutes=1)]

        if len(self.requests_per_minute) < self.MAX_REQUESTS_PER_MINUTE and len(self.requests_per_hour) < self.MAX_REQUESTS_PER_HOUR:
            self.requests_per_minute.append(current_time)
            self.requests_per_hour.append(current_time)
            return True

        return False


@api_view(['POST'])
def reserve_book(request):
    serializer = ReserveBookSerializer(data=request.data)
    if serializer.is_valid():
        book_id = serializer.validated_data['book_id']
        book = Book.objects.get(pk=book_id)
        member = request.user

        if book.is_available:
            if not Borrow.objects.filter(book=book, returned=False).exists():
                if member.has_valid_membership():
                    if member.membership_type == 'premium':
                        max_borrow_duration = 14
                    else:
                        max_borrow_duration = 7

                    return_date = timezone.now() + timezone.timedelta(days=max_borrow_duration)
                    payment = Borrow.objects.filter(
                        member=member,
                        returned=True,
                        return_date__gte=timezone.now() - timezone.timedelta(days=60)
                    ).count()

                    if payment > 3:
                        payment = 0.7 * payment * 1000

                    if payment > 300000:
                        payment = 0

                    borrowed_book = Borrow(
                        member=member,
                        book=book,
                        return_date=return_date,
                        payment=payment
                    )
                    borrowed_book.save()

                    book.is_available = False
                    book.save()


@api_view(['GET'])
def list_borrowed_books(request):
    member = request.user
    borrowed_books = Borrow.objects.filter(member=member)
    serializer = BorrowedBookSerializer(borrowed_books, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)