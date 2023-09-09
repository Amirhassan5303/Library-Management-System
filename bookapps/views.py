import time
import random
from django.conf import settings
import redis
from django.contrib.auth import authenticate

from .models import Member, Book, Borrow
from .serializers import BookSerializer
from rest_framework.response import Response
from rest_framework import status, generics, filters
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse
from django.views import View


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


class CircuitBreaker:
    def __init__(self, failure_threshold, recovery_timeout):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.circuit_open_time = None
        self.failure_count = 0
        self.redis_client = redis.Redis(host='localhost', port=6379)

    def __call__(self, func):
        def wrapped_func(*args, **kwargs):
            if self.circuit_open_time:
                elapsed_time = time.time() - self.circuit_open_time
                if elapsed_time < self.recovery_timeout:
                    raise CircuitBreakerOpen("Circuit breaker is open")

                self.reset_circuit()

            try:
                result = func(*args, **kwargs)
                self.reset_circuit()
                return result
            except Exception as e:
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    self.open_circuit()
                    raise CircuitBreakerOpen("Circuit breaker is open")
                print(f"Failed to execute function: {str(e)}")

        return wrapped_func

    def open_circuit(self):
        self.circuit_open_time = time.time()
        self.redis_client.set("circuit_breaker:state", "open")
        self.redis_client.expire("circuit_breaker:state", self.recovery_timeout)

    def reset_circuit(self):
        self.failure_count = 0
        self.circuit_open_time = None
        self.redis_client.delete("circuit_breaker:state")


class CircuitBreakerOpen(Exception):
    pass


class Providers:
    providers_list = ['signal', 'kavehnegar']


class SMSManager:
    def __init__(self):
        self.service_providers = Providers.providers_list
        self.redis_client = redis.Redis(host=settings.CACHES['default']['LOCATION'])

    def choose_provider(self):
        provider = self.get_available_provider()
        if provider is None:
            raise Exception("No available service provider")
        try:
            self.send_sms_with_available_provider(provider)
        except Exception as e:
            print(f"Failed to send SMS through {provider}: {str(e)}")
            self.mark_provider_as_unavailable(provider)

    def get_available_provider(self):
        available_providers = []
        if len(available_providers) == 0:
            provider = random.choice(self.service_providers)
        else:
            provider = random.choice(available_providers)
        try:
            if self.is_provider_available(provider):
                return provider
        except Exception as e:
            print(f"Failed to send SMS through {provider}: {str(e)}")
            self.mark_provider_as_unavailable(provider)

    def is_provider_available(self, provider):
        if self.redis_client.get(f"provider_status:{provider}") != b"unavailable":
            return provider
        else:
            self.mark_provider_as_unavailable(provider)

    def mark_provider_as_unavailable(self, provider):
        self.redis_client.set(f"provider_status:{provider}", "unavailable")
        self.choose_provider()

    @CircuitBreaker(failure_threshold=3, recovery_timeout=1800)
    def send_sms_with_available_provider(self, provider, phone_number, message):
        print(f"Sending SMS through {provider}: {message} to {phone_number}")


@api_view(["POST"])
def send_sms(request):
    if request.method == "POST":
        sms_provider = SMSManager()
        provider = sms_provider.choose_provider()


@api_view(["POST"])
def login_member(request):
    if request.method == "POST":
        username = request.data.get("username")
        password = request.data.get("password")
        otp = request.data.get("otp")

        user = authenticate(request, username=username, password=password, otp=otp)
        return HttpResponse("Authentication was successful")


def generate_otp(length=6):
    otp = ""
    for _ in range(length):
        otp += str(random.randint(0, 9))
    return otp


class SMSManagerView(View):
    def post(self, request):
        sms_manager = SMSManager()
        phone_number = request.POST.get('phone_number')
        message = request.POST.get('message')
        otp = request.POST.get('otp')

        if phone_number and message and otp:
            if self.verify_otp(phone_number, otp):
                try:
                    sms_manager.choose_provider()
                    return HttpResponse("SMS sent successfully")
                except CircuitBreakerOpen:
                    return HttpResponse("Circuit breaker is open. Please try again later.")
            else:
                return HttpResponse("Invalid OTP")
        else:
            return HttpResponse("Invalid request")

    def verify_otp(self, phone_number, otp):
        return True



# class OTPThrottle:
#     MAX_REQUESTS_PER_MINUTE = 5
#     MAX_REQUESTS_PER_HOUR = 10
#
#     def __init__(self):
#         self.requests_per_minute = []
#         self.requests_per_hour = []
#
#     def should_allow_request(self):
#         current_time = datetime.timezone.now()
#
#         self.requests_per_hour = [req for req in self.requests_per_hour if req >= current_time - timezone.timedelta(hours=1)]
#
#         self.requests_per_minute = [req for req in self.requests_per_minute if req >= current_time - timezone.timedelta(minutes=1)]
#
#         if len(self.requests_per_minute) < self.MAX_REQUESTS_PER_MINUTE and len(self.requests_per_hour) < self.MAX_REQUESTS_PER_HOUR:
#             self.requests_per_minute.append(current_time)
#             self.requests_per_hour.append(current_time)
#             return True
#
#         return False
#
#
# @api_view(['POST'])
# def reserve_book(request):
#     serializer = ReserveBookSerializer(data=request.data)
#     if serializer.is_valid():
#         isbn = serializer.validated_data['isbn']
#         book = Book.objects.get(pk=isbn)
#         member = request.user
#
#         if book.is_available:
#             if not Borrow.objects.filter(book=book, returned=False).exists():
#                 if member.has_valid_membership():
#                     if member.membership_type == 'premium':
#                         max_borrow_duration = 14
#                     else:
#                         max_borrow_duration = 7
#
#                     return_date = timezone.now() + timezone.timedelta(days=max_borrow_duration)
#                     payment = Borrow.objects.filter(
#                         member=member,
#                         returned=True,
#                         return_date__gte=timezone.now() - timezone.timedelta(days=60)
#                     ).count()
#
#                     if payment > 3:
#                         payment = 0.7 * payment * 1000
#
#                     if payment > 300000:
#                         payment = 0
#
#                     borrowed_book = Borrow(
#                         member=member,
#                         book=book,
#                         return_date=return_date,
#                         payment=payment
#                     )
#                     borrowed_book.save()
#
#                     book.is_available = False
#                     book.save()
#
#
# @api_view(['GET'])
# def list_borrowed_books(request):
#     member = request.user
#     borrowed_books = Borrow.objects.filter(member=member)
#     serializer = BorrowedBookSerializer(borrowed_books, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)