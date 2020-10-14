import base64

from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Review, Comment, Category, Genre, Title, CustomUser


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username", read_only=True
    )

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date")
        model = Review

    def create(self, validated_data):
        try:
            result = super().create(validated_data)
        except IntegrityError as e:
            raise serializers.ValidationError(e)
        return result


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username", read_only=True
    )

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "slug")
        lookup_field = "slug"


class GenreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Genre
        fields = ("name", "slug")
        lookup_field = "slug"


class TitlesSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(read_only=True)
    year = serializers.DateField(format="%Y",
                                 input_formats=["%Y", ],
                                 required=False)
    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all())

    genre = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Genre.objects.all(),
        many=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['category'] = CategorySerializer(instance=instance.category).data
        genre_list = []
        for genre in ret['genre']:
            genre_instance = Genre.objects.get(slug=genre)
            genre_list.append(GenreSerializer(instance=genre_instance).data)
        ret['genre'] = genre_list
        if ret['year']!=None:
            ret['year'] = int(ret['year'])
        return ret


User = get_user_model()


def encode(text):
    enc_bytes = text.encode("ascii")
    base64_bytes = base64.b64encode(enc_bytes)
    base64_enc = base64_bytes.decode("ascii")
    return base64_enc


def decode(text):
    base64_bytes = text.encode("ascii")
    text_bytes = base64.b64decode(base64_bytes)
    decoded_text = text_bytes.decode("ascii")
    return decoded_text


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email",)

    def create(self, validated_data):
        email = validated_data["email"]
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "Email addresses must be unique."}
            )
        user = CustomUser.objects.create(
            username=email, email=email, is_active=False, role="user"
        )

        request = self.context.get("request")
        current_site = get_current_site(request)
        mail_subject = "Activate your account."
        message = render_to_string(
            "activate.html",
            {
                "email": user.email,
                "domain": current_site.domain,
                "confirmation_code": decode(user.confirmation_code),
            },
        )
        email = EmailMessage(mail_subject, message, to=[user.email])
        email.send()
        return self.data["email"]


def required(value):
    if value is None:
        raise serializers.ValidationError("This field is required")


class CustomUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[required])

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )

    def validate(self, data):
        if "username" in data:
            user = CustomUser.objects.filter(username=data["username"]).first()
            if user:
                raise serializers.ValidationError(f"Username should be unique")
        return data


class MyAuthTokenSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = CustomUser
        fields = ("email", "confirmation_code")

    def validate(self, data):
        email = self.initial_data["email"]
        confirmation_code = data["confirmation_code"]
        user = CustomUser.objects.filter(email=email).first()

        if user:
            if encode(confirmation_code) == user.confirmation_code:
                user.is_active = True
                user.save()
                refresh = TokenObtainPairSerializer.get_token(user)
                del data["email"]
                del data["confirmation_code"]
                data["token"] = str(refresh.access_token)
                return data
        else:
            raise serializers.ValidationError(
                {"token": "User already has token."}
            )
        return data
