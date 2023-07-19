from random import randint

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField

from category.models import Category
from ckeditor.fields import RichTextField

User = get_user_model()


class Post(models.Model):
    owner = models.ForeignKey(User, on_delete=models.RESTRICT,
                              related_name='posts', default=None)
    title_of_game = models.CharField(max_length=150, unique=True)
    title_of_publisher = models.CharField(max_length=50)
    name_of_developer = models.CharField(max_length=50)
    date_of_issue = models.DateField()
    short_description = RichTextField(default='', max_length=250)
    preview = models.URLField()
    category = models.ForeignKey(Category, related_name='posts',
                                 on_delete=models.RESTRICT)
    full_description = RichTextField(default='', max_length=10000)
    image_for_full = models.URLField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    link_on_game = models.URLField()
    link_on_discord = models.URLField(blank=True)
    link_on_instagram = models.URLField(blank=True)
    link_on_twitter = models.URLField(blank=True)
    link_on_facebook = models.URLField(blank=True)
    video = models.URLField(blank=True)
    image_one = models.URLField(default='', blank=True)
    image_two = models.URLField(default='', blank=True)
    image_three = models.URLField(default='', blank=True)
    image_four = models.URLField(default='', blank=True)
    image_five = models.URLField(default='', blank=True)


    def __str__(self):
        return self.title_of_game


# class PostImages(models.Model):
#     title = models.CharField(max_length=100, blank=True)
#     image = models.URLField(default=None)
#     post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
#
#     def generate_name(self):
#         return 'image' + str(self.id) + str(randint(100000, 999999))
#
#     def save(self, *args, **kwargs):
#         return super(PostImages, self).save(*args, **kwargs)


class Likes(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='likes')
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE, related_name='likes')

    is_liked = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.post} -> {self.user} -> {self.is_liked}'

    class Meta:
        verbose_name = 'like'
        verbose_name_plural = 'likes'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='favorites')
    favorite = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.post} -> {self.user} -> {self.favorite}'
