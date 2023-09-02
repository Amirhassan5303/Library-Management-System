from rest_framework import serializers

from .models import Book, Borrow


class RequestOTPSerializer(serializers.Serializer):
    receiver = serializers.CharField(max_length=50, allow_null=False)
    channel = serializers.ChoiceField(allow_null=False, choices=Member.MEMBERSHIP_CHOICES)


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6, allow_null=False)


class PurchaseMembershipSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255, allow_null=False)


class ReserveBookSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()


class BorrowedBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ['book', 'borrowed_date', 'return_date']


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = "__all__"