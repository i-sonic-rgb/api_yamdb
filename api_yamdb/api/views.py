from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .permissions import (IsAdminOrReadOnly,
                          IsAuthorOrReadOnly, IsSuperUserOrAdmin)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewObjectSerializer,
                          ReviewSerializer, SignUpSerializer,
                          TitleSerializerReadOnly, TitleSerializerWritable,
                          TokenSerializer, UserSerializer)


class ReviewViewSet(viewsets.ModelViewSet):
    '''CRUD for Review model.'''
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('text', )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Review.objects.filter(title_id=self.kwargs.get('title_id'))

    def get_serializer_class(self):
        if self.action in ('list', 'create'):
            return ReviewSerializer
        return ReviewObjectSerializer

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    '''CRUD for Comment model.'''
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    serializer_class = CommentSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('text', )

    def get_review(self, review_id):
        return get_object_or_404(Review, id=review_id)

    def get_queryset(self):
        return self.get_review(self.kwargs.get('review_id')).comments.all()

    def perform_create(self, serializer):
        serializer.save(
            review=self.get_review(self.kwargs.get('review_id')),
            author=self.request.user
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    pagination_class = LimitOffsetPagination
    permission_classes = (IsSuperUserOrAdmin,)

    @action(
        detail=False,
        methods=['PATCH', 'GET'],
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'GET':
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_200_OK
            )

        serializer = UserSerializer(
            instance=user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def token(request):
    serializer = TokenSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.data['username']
    user = get_object_or_404(User, username=username)
    confirmation_code = serializer.data['confirmation_code']

    if not default_token_generator.check_token(user, confirmation_code):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    token = RefreshToken.for_user(user)
    return Response(
        {'token': str(token.access_token)}, status=status.HTTP_200_OK
    )


class SignupView(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']]
        )
        email.send()

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        user, foo = User.objects.get_or_create(username=username, email=email)
        confirmation_code = default_token_generator.make_token(user)
        email_body = (
            f'Здравствуйте, {username}.'
            f'\nКод подтверждения Yamdb: {confirmation_code}'
        )
        data = {
            'email_body': email_body,
            'to_email': email,
            'email_subject': 'Код подтверждения Yamdb'
        }
        self.send_email(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommonViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.CreateModelMixin):
    '''Common CRUD for Genre and Category models.'''
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class CategoryViewSet(CommonViewSet):
    '''CRUD for Category model.'''
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CommonViewSet):
    '''CRUD for Genre model.'''
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    '''CRUD for Title model.'''
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializerReadOnly
        return TitleSerializerWritable
