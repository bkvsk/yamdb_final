from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db.models import Avg
from django_filters import rest_framework
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitlesFilter
from .models import Categories, Genres, Review, Titles
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsPostOrIsAuthorOrNotUserOrReadOnly,
)
from .serializers import (
    AuthConfirmationSerializer,
    AuthStartSerializer,
    CategoriesSerializer,
    CommentSerializer,
    GenresSerializer,
    ReviewSerializer,
    TitlesSerializer,
    UserSerializer,
)

User = get_user_model()


class AuthEmailView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = AuthStartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data.get('email')
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={'is_active': False}
        )
        mail_subject = 'Activate your account on YaMDB'
        message = f'Сonfirmation code: {user.confirmation_code}'
        email = EmailMessage(mail_subject, message, to=[email])
        email.send()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthTokenView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = AuthConfirmationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data.get('email')
        user = get_object_or_404(User, email=email)
        user.is_active = True
        user.save()
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    queryset = User.objects.order_by('id')
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    @action(methods=['GET', 'PATCH'], detail=False,
            permission_classes=[IsAuthenticated])
    def me(self, request):
        self.kwargs['username'] = request.user.username
        if request.method == 'GET':
            return self.retrieve(request)
        return self.partial_update(request)


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all().order_by('name')
    serializer_class = CategoriesSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    http_method_names = ['get', 'post', 'delete']

    def retrieve(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed('GET')


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all().order_by('name')
    serializer_class = GenresSerializer
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    http_method_names = ['get', 'post', 'delete']

    def retrieve(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed('GET')


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all().order_by('name')
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TitlesSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = TitlesFilter

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.rating = instance.reviews.all().aggregate(
            Avg('score'))['score__avg']
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsPostOrIsAuthorOrNotUserOrReadOnly)
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title = get_object_or_404(Titles, pk=self.kwargs.get('title_id'))
        return title.reviews.all().order_by('id')

    def perform_create(self, serializer):
        title = get_object_or_404(Titles, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsPostOrIsAuthorOrNotUserOrReadOnly)
    serializer_class = CommentSerializer

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all().order_by('id')

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
