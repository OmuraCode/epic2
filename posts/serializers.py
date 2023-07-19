from random import randint
from rest_framework import serializers
from category.models import Category
from comment.serializers import CommentSerializer
from posts.models import Post, Likes, Favorite
from rating.models import Mark
from purchase.models import Purchase
from django.db.models import Sum

# class PostImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PostImages
#         fields = '__all__'


class PostListSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Post
        fields = (
            'id', 'owner', 'owner_email', 'title_of_game', 'price', 'date_of_issue', 'link_on_game',
            'video')


class PostSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source='owner.email')
    owner = serializers.ReadOnlyField(source='owner.id')
    # images = PostImageSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = '__all__'
    #
    # def create(self, validated_data):
    #     request = self.context.get('request')
    #     images = request.FILES.getlist('images')
    #     post = Post.objects.create(**validated_data)
    #     for image in images:
    #         PostImages.objects.create(image=image, post=post)
    #     return post

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        # recommendations
        category = instance.category
        similar_posts = Post.objects.filter(category=category).exclude(id=instance.id)[:5]
        liked_posts = Post.objects.filter(likes__user=instance.owner, likes__is_liked=True).exclude(id=instance.id)[:5]
        recommendations = list(similar_posts) + list(liked_posts)

        repr['recommendations'] = PostListSerializer(recommendations, many=True).data
        repr['comments_count'] = instance.comments.count()
        repr['comments'] = CommentSerializer(instance.comments.all(), many=True).data
        repr['likes_count'] = instance.likes.count()
        repr['marks_count'] = instance.marks.count()
        total_marks = instance.marks.aggregate(total=Sum('mark'))['total']
        if total_marks is not None:
            repr['rating'] = total_marks / repr['marks_count']
        else:
            repr['rating'] = None  # or set a default value
        repr['purchase_count'] = instance.purchase.count()
        user = self.context['request'].user
        if user.is_authenticated:
            repr['is_liked'] = user.likes.filter(post=instance).exists()
            repr['is_favorite'] = user.favorites.filter(post=instance).exists()
        return repr


class LikeUserSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Likes
        fields = '__all__'


class FavoritesUserSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Favorite
        fields = '__all__'


class FavoriteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["author"] = instance.author.email
        repr["category"] = instance.category.title
        return repr
