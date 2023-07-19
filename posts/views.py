from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, response, status
from rest_framework.decorators import action

from .models import Post, Likes, Favorite
from . import serializers
from .permissions import IsAuthor, IsAuthorOrAdmin, IsSeller, IsBuyer
from rest_framework.response import Response

from .serializers import PostSerializer

from rating.serializers import MarkSerializer
from purchase.models import Purchase
from purchase.serializers import PurchaseSerializer
from rating.models import Mark
from comment.models import Comment
from comment.serializers import CommentSerializer


# class PostDeleteView(APIView):
#     def delete(self, request, slug):
#         my_model = get_object_or_404(Post, slug=slug)
#         my_model.delete()
#         return Response("Object deleted successfully.")

class StandartResultPagination(PageNumberPagination):
    page_size = 15


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().order_by('title_of_game')
    pagination_class = StandartResultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('title_of_game', 'title_of_publisher')
    filterset_fields = ('owner', 'category')

    @swagger_auto_schema(request_body=serializers.PostSerializer)
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PostListSerializer
        return serializers.PostSerializer

    @method_decorator(cache_page(5 * 60), name='list')
    @method_decorator(cache_page(5 * 60), name='retrieve')
    @action(methods=['POST', 'GET'], detail=True)
    def rating(self, request, pk):
        post = self.get_object()
        if request.method == 'GET':
            marks = post.marks.all()
            serializer = MarkSerializer(marks, many=True).data
            return response.Response(serializer, status=200)
        elif post.marks.filter(owner=request.user).exists():
            return response.Response('You already marked this post!',
                                     status=400)
        elif request.method == 'POST':
            Mark.objects.create(owner=request.user, mark=request.data['mark'], post=post)
            return response.Response({'msg': 'Thank you for your mark'}, status=201)

    @action(['DELETE'], detail=True)
    def rating_delete(self, request, pk=None):
        post = self.get_object()  # Product.objects.get(id=pk)
        user = request.user
        if not post.marks.filter(owner=user).exists():
            return response.Response('You didn\'t marked this post!',
                                     status=400)
        mark = post.marks.get(owner=user)
        mark.delete()
        return response.Response('Successfully deleted', status=204)

    @method_decorator(cache_page(5 * 60), name='list')
    @method_decorator(cache_page(5 * 60), name='retrieve')
    @action(['POST', 'GET'], detail=True)
    def purchase(self, request, pk):
        post = self.get_object()
        if request.method == 'GET':
            purchase = post.purchase.all()
            serializer = PurchaseSerializer(purchase, many=True).data
            return response.Response(serializer, status=200)
        elif post.purchase.filter(owner=request.user).exists():
            return response.Response('You already purchased this game!',
                                     status=400)
        elif request.method == 'POST':
            Purchase.objects.create(owner=request.user, post=post)
            return response.Response({'msg': 'Thank you for your purchase'}, status=201)

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthorOrAdmin(), ]
        elif self.action in ('update', 'partial_update'):
            return [IsAuthor(), ]
        elif self.action == 'create':
            return [IsSeller(), ]
        elif self.action == 'list':
            return [permissions.AllowAny(), ]
        return [IsBuyer(), ]

    @action(detail=True, methods=['GET'])
    def delete_like(self, request, pk):
        post = self.get_object()
        user = request.user
        like_obj, created = Likes.objects.get_or_create(post=post, user=user)

        like_obj.is_liked = not like_obj.is_liked
        like_obj.delete()
        return Response('like deleted')

    @action(detail=True, methods=['GET'])
    def toggle_like(self, request, pk):
        post = self.get_object()
        user = request.user
        like_obj, created = Likes.objects.get_or_create(post=post, user=user)

        like_obj.is_liked = not like_obj.is_liked
        like_obj.save()
        return Response('like toggled')

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('likes_from', openapi.IN_QUERY, 'filter products by amount of likes', True,
                          type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["GET"])
    def likes(self, request, pk=None):
        from django.db.models import Count
        q = request.query_params.get("likes_from")  # request.query_params = request.GET
        queryset = self.get_queryset()
        queryset = queryset.annotate(Count('likes')).filter(likes__count__gte=q)

        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # @swagger_auto_schema(manual_parameters=[
    #     openapi.Parameter('likes_from', openapi.IN_QUERY, 'filter products by amount of likes', True,
    #                       type=openapi.TYPE_INTEGER)])
    # @action(detail=False, methods=["GET"])
    # def likes(self, request):
    #     from django.db.models import Count
    #     q = request.query_params.get("likes_from")
    #     queryset = self.get_queryset().annotate(likes_count=Count('likes')).filter(likes_count__gte=q)
    #
    #     serializer = PostSerializer(queryset, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=True, methods=['GET'])
    def delete_favorite(self, request, pk):
        post = self.get_object()
        user = request.user
        fav, created = Favorite.objects.get_or_create(post=post, user=user)

        fav.favorite = not fav.favorite
        fav.delete()
        return Response('favourite deleted')

    @action(detail=True, methods=['GET'])
    def toggle_favorite(self, request, pk):
        post = self.get_object()
        user = request.user
        fav, created = Favorite.objects.get_or_create(post=post, user=user)

        fav.favorite = not fav.favorite
        fav.save()
        return Response('favorite toggled')

    # @action(['GET', 'POST'], detail=True)
    # def reviews(self, request, pk):
    #     product = self.get_object()
    #     if request.method == 'GET':
    #         reviews = product.reviews.all()
    #         serializer = MarkActionSerializer(reviews, many=True).data
    #         return response.Response(serializer, status=200)
    #     else:
    #         if product.reviews.filter(user=request.user).exists():
    #             return response.Response('You already reviewed this product!',
    #                                      status=400)
    #         data = request.data  # rating text
    #         serializer = MarkActionSerializer(data=data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save(user=request.user, product=product)
    #         return response.Response(serializer.data, status=201)
    #
    # # api/v1/product/id/
    # @action(['DELETE'], detail=True)
    # def review_delete(self, request, pk):
    #     product = self.get_object()  # Product.objects.get(id=pk)
    #     user = request.user
    #     if not product.reviews.filter(user=user).exists():
    #         return response.Response('You didn\'t reviewed this product!',
    #                                  status=400)
    #     review = product.reviews.get(user=user)
    #     review.delete()
    #     return response.Response('Successfully deleted', status=204)
    @action(detail=True, methods=['POST', 'GET'])
    def comment(self, request, pk):
        post = self.get_object()
        user = request.user
        if request.method == 'POST':
            body = request.data.get('body')
            if body is not None:
                Comment.objects.create(owner=request.user, post=post, body=body)
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Missing or invalid "body" field in request data.'},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'GET':
            comments = post.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

    @action(['DELETE'], detail=True)
    def comment_delete(self, request, pk=None):
        post = self.get_object()  # Product.objects.get(id=pk)
        user = request.user
        if not post.comments.filter(owner=user).exists():
            return response.Response('You didn\'t commented this post!',
                                     status=400)
        comment = post.comments.get(owner=user)
        comment.delete()
        return response.Response('Comment successfully deleted', status=204)
