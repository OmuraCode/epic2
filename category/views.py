from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from category import serializers
from category.models import Category
from posts.models import Post
from posts.serializers import PostSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from posts.serializers import PostListSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def get_permissions(self):
        if self.action in ('retrieve', 'list'):
            return [permissions.AllowAny(), ]
        else:
            return [permissions.IsAdminUser(), ]

    def retrieve(self, request, *args, **kwargs):
        print(kwargs.items())
        category_slug = kwargs.get('pk')  # Получение slug из URL-параметров
        print(category_slug)
        category = PostSerializer(Post.objects.filter(category__name=category_slug)).data  # Получение категории по slug
        posts = Post.objects.filter(category=category)  # Получение всех постов, связанных с категорией
        post_serializer = PostSerializer(posts, many=True)  # Сериализация постов
        return Response(post_serializer.data)

