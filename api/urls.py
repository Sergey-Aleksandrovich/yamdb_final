from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    ReviewViewSet,
    CommentViewSet,
    CategoriesViewSet,
    GenresViewSet,
    TitlesViewSet,
)
from .views import (
    RegisterView,
    ObtainAuthToken,
    UserDetailView,
    UserListCreateView,
    UserView,
)


router = DefaultRouter()
router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="reviews"
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)
router.register(r"categories", CategoriesViewSet, basename="categories")
router.register(r"genres", GenresViewSet, basename="genres")
router.register(r"titles", TitlesViewSet, basename="titles")

urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += [
    path("auth/email/", RegisterView.as_view()),
    path("auth/token/", ObtainAuthToken.as_view(), name="token_obtain_pair"),
]

urlpatterns += [
    path("users/me/", UserDetailView.as_view()),
    re_path("^users/$", UserListCreateView.as_view()),
    path("users/<str:username>/", UserView.as_view()),
]
