from django.contrib.auth import get_user_model
from django.urls.conf import path
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.utils import swagger_auto_schema

from account import serializers
from account.send_mail import send_confirmation_email, send_confirmation_seller_email
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth.models import User

from posts.serializers import LikeUserSerializer, FavoritesUserSerializer
from posts.views import StandartResultPagination
from .serializers import ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated
from posts.models import Likes
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from config.task import send_confirmation_email_task, send_confirmation_seller_email_task


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# from account.send_mail import


User = get_user_model()


class UserViewSet(ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    agination_class = StandartResultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('username', 'email')
    filterset_fields = ('is_seller', 'is_buyer')
    serializer_class = serializers.UserSerializer
    permission_classes = (AllowAny,)

    @method_decorator(cache_page(5 * 60), name='list')
    @method_decorator(cache_page(5 * 60), name='retrieve')
    @action(['GET'], detail=True)
    def likes(self, request, pk):
        user = request.user
        likes = user.likes.all()
        serializers = LikeUserSerializer(likes, many=True)
        return Response(serializers.data, status=201)

    @method_decorator(cache_page(5 * 60), name='list')
    @method_decorator(cache_page(5 * 60), name='retrieve')
    @action(['GET'], detail=True)
    def favorites(self, request, pk):
        user = request.user
        favorites = user.favorites.all()
        serializers = FavoritesUserSerializer(favorites, many=True)
        return Response(serializers.data, status=201)

    @swagger_auto_schema(request_body=serializers.RegisterSerializer)
    @action(['POST'], detail=False)
    def register(self, request, *args, **kwargs):
        serializer = serializers.RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            try:
                send_confirmation_email_task.delay(user.email, user.activation_code)
            except Exception as e:
                return Response({'msg': 'Registered, but troubles with email!',
                                 'data': 'serializer.data'}, status=201)
            return Response(serializer.data, status=201)

    @action(['GET'], detail=False, url_path='activate/(?P<uuid>[0-9A-Fa-f-]+)')
    def activate(self, request, uuid):
        try:
            user = User.objects.get(activation_code=uuid)
        except User.DoesNotExist:
            return Response({'msg': 'Invalid link or link expired!'}, status=400)
        user.is_active = True
        user.is_buyer = True
        user.activation_code = ''
        user.save()
        return Response({'msg': 'Successfully activated!'}, status=200)

    @action(['POST'], detail=False)
    def register_seller(self, request, *args, **kwargs):
        serializer = serializers.RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            try:
                send_confirmation_seller_email_task.delay(user.email, user.activation_code)
            except Exception as e:
                return Response({'msg': 'Registered, but troubles with email!',
                                 'data': 'serializer.data'}, status=201)
            return Response(serializer.data, status=201)

    @action(['GET'], detail=False, url_path='activate_seller/(?P<uuid>[0-9A-Fa-f-]+)')
    def activate_seller(self, request, uuid):
        try:
            user = User.objects.get(activation_code=uuid)
        except User.DoesNotExist:
            return Response({'msg': 'Invalid link or link expired!'}, status=400)
        user.is_active = True
        user.is_seller = True
        user.activation_code = ''
        user.save()
        return Response({'msg': 'Successfully activated!'}, status=200)


class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)


class RefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)
