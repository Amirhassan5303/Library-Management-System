from rest_framework import serializers
from .models import Book


# class MemberSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Member
#         fields = ["first_name", "last_name", "code"]

class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = "__all__"