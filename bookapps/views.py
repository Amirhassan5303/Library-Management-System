import time
import random
import redis
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


# class CircuitBreakerOpen(Exception):
#     pass
#
#
# class Providers:
#     providers_list = ['signal', 'kavehnegar']
#
#
# class CircuitBreaker:
#     def __init__(self, failure_threshold, recovery_timeout):
#         self.failure_threshold = failure_threshold
#         self.recovery_timeout = recovery_timeout
#         self.circuit_open_time = None
#         self.failure_count = 0
#
#     def __call__(self, func):
#         def wrapped_func(*args, **kwargs):
#             if self.circuit_open_time:
#                 elapsed_time = time.time() - self.circuit_open_time
#                 if elapsed_time < self.recovery_timeout:
#                     raise CircuitBreakerOpen("Circuit breaker is open")
#
#                 self.reset_circuit()
#
#             try:
#                 result = func(*args, **kwargs)
#                 self.reset_circuit()
#                 return result
#             except Exception as e:
#                 self.failure_count += 1
#                 if self.failure_count >= self.failure_threshold:
#                     self.open_circuit()
#                     raise CircuitBreakerOpen("Circuit breaker is open")
#                 print(f"Failed to execute function: {str(e)}")
#
#         return wrapped_func
#
#     def open_circuit(self):
#         self.circuit_open_time = time.time()
#
#     def reset_circuit(self):
#         self.failure_count = 0
#         self.circuit_open_time = None
#
#
# class SMSManager:
#     def __init__(self):
#         self.service_providers = Providers.providers_list
#         self.provider_availability = {provider: True for provider in self.service_providers}
#         self.provider_failure_count = {provider: 0 for provider in self.service_providers}
#
#     def login_with_otp(self, member):
#         otp = self.generate_otp()
#         self.send_sms(member, otp)
#
#     def generate_otp(self, length=6):
#         otp = ""
#         for _ in range(length):
#             otp += str(random.randint(0, 9))
#         return otp
#
#     def send_sms(self, member, message):
#         try:
#             self.choose_provider(member, message)
#         except CircuitBreakerOpen:
#             print("Circuit breaker is open. Unable to send SMS.")
#
#     def choose_provider(self, member, message):
#         providers = self.get_available_providers()
#         if not providers:
#             raise CircuitBreakerOpen("No available service providers")
#
#         provider = random.choice(providers)
#         try:
#             self.send_sms_with_provider(provider, member, message)
#             self.mark_provider_as_available(provider)
#             self.reset_failure_count(provider)
#         except Exception as e:
#             print(f"Failed to send SMS through {provider}: {str(e)}")
#             self.mark_provider_as_unavailable(provider)
#             self.increment_failure_count(provider)
#
#     def get_available_providers(self):
#         return [provider for provider, is_available in self.provider_availability.items() if is_available]
#
#     def send_sms_with_provider(self, provider, member, message):
#         if provider == 'kavehnegar':
#             self.send_sms_with_kavehnegar(member, message)
#         elif provider == 'signal':
#             self.send_sms_with_signal(member, message)
#
#     @CircuitBreaker(failure_threshold=3, recovery_timeout=1800)
#     def send_sms_with_kavehnegar(self, member, message):
#         print(f"Sending SMS with KavehNegar to {member}: {message}")
#
#     @CircuitBreaker(failure_threshold=3, recovery_timeout=1800)
#     def send_sms_with_signal(self, member, message):
#         print(f"Sending SMS with Signal to {member}: {message}")
#
#     def mark_provider_as_unavailable(self, provider):
#         self.provider_availability[provider] = False
#
#     def mark_provider_as_available(self, provider):
#         self.provider_availability[provider] = True
#
#     def increment_failure_count(self, provider):
#         self.provider_failure_count[provider] += 1
#
#     def reset_failure_count(self, provider):
#         self.provider_failure_count[provider] = 0
#
#     def get_failure_count(self, provider):
#         return self.provider_failure_count.get(provider, 0)
#
#
# sms_provider = SMSManager()


# class CircuitBreakerOpen(Exception):
#     pass
#
#
# class CircuitBreaker:
#     def __init__(self, failure_threshold, recovery_timeout):
#         self.failure_threshold = failure_threshold
#         self.recovery_timeout = recovery_timeout
#         self.circuit_open_time = None
#         self.failure_count = 0
#
#     def __call__(self, func):
#         def wrapped_func(*args, **kwargs):
#             if self.circuit_open_time:
#                 elapsed_time = time.time() - self.circuit_open_time
#                 if elapsed_time < self.recovery_timeout:
#                     raise CircuitBreakerOpen("Circuit breaker is open")
#
#                 self.reset_circuit()
#
#             try:
#                 result = func(*args, **kwargs)
#                 self.reset_circuit()
#                 return result
#             except Exception as e:
#                 self.failure_count += 1
#                 if self.failure_count >= self.failure_threshold:
#                     self.open_circuit()
#                     raise CircuitBreakerOpen("Circuit breaker is open")
#                 print(f"Failed to execute function: {str(e)}")
#
#         return wrapped_func
#
#     def open_circuit(self):
#         self.circuit_open_time = time.time()
#
#     def reset_circuit(self):
#         self.failure_count = 0
#         self.circuit_open_time = None

redis_client = redis.from_url("redis://172.17.0.2:6379")
redis_client.set(f"amirhassan", 3)


@api_view(["POST"])
def login_member(request):
    try:
        if request.method == "POST":
            username = request.data.get("username")
            otp = login_with_otp(username)
            print(otp)
            return HttpResponse("Message has sent successfully")
    except Exception as e:
        return HttpResponse("Error occurred")


def login_with_otp(username):
    otp = generate_otp()
    return otp


def generate_otp(length=6):
    otp = ""
    for _ in range(length):
        otp += str(random.randint(0, 9))
    return otp


# def send_sms(username, otp):
#     provider = choose_provider()
#     if provider == 'signal':
#         return send_sms_with_signal(username, otp)
#     elif provider == 'kavehnegar':
#         return send_sms_with_kavehnegar(username, otp)
#
#
# def choose_provider():
#     providers = ['signal', 'kavehnegar']
#     provider = random.choice(providers)
#     return provider
#
#
# def send_sms_with_kavehnegar(username, otp):
#     return f'The otp number for {username} is: {otp}, kavehnegar'
#
#
# def send_sms_with_signal(username, otp):
#     return f'The otp number for {username} is: {otp}, signal'



















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