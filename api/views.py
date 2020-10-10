from django.db.models import Avg, F
from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, status, permissions
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,

)

from .models import Title, Review, Comment, Category, Genre, CustomUser
from .permissions import (
    IsAuthorOrReadOnly,
    IsModerator,
    IsStaff,
    IsStaffOrReadOnly,
)
from .serializers import (
    ReviewSerializer,
    CommentSerializer,
    CategorySerializer,
    GenreSerializer,
    TitlesSerializer,
)
from .serializers import (
    UserRegistrationSerializer,
    MyAuthTokenSerializer,
    CustomUserSerializer,
)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly | IsModerator | IsStaff,
    ]

    def get_title(self):
        title = get_object_or_404(Title, id=self.kwargs["title_id"])
        return title

    def get_queryset(self):
        queryset = Review.objects.filter(title=self.get_title()).all()
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def perform_update(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly | IsModerator | IsStaff,
    ]

    def get_review(self):
        post = get_object_or_404(
            Review,
            id=self.kwargs["review_id"],
            title__id=self.kwargs["title_id"],
        )
        return post

    def get_queryset(self):
        queryset = Comment.objects.filter(review=self.get_review()).all()
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def perform_update(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class CategoriesViewSet(
    CreateModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"
    filter_backends = [SearchFilter]
    search_fields = [
        "name",
    ]
    permission_classes = [IsStaffOrReadOnly]


class GenresViewSet(
    CreateModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = "slug"
    filter_backends = [SearchFilter]
    search_fields = [
        "name",
    ]
    permission_classes = [IsStaffOrReadOnly]


class TitlesViewSet(ModelViewSet):
    serializer_class = TitlesSerializer
    queryset = Title.objects.all()
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            rating=Avg(F('reviews__score')))
        category = self.request.query_params.get('category', None)
        genre = self.request.query_params.get('genre', None)
        name = self.request.query_params.get('name', None)
        year = self.request.query_params.get('year', None)
        if category is not None:
            queryset = queryset.filter(category__slug=category)
        if genre is not None:
            queryset = queryset.filter(genre__slug=genre)
        if name is not None:
            queryset = queryset.filter(name__iregex=r'.*{}.*'.format(name))
        if year is not None:
            queryset = queryset.filter(year__year=year)
        return queryset.order_by('id')


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    queryset = CustomUser.objects.all()


class UserListCreateView(generics.ListCreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = CustomUser.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["$username"]


class UserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = CustomUser.objects.all()

    def get_object(self):
        return self.queryset.get(username=self.kwargs["username"])

    def partial_update(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(
            self.get_object(), data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()

    def get_object(self):
        return self.queryset.get(email=self.request.user)


class ObtainAuthToken(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = MyAuthTokenSerializer
    queryset = CustomUser.objects.all()
