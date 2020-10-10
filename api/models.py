import base64
import random
import string

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email address", unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    role = models.CharField(max_length=30, blank=True)
    confirmation_code = models.CharField(max_length=30, blank=True)
    username = models.CharField(max_length=30, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200, )
    year = models.DateField(null=True, blank=True, )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, blank=True,
                                 related_name='titles')
    genre = models.ManyToManyField(Genre, blank=True, related_name='titles')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    SCORE_CHOICES = [(i, i) for i in range(1, 11)]

    text = models.TextField()
    score = models.PositiveSmallIntegerField(
        choices=SCORE_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    pub_date = models.DateTimeField(
        "Дата публикации", auto_now_add=True, db_index=True
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="reviews"
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name="reviews"
    )

    class Meta:
        unique_together = ("author", "title")

    def __str__(self):
        return self.text


class Comment(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(
        "Дата публикации", auto_now_add=True, db_index=True
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comments"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )

    def __str__(self):
        return self.text


def encode(text):
    enc_bytes = text.encode("ascii")
    base64_bytes = base64.b64encode(enc_bytes)
    base64_enc = base64_bytes.decode("ascii")
    return base64_enc


@receiver(pre_save, sender=CustomUser)
def create_code(sender, instance, **kwargs):
    confirmation_code = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(8)
    )
    instance.confirmation_code = encode(confirmation_code)
    return instance


@receiver(pre_save, sender=CustomUser)
def define_role(sender, instance, **kwargs):
    if instance.role == "admin":
        instance.is_staff = 1
        instance.role = "admin"
    elif instance.role == "superuser":
        instance.is_superuser = 1
        instance.is_staff = 1
        instance.role = "superuser"
    elif instance.role == "user":
        instance.is_superuser = 0
        instance.is_staff = 0
    elif instance.role == "moderator":
        instance.is_superuser = 0
        instance.is_staff = 0
    return instance
