from rest_framework import serializers

from .models import Book, Borrow, Member


# class VerifyOTPSerializer(serializers.Serializer):
#     otp = serializers.CharField(max_length=6, allow_null=False)
#
#
# class PurchaseMembershipSerializer(serializers.Serializer):
#     token = serializers.CharField(max_length=255, allow_null=False)
#
#
# class ReserveBookSerializer(serializers.Serializer):
#     book_id = serializers.IntegerField()
#
#
# class BorrowedBookSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Borrow
#         fields = ['book', 'borrowed_date', 'return_date']


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = "__all__"
