from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=2, choices=(("1", "Inactive"), ("2", "Active")), default=2)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class Book(models.Model):
    title = models.CharField(max_length=200)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    published_date = models.DateTimeField()
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"


class Member(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    gender = models.CharField(max_length=2, choices=(("1", "Male"), ("2", "Female")), default=1)
    email = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    crated_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Borrow(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField()
    return_date = models.DateField()
    status = models.CharField(max_length=2, choices=(("1", "pending"), ("2", "returned")), default=1)
    crated_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.member.first_name} {self.member.last_name} - {self.return_date}"


