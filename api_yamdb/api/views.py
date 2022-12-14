from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg, SmallIntegerField
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from iniconfig import ParseError
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title

from .filters import TitleFilter
from .permissions import (IsAdminOrSuperuser, IsAdminUserOrReadOnly,
                          ReviewCommentPermission, UsersPermission)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          UsersSerializer)

User = get_user_model()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = get_object_or_404(
            User, username=serializer.validated_data.get('username'))
        token = default_token_generator.make_token(user=user)
        serializer.save(confirmation_code=token)
        send_mail(subject='Confirmation code', message=token,
                  from_email='YaMBD',
                  recipient_list=(serializer.validated_data.get('email'),))
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def obtain_token(request):
    if 'username' in request.data and 'confirmation_code' in request.data:
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        refresh = RefreshToken.for_user(user)
        if default_token_generator.check_token(user, confirmation_code):
            return Response(status=200, data=str(refresh.access_token))
    return Response(status=400)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def get_permissions(self):
        if self.kwargs.get('username') == 'me':
            permission_classes = (permissions.IsAuthenticated,
                                  UsersPermission,)
        else:
            permission_classes = (IsAdminOrSuperuser, UsersPermission,)
        return [permission() for permission in permission_classes]

    @action(
        methods=['patch'],
        detail=True,
        url_path='me'
    )
    def get_object(self):
        if self.kwargs.get('username') == 'me':
            self.check_object_permissions(self.request, self.request.user)
            return self.request.user
        return super(UsersViewSet, self).get_object()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        if (self.kwargs.get('username') == 'me'
           and request.data.get('role') is not None):
            return Response(data={'role': 'user'},
                            status=status.HTTP_403_FORBIDDEN)
        return self.update(request, *args, **kwargs)

# ?????? ???? ????????????????, ?????? ????????????????!= me
# ?????? ?????????????????? ?????????????? ?? url /api/v1/users/me/ - ?????????????? ????????????????????????
# ?? ?????????????????????????? ???????? (?? ????????) ???????????????? ???? ????????????????!= me
# ?? ???????????? ???????????????? ?????????????????? ?????? ?? ??????????????????, ???????? ???????? ????????????
    def destroy(self, request, *args, **kwargs):
        if self.kwargs.get('username') == 'me':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg("reviews__score",
                                            output_field=SmallIntegerField()))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class CreateRetrieveViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                            mixins.DestroyModelMixin, viewsets.GenericViewSet):

    pass


class CategoriesViewSet(CreateRetrieveViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminUserOrReadOnly,)


class GenresViewSet(CreateRetrieveViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminUserOrReadOnly,)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        ReviewCommentPermission,
        permissions.IsAuthenticatedOrReadOnly
    ]
    pagination_class = PageNumberPagination

    def get_queryset(self, *args, **kwargs):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        if Review.objects.filter(title=title,
                                 author=self.request.user).exists():
            raise ParseError
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (ReviewCommentPermission,)
    pagination_class = PageNumberPagination

    def get_queryset(self, *args, **kwargs):
        review = get_object_or_404(
            Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
